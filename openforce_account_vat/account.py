# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (alessandrocamilli@openforce.it)
#    Copyright (C) 2014
#    Openforce (<http://www.openforce.it>)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp import netsvc


class statement_generic_account_line(orm.Model):
    _inherit ='statement.generic.account.line'
    _columns = {
        'description': fields.char('Description'),
        }

class account_vat_period_end_statement(orm.Model):
    _inherit = "account.vat.period.end.statement"
    
    def _get_default_interest(self, cr, uid, context=None):
        res = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        company = user.company_id
        return company.of_account_end_vat_statement_interest
    
    def _get_default_interest_percent(self, cr, uid, context=None):
        res = {}
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        company = user.company_id
        if not company.of_account_end_vat_statement_interest:
            return 0 
        return company.of_account_end_vat_statement_interest_percent
    
    
    _columns = {
            'interest': fields.boolean('Compute Interest'),
            'interest_percent': fields.float('Interest - Percent'),
            'print_account_vat_group': fields.boolean('Group by account VAT'),
            'print_page_from': fields.integer('Page number from'),
            'print_page_year': fields.char('Page number year', size=10),
        }
    
    _defaults = {
            'interest' : _get_default_interest,
            'interest_percent' : _get_default_interest_percent,
            'print_account_vat_group': True,
            'print_page_from': 1,
        }
    
    
    def onchange_interest(self, cr, uid, ids, interest, context=None):
        res = {}
        if not ids:
            return res
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        company = user.company_id
        
        # Test account in config
        if interest:
            acc_id = self.get_account_interest(cr, uid, ids, context)
        res = {
               'value' : {
                          'interest_percent' : company.of_account_end_vat_statement_interest_percent,
                          }
               }
        return res
    
    def get_account_interest(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        company = user.company_id
        if company.of_account_end_vat_statement_interest:
            if not company.of_account_end_vat_statement_interest_account_id:
                raise orm.except_orm(_('Error VAT Configuration!'),
                                     _("The account for vat interest must be configurated") )
        
        return company.of_account_end_vat_statement_interest_account_id.id
        
    def compute_amounts(self, cr, uid, ids, context=None):
        '''
        Line of Interest
        '''
        statement_generic_account_line_obj = self.pool['statement.generic.account.line'] 
        decimal_precision_obj = self.pool['decimal.precision']
        
        res = super(account_vat_period_end_statement, self).compute_amounts(cr, uid, ids, context=context)
        
        for end_st in self.browse(cr, uid, ids):
            interest_amount = 0.0
            # if exits Delete line with interest
            acc_id = self.get_account_interest(cr, uid, ids, context)
            domain = [('account_id','=', acc_id),('statement_id','=', end_st.id)]
            line_ids = statement_generic_account_line_obj.search(cr, uid, domain)
            if line_ids:
                statement_generic_account_line_obj.unlink(cr, uid, line_ids)
                
            # Compute interest
            if end_st.interest and end_st.authority_vat_amount > 0:
                interest_amount = -1 * round(end_st.authority_vat_amount * \
                                (float(end_st.interest) / 100), \
                                decimal_precision_obj.precision_get(cr, uid, 'Account'))
            # Add line with interest
            if interest_amount:
                val= {
                    'statement_id' : end_st.id,
                    'account_id' : acc_id,
                    'amount' : interest_amount,
                    }
                statement_generic_account_line_obj.create(cr, uid, val)
            
        return True