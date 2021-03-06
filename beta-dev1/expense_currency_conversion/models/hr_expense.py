# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
#from odoo.exceptions import UserError, RedirectWarning, ValidationError
#from datetime import datetime
#from werkzeug import url_encode

class HrExpense(models.Model):
    _inherit = 'hr.expense'
    
    @api.multi
    def _calculate_rate(self):
        self.non_company_currency_value = self.unit_amount * self.quantity
    @api.multi
    def _is_different_currency(self):
        for obj in self:
            company_cur = self.env.user.company_id.currency_id.id
            if obj.currency_id.id != company_cur:
                obj.is_different_currency = True
    non_company_currency_rate = fields.Float(string='Currency Rate',readonly="1")
    non_company_currency_value = fields.Float(string="Original Expense Claim Value",readonly="1")
    non_company_currency = fields.Char(string="Original Currency",readonly="1")
    is_different_currency = fields.Boolean(compute=_is_different_currency,string="Different Curency")
    rate_applied = fields.Boolean(string="Rate Applied")
    
    @api.multi
    def apply_rate(self):
        self.non_company_currency_rate = self.currency_id.rate
        unit_amount = self.non_company_currency_rate * self.unit_amount
        self.non_company_currency_value = self.unit_amount * self.quantity
        self.non_company_currency = self.currency_id.name
        
        vals = {'unit_amount': unit_amount,
                'rate_applied':True,
                'currency_id':self.env.user.company_id.currency_id.id}
        return self.write(vals)
        
class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.one
    @api.depends('expense_line_ids', 'expense_line_ids.total_amount', 'expense_line_ids.currency_id')
    def _compute_amount(self):
        self.total_amount = sum(self.expense_line_ids.mapped('total_amount'))
    
