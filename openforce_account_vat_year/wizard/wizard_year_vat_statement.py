# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Apulia Sofware s.r.l (<info@apuliasoftware.it>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.tools.translate import _
from openerp.osv import orm, fields
import decimal_precision as dp

class wizard_year_statement(orm.TransientModel):

    _name = 'wizard.year.statement'

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear',
                                         required=True),
        'amount_generic': fields.float('Generic Credit or Debit', 
                                       readonly=True),
        'amount_interest': fields.float('Amount Interest'),
        'amount_previous_credit': fields.float('Amount Previous Credit',  readonly=True),
        'amount_previous_debit': fields.float('Amount Previous Debit',  readonly=True),
        'amount_paid_on_statement': fields.float('Amount Paid on Statement',  readonly=True),
        'amount_paid': fields.float('Amount Paid - ON PRINT'),
        'print_page_from': fields.integer('Page number from'),
        'print_page_year': fields.char('Page number year', size=10),
        }
    
    _defaults = {
        'print_page_from' : 1,
        'amount_paid' : 0
        }
    
    def on_change_fiscalyear_id(self, cr, uid, ids, fiscalyear_id, context=None):
        res={}
        
        end_statment_vat_obj = self.pool['account.vat.period.end.statement']
        period_obj = self.pool['account.period']
        dp_obj = self.pool['decimal.precision']
        
        if not fiscalyear_id:
            return res
        fiscalyear = self.pool['account.fiscalyear'].browse(cr, uid, fiscalyear_id)
        # Periods competence
        domain = [('fiscalyear_id', '=', fiscalyear_id)]
        period_ids = period_obj.search(cr, uid, domain)
        
        wiz_val = {}
        # Statements of competence
        statements = []
        domain = [('id', '>', 0)]
        statement_ids = end_statment_vat_obj.search(cr, uid, domain)
        for statement in end_statment_vat_obj.browse(cr, uid, statement_ids):
            statement_valid = True
            for ps in statement.period_ids:
                if ps.id not in period_ids:
                    statement_valid = False
            if statement_valid:
                statements.append(statement.id)
        
        # Statement Generic lines
        amount_generic = 0
        for statement in end_statment_vat_obj.browse(cr, uid, statements):
            for line in statement.generic_vat_account_line_ids:
                print "xx"
                # credits are positive and debits are negative
                amount_generic += line.amount * -1
        wiz_val.update({'amount_generic':amount_generic})
        
        # Statement Paid
        amount_paid = 0
        amount_paid_on_statement = 0
        previous_credit = 0
        previous_debit = 0
        domain = [('state', '=', 'paid')]
        statement_ids = end_statment_vat_obj.search(cr, uid, domain)
        for statement in end_statment_vat_obj.browse(cr, uid, statements):
            if statement.id not in statements:
                continue
            # First period for credit/debit form previous year
            for p in statement.period_ids:
                if p.date_start == fiscalyear.date_start:
                    previous_credit = statement.previous_credit_vat_amount
                    previous_debit = statement.previous_debit_vat_amount
            for line in statement.payment_ids:
                if line.debit:
                    amount_paid += line.debit
                else:
                    amount_paid -= line.credit
        amount_paid_on_statement = amount_paid
        amount_paid += previous_credit
        amount_paid -= previous_debit
        wiz_val.update({
                        'amount_previous_credit': previous_credit,
                        'amount_previous_debit': previous_debit,
                        'amount_paid_on_statement': amount_paid_on_statement,
                        'amount_paid': amount_paid,
                        }) 
        
        res={'value': wiz_val}
        
        return res
    
    def print_report(self, cr, uid, ids, context={}):
        wizard = self.browse(cr, uid, ids, context)[0]
        res = {
            'type': 'ir.actions.report.xml',
            'datas': {'ids': ids,
                      #'model': 'account.move',
                      'model': self._name,
                      'fiscalyear_id': wizard.fiscalyear_id.id,
                      'amount_generic': wizard.amount_generic,
                      'amount_interest': wizard.amount_interest,
                      'amount_previous_credit': wizard.amount_previous_credit,
                      'amount_previous_debit': wizard.amount_previous_debit,
                      'amount_paid': wizard.amount_paid,
                      'year': wizard.fiscalyear_id.name,
                      'print_page_from': wizard.print_page_from,
                      'print_page_year': wizard.print_page_year,
                      },
            'report_name': 'vat.year.end.statement',
        }
        return res