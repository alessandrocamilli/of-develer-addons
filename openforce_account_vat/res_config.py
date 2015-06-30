# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@openforce.it)
#    Copyright (C) 2014
#    Openforce di Camilli Alessandro (www.openforce.it)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, orm, osv
from openerp.tools.translate import _

class openfoce_config_setting(osv.osv_memory):
    
    #_name = "openforce.config.settings"
    #_inherit = 'openforce.config.settings'
    _inherit = 'account.config.settings'
    
    _columns = {
        'of_account_end_vat_statement_interest': fields.boolean('Interest on End Vat Statement', 
                    help="Apply interest on end vat statement"),
        'of_account_end_vat_statement_interest_percent': fields.float('Interest on End Vat Statement - %', 
                    help="Apply interest on end vat statement"),
        'of_account_end_vat_statement_interest_account_id': fields.many2one('account.account', 'Interest on End Vat Statement - Account', 
                    help="Apply interest on end vat statement"),
        'of_account_end_vat_statement_print_all_tax': fields.boolean('Interest on End Vat Statement - Print all taxes', 
                    help="Print all taxes, also without amount"),        
        }
        
    _defaults = {
        'of_account_end_vat_statement_interest': False,
        'of_account_end_vat_statement_print_all_tax': False,
    }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(openfoce_config_setting, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({
                'of_account_end_vat_statement_interest': (
                    company.of_account_end_vat_statement_interest
                    or False), 
                'of_account_end_vat_statement_interest_percent': (
                    company.of_account_end_vat_statement_interest_percent
                    or False),
                'of_account_end_vat_statement_interest_account_id': (
                    company.of_account_end_vat_statement_interest_account_id
                    and company.of_account_end_vat_statement_interest_account_id.id 
                    or False),
                'of_account_end_vat_statement_print_all_tax': (
                    company.of_account_end_vat_statement_print_all_tax
                    or False),
                })
        else: 
            res['value'].update({
                'of_account_end_vat_statement_interest': 0, 
                'of_account_end_vat_statement_interest_percent': 0,
                'of_account_end_vat_statement_interest_account_id': False,
                'of_account_end_vat_statement_print_all_tax': False
                })
        return res
    
    def get_of_default_account_vat(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return {
            'of_account_end_vat_statement_interest': user.company_id.of_account_end_vat_statement_interest,
            'of_account_end_vat_statement_interest_percent': user.company_id.of_account_end_vat_statement_interest_percent,
            'of_account_end_vat_statement_interest_account_id': user.company_id.of_account_end_vat_statement_interest_account_id.id,
            'of_account_end_vat_statement_print_all_tax': user.company_id.of_account_end_vat_statement_print_all_tax,
        }
    def set_of_default_account_vat(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        user.company_id.write({
            'of_account_end_vat_statement_interest': config.of_account_end_vat_statement_interest,
            'of_account_end_vat_statement_interest_percent': config.of_account_end_vat_statement_interest_percent,
            'of_account_end_vat_statement_interest_account_id': config.of_account_end_vat_statement_interest_account_id.id,
            'of_account_end_vat_statement_print_all_tax': config.of_account_end_vat_statement_print_all_tax,
        })
