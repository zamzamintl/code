# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning


class res_users(models.Model):

    _inherit = 'res.users'
    
    def check_user_role(self):
        group_hilti_customer = self.has_group('hilti_modifier_accessrights.group_hilti_customer')
        group_hilti_tester = self.has_group('hilti_modifier_accessrights.group_hilti_tester')
        group_hilti_account_manager = self.has_group('hilti_modifier_accessrights.group_hilti_account_manager')
        group_hilti_engineers = self.has_group('hilti_modifier_accessrights.group_hilti_engineers')
        group_hilti_customer_service = self.has_group('hilti_modifier_accessrights.group_hilti_customer_service')
        group_hilti_admin = self.has_group('hilti_modifier_accessrights.group_hilti_admin')
        if group_hilti_customer and (group_hilti_tester or group_hilti_account_manager or group_hilti_engineers or group_hilti_customer_service or group_hilti_admin):
            raise UserError(_('You can not assign more then one role to user.'))
        elif group_hilti_tester and (group_hilti_customer or group_hilti_account_manager or group_hilti_engineers or group_hilti_customer_service or group_hilti_admin):
            raise UserError(_('You can not assign more then one role to user.'))
        elif group_hilti_account_manager and (group_hilti_customer or group_hilti_tester or group_hilti_engineers or group_hilti_customer_service or group_hilti_admin):
            raise UserError(_('You can not assign more then one role to user.'))
        elif group_hilti_engineers and (group_hilti_customer or group_hilti_tester or group_hilti_account_manager or group_hilti_customer_service or group_hilti_admin):
            raise UserError(_('You can not assign more then one role to user.'))
        elif group_hilti_customer_service and (group_hilti_customer or group_hilti_tester or group_hilti_account_manager or group_hilti_engineers or group_hilti_admin):
            raise UserError(_('You can not assign more then one role to user.'))
        elif group_hilti_admin and (group_hilti_customer or group_hilti_tester or group_hilti_account_manager or group_hilti_engineers or group_hilti_customer_service):
            raise UserError(_('You can not assign more then one role to user.'))
        if group_hilti_customer:
            self.partner_id.write({
                'type_of_user': 'hilti_customer'
            })
        elif group_hilti_tester:
            self.partner_id.write({
                'type_of_user': 'hilti_tester'
            })
        elif group_hilti_account_manager:
            self.partner_id.write({
                'type_of_user': 'hilti_account_manager'
            })
        elif group_hilti_engineers:
            self.partner_id.write({
                'type_of_user': 'hilti_engineers'
            })
        elif group_hilti_customer_service:
            self.partner_id.write({
                'type_of_user': 'hilti_customer_service'
            })
        elif group_hilti_admin:
            self.partner_id.write({
                'type_of_user': 'hilti_admin'
            })
        return True
    
    @api.multi
    def write(self, vals):
        res = super(res_users, self).write(vals)
        for rec in self:
            rec.check_user_role()
        return res
    
    @api.model
    def create(self, vals):
        rec = super(res_users, self).create(vals)
        rec.check_user_role()
        return rec 
    

class res_partner(models.Model):

    _inherit = 'res.partner'
    
    type_of_user = fields.Selection([
        ('hilti_customer', 'hilti_customer'),
        ('hilti_tester', 'hilti_tester'),
        ('hilti_account_manager', 'hilti_account_manager'),
        ('hilti_engineers', 'hilti_engineers'),
        ('hilti_customer_service', 'hilti_customer_service'),
        ('hilti_admin', 'hilti_admin'),
    ])
