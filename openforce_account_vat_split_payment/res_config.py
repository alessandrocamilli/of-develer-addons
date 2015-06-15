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
    
    #_inherit = 'openforce.config.settings'
    _inherit = 'account.config.settings'
    
    _columns = {
        'of_account_end_vat_st_split_payment_transitory_account_id': 
                    fields.many2one('account.account',
                    """Split Payment transitory account""", 
                    help="Account to use for transitory moves by split payment"),
        'of_account_end_vat_st_split_payment_transitory_journal_id': 
                    fields.many2one('account.journal',
                    """Split Payment transitory journal""", 
                    help="Journal to use for transitory moves by split payment"),
        }
        
    def get_default_account_vat_sp(self, cr, uid, fields, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        res  ={}
        #res = super(openfoce_config_setting,self).get_default_account_vat(cr, uid, fields, context=context)
        res['of_account_end_vat_st_split_payment_transitory_account_id'] = \
            user.company_id.of_account_end_vat_st_split_payment_transitory_account_id.id
        res['of_account_end_vat_st_split_payment_transitory_journal_id'] = \
            user.company_id.of_account_end_vat_st_split_payment_transitory_journal_id.id
        return res
    
    def set_default_account_vat_sp(self, cr, uid, ids, context=None):
        config = self.browse(cr, uid, ids[0], context)
        user = self.pool.get('res.users').browse(cr, uid, uid, context)
        res  ={}
        #res = super(openfoce_config_setting,self).set_default_account_vat(cr, uid, ids, context=context)
        user.company_id.write({
            'of_account_end_vat_st_split_payment_transitory_account_id': \
                config.of_account_end_vat_st_split_payment_transitory_account_id.id,
            'of_account_end_vat_st_split_payment_transitory_journal_id': \
                config.of_account_end_vat_st_split_payment_transitory_journal_id.id,
        })
        return res
