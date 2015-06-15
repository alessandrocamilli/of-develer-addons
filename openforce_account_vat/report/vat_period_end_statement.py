# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from report import report_sxw
from tools.translate import _
from openerp.osv import orm
from account_vat_period_end_statement.report import vat_period_end_statement

class print_vat_period_end_statement(vat_period_end_statement.print_vat_period_end_statement):
    
    _inherit = 'parser.vat.period.end.statement'
    
    def __init__(self, cr, uid, name, context=None):
        
        super(print_vat_period_end_statement, self).__init__(cr, uid, name, context)
        #self.localcontext.update({
        #    'convert': self.convert,
        #})

    def _build_codes_dict(self, tax_code, res={}, context=None):
        '''
        Extend to possibility to print all taxes with amount or base amount
        '''
        of_config_obj = self.pool['account.config.settings']
        of_vat_config = of_config_obj.get_default_account_vat( 
                                                        self.cr, self.uid, 
                                                        fields=None, 
                                                        context=None)
        if context is None:
            context = {}
        tax_pool = self.pool.get('account.tax')
        
        # search for taxes linked to that code
        tax_ids = tax_pool.search(self.cr, self.uid, [('tax_code_id', '=', tax_code.id)], context=context)
        if tax_ids:
            tax = tax_pool.browse(self.cr, self.uid, tax_ids[0], context=context)
            # search for the related base code
            base_code = tax.base_code_id or tax.parent_id and tax.parent_id.base_code_id or False
            if not base_code:
                raise orm.except_orm(_('Error'), 
                    _('No base code found for tax code %s') % tax_code.name)
            # check if every tax is linked to the same tax code and base code
            for tax in tax_pool.browse(self.cr, self.uid, tax_ids, context=context):
                test_base_code = tax.base_code_id or tax.parent_id and tax.parent_id.base_code_id or False
                if test_base_code.id != base_code.id:
                    raise orm.except_orm(_('Error'), 
                        _('Not every tax linked to tax code %s is linked \
                            the same base code') 
                        % tax_code.name)
            
            if tax_code.sum_period \
                    or base_code.sum_period \
                    and of_vat_config['of_account_end_vat_statement_print_all_tax']:
                res[tax_code.name] = {
                        'vat': tax_code.sum_period,
                        'base': base_code.sum_period,
                    }
        for child_code in tax_code.child_ids:
                res = self._build_codes_dict(child_code, res=res, context=context)
                
        return res
report_sxw.report_sxw('report.account.print.vat.period.end.statement_openforce_vat',
                      'account.vat.period.end.statement',
                      'addons/openforce_account_vat/report/vat_period_end_statement.mako',
                      parser=print_vat_period_end_statement)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
