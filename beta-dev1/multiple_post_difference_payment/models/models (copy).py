# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    multiple_post_line = fields.Integer('multiple post line',default=0)

    writeoff_account_id_1 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_1 = fields.Monetary(string='Payment Amount', required=True)
    writeoff_account_id_2 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_2 = fields.Monetary(string='Payment Amount', required=True)
    writeoff_account_id_3 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_3 = fields.Monetary(string='Payment Amount', required=True)
    writeoff_account_id_4 = fields.Many2one('account.account', string="Difference Account",
                                            domain=[('deprecated', '=', False)], copy=False)
    amount_4 = fields.Monetary(string='Payment Amount', required=True)

    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id', 'amount_1', 'amount_2', 'amount_3', 'amount_4',)
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            self.payment_difference = self.amount - self._compute_total_invoices_amount()
        else:
            if self.amount_1 and not self.amount_2 and not self.amount_3 and not self.amount_4:
                self.payment_difference = self._compute_total_invoices_amount() - (self.amount + self.amount_1)
            elif self.amount_1 and self.amount_2 and not self.amount_3 and not self.amount_4:
                self.payment_difference = self._compute_total_invoices_amount() - (self.amount + self.amount_1 + self.amount_2)
            elif self.amount_1 and self.amount_2 and self.amount_3 and not self.amount_4:
                self.payment_difference = self._compute_total_invoices_amount() - (self.amount + self.amount_1 + self.amount_2 + self.amount_3)
            elif self.amount_1 and self.amount_2 and self.amount_3 and self.amount_4:
                self.payment_difference = self._compute_total_invoices_amount() - (self.amount + self.amount_1 + self.amount_2 + self.amount_3 + self.amount_4)
            else:
                self.payment_difference = self._compute_total_invoices_amount() - self.amount

        # if self.payment_difference < 0:
        #     raise ValidationError(_("The total amount that will be posted should equal to the payment difference."))

    def post(self):
        if self.payment_difference_handling == 'reconcile':
            # 1
            self.writeoff_account_id = self.writeoff_account_id_1
            self.amount = self.amount_1
            if self.multiple_post_line == 0:
                res = super(AccountPayment, self).post()
                return res
            else:
                amount = self.amount_1 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = self._create_payment_entry_with_account(amount,self.writeoff_account_id)
            # 2
            self.writeoff_account_id = self.writeoff_account_id_2
            self.amount = self.amount_2
            if self.multiple_post_line == 1:
                res = super(AccountPayment, self).post()
                return res
            else:
                amount = self.amount_2 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = self._create_payment_entry_with_account(amount,self.writeoff_account_id)
            # 3
            self.writeoff_account_id = self.writeoff_account_id_3
            self.amount = self.amount_3
            if self.multiple_post_line == 2:
                res = super(AccountPayment, self).post()
                return res
            else:
                amount = self.amount_3 * (self.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = self._create_payment_entry_with_account(amount, self.writeoff_account_id)

            # 4
            self.writeoff_account_id = self.writeoff_account_id_4
            self.amount = self.amount_4
            if self.multiple_post_line == 3:
                res = super(AccountPayment, self).post()
                return res
            self.multiple_post_line = 0
        else:
            res = super(AccountPayment, self).post()
            return res

    @api.multi
    def show_new_post_payment(self):
        if self.multiple_post_line != 3:
            self.multiple_post_line += 1
        return {
            "type": "ir.actions.do_nothing",
        }

    def _create_payment_entry_with_account(self, amount,account):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the paiement in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        self.invoice_ids.register_payment(counterpart_aml)

        #Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0
        liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        liquidity_aml_dict.update({'account_id':account.id})
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move