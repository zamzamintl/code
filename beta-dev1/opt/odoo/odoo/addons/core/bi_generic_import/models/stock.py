# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C) 2015-Today BrowseInfo (<http://www.browseinfo.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from xlrd import open_workbook
import xmlrpclib
import xlrd
import os
import tempfile
import binascii
from xlwt import Workbook
import xlwt

try:
    import xmlrpclib
except ImportError:
    _logger.debug('Cannot `import xmlrpclib`.')

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')
# for xls 
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')

class gen_inv(models.TransientModel):
    _name = "gen.inv"

    file = fields.Binary('File')
    inv_name = fields.Char('Inventory Name')
    location_id = fields.Many2one('stock.location', "Location")
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
#    filename = fields.Char('Filename')

    @api.multi
    def import_csv(self):

        """Load Inventory data from the CSV file."""
        if self.import_option == 'csv': 
            """Load Inventory data from the CSV file."""
            ctx = self._context
            keys=['code', 'quantity']
            stloc_obj = self.env['stock.location']
            inventory_obj = self.env['stock.inventory']
            product_obj = self.env['product.product']
            data = base64.b64decode(self.file)
            file_input = cStringIO.StringIO(data)
            file_input.seek(0)
            reader_info = []
            reader = csv.reader(file_input, delimiter=',')
    
            try:
                reader_info.extend(reader)
            except Exception:
                raise exceptions.Warning(_("Not a valid file!"))
            values = {}
            inventory_id = inventory_obj.create({'name':self.inv_name})
            for i in range(len(reader_info)):
                val = {}
                try:
                     field= map(str, reader_info[i])
                except ValueError:
                     raise exceptions.Warning(_("Dont Use Charecter only use numbers"))
                
    #             field = reader_info[i]
                values = dict(zip(keys, field))
                prod_lst = product_obj.search([('default_code', '=',
                                                values['code'])])
                if prod_lst:
                    val['product'] = prod_lst[0].id
                    val['quantity'] = values['quantity']
                if bool(val):
                    product_uom_id=product_obj.browse(val['product']).uom_id
                    res = inventory_id.write({
                'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity']})]})
                else:
                    continue
            res = inventory_obj.with_context(ids=inventory_id).prepare_inventory()
            return res
        else:
            fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            inventory_id = self.env['stock.inventory'].create({'name':self.inv_name})
            product_obj = self.env['product.product']
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = (map(lambda row:isinstance(row.value, unicode) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if line:
                        values.update({'code':line[0],'quantity':line[1]})
                        prod_lst = product_obj.search([('default_code', '=',
                                                    values['code'])])
                        if prod_lst:
                            val['product'] = prod_lst[0].id
                            val['quantity'] = values['quantity']
                        if bool(val):
                            product_uom_id=product_obj.browse(val['product']).uom_id
                            res = inventory_id.write({
                        'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity']})]})
                        else:
                            continue
                    res = self.env['stock.inventory'].with_context(ids=inventory_id).prepare_inventory()
                    return res




#
class stock_inventory(models.Model):
    _inherit = "stock.inventory"


    @api.multi
    def action_start(self):
	if self._context.get('ids'):
		self = self._context.get('ids')
		for inventory in self:
		    vals = {'state': 'confirm', 'date': fields.Datetime.now()}
		    if (inventory.filter != 'partial') and not inventory.line_ids:
		        vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory.line_ids]})
		    inventory.write(vals)
	else:
		super(stock_inventory, self).action_start()
        return True
    prepare_inventory = action_start

