# -*- coding: utf-8 -*-
##############################################################################
#    
#    Author: Alessandro Camilli (a.camilli@yahoo.it)
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

from osv import fields, orm

class res_company(orm.Model):
    _inherit = "res.company"
    _columns = {
        'of_account_end_vat_st_split_payment_transitory_account_id': 
                    fields.many2one('account.account',
                    """Split Payment transitory account""", 
                    help="Account to user for transitory moves by split payment"),
        'of_account_end_vat_st_split_payment_transitory_journal_id': 
                    fields.many2one('account.journal',
                    """Split Payment transitory journal""", 
                    help="Journal to use for transitory moves by split payment"),
        }
    