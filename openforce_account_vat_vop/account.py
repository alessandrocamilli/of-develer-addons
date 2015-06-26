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

'''
class statement_generic_account_line(orm.Model):
    _name ='statement.generic.account.line'
    _columns = {
        }
'''
class account_tax_code(orm.Model):
    _inherit = "account.tax.code"
    
    def _get_lines_vat_on_payment(self, cr, uid, ids, context):
        res = []
        if context is None:
            context = {}
        move_state = ('posted', )
        if context.get('state', False) == 'all':
            move_state = ('draft', 'posted', )
        if context.get('period_id', False):
            period_id = context['period_id']
        # Without where passing, setting params from context 
        where = ''
        where_params = []
        if period_id:
            where += ' AND line.period_id=%s '
            where_params.append(period_id)
        if move_state:
            where += ' AND move.state IN %s '
            where_params.append(move_state)
        where_params = tuple(where_params)
        parent_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)]))
        for tax_code_id in parent_ids:
            cr.execute('SELECT line.id AS line_id \
                    FROM account_move_line AS line, \
                        account_move AS move \
                        LEFT JOIN account_invoice invoice ON \
                            (invoice.move_id = move.id) \
                    WHERE line.tax_code_id IN %s '+where+' \
                        AND move.id = line.move_id \
                        AND invoice.id IS NULL \
                             GROUP BY line.id',
                                (parent_ids,) + where_params)
            lines_paid = cr.fetchall()
            for line in lines_paid:
                res.append(line[0])
            
        return res
    
    def _sum(self, cr, uid, ids, name, args, context, where ='', where_params=()):
        '''
        It extends standard compute. With "vat_on_payment" in the context, recompute
        the amounts with new policy for only lines of payments.
        '''
        tax_code_obj = self.pool['account.tax.code']
        res = super(account_tax_code, self)._sum(cr, uid, ids, name, args, context, where, where_params)
        
        if context.get('based_on', 'invoices') == 'vat_on_payment':
            parent_ids = tuple(self.search(cr, uid, [('parent_id', 'child_of', ids)]))
            
            for tax_code_id in parent_ids:
                # Nature of tax code for search the inverse lines
                # Use lines_paid for to have one statement that retrieve the right lines
                lines_paid = tax_code_obj._get_lines_vat_on_payment(cr, 
                                                                uid, 
                                                                [tax_code_id],
                                                                context)
                if not lines_paid:
                    lines_paid = ()
                    res[tax_code_id] = 0.0
                else:
                    lines_paid = tuple(lines_paid)
                    cr.execute('SELECT line.tax_code_id, sum(line.tax_amount) \
                                    FROM account_move_line AS line \
                                    WHERE line.id IN %s \
                                    GROUP BY line.tax_code_id',(lines_paid,))
                    res=dict(cr.fetchall())
                '''
                cr.execute('SELECT line.tax_code_id, sum(line.tax_amount) \
                    FROM account_move_line AS line, \
                        account_move AS move \
                        LEFT JOIN account_invoice invoice ON \
                            (invoice.move_id = move.id) \
                    WHERE line.tax_code_id IN %s '+where+' \
                        AND move.id = line.move_id \
                        AND invoice.id IS NULL \
                            GROUP BY line.tax_code_id',
                                (parent_ids,) + where_params)
                                '''
                obj_precision = self.pool.get('decimal.precision')
                res2 = {}
                for record in self.browse(cr, uid, ids, context=context):
                    def _rec_get(record):
                        amount = res.get(record.id, 0.0)
                        for rec in record.child_ids:
                            amount += _rec_get(rec) * rec.sign
                        return amount
                    res2[record.id] = round(_rec_get(record), obj_precision.precision_get(cr, uid, 'Account'))
                return res2
        return res
    
class account_vat_period_end_statement(orm.Model):
    _inherit = "account.vat.period.end.statement"
    
    _columns = {
        'debit_vat_suspension_account_line_ids': fields.one2many('statement.debit.suspension.account.line', 'statement_id', 'Debit suspension VAT', help='The accounts containing the debit suspension VAT amount', states={'confirmed': [('readonly', True)], 'paid': [('readonly', True)], 'draft': [('readonly', False)]}),
        'credit_vat_suspension_account_line_ids': fields.one2many('statement.credit.suspension.account.line', 'statement_id', 'Credit suspension VAT', help='The accounts containing the credit suspension VAT amount ', states={'confirmed': [('readonly', True)], 'paid': [('readonly', True)], 'draft': [('readonly', False)]}),
        }
    
    _defaults = {
        }
    
    def compute_amounts(self, cr, uid, ids, context=None):
        '''
        Vat on payment throw shadow tax accounts
        '''
        decimal_precision_obj = self.pool['decimal.precision']
        tax_code_obj = self.pool['account.tax.code']
        debit_suspension_line_obj = self.pool['statement.debit.suspension.account.line']
        credit_suspension_line_obj = self.pool['statement.credit.suspension.account.line']
        
        res = super(account_vat_period_end_statement, self).compute_amounts(cr, uid, ids, context=context)
        
        for end_st in self.browse(cr, uid, ids):
            
            # Debits
            debit_line_ids = []
            for line in end_st.debit_vat_account_line_ids:
                ###
                print line.tax_code_id.vat_on_payment_related_tax_code_id.name
                ###
                if not line.tax_code_id.vat_on_payment_related_tax_code_id:
                    continue
                tax_code = line.tax_code_id.vat_on_payment_related_tax_code_id
                total = 0.0
                total_paid = 0.0
                lines_paid = []
                for period in end_st.period_ids:
                    context['period_id'] = period.id
                    context['based_on'] = '' # normal compute
                    total += tax_code_obj.browse(cr, uid, tax_code.id, context).sum_period
                    context['based_on'] = 'vat_on_payment'
                    total_paid += tax_code_obj.browse(cr, uid, tax_code.id, context).sum_period
                    lines_paid += tax_code_obj._get_lines_vat_on_payment(cr, 
                                                                uid, 
                                                                [tax_code.id],
                                                                context)
                if total or total_paid:
                    debit_line_ids.append({
                        'account_id': tax_code.vat_statement_account_id.id,
                        'tax_code_id': tax_code.id,
                        'amount': total * tax_code.vat_statement_sign,
                        'paid': total_paid * tax_code.vat_statement_sign,
                        'line_payment_ids': lines_paid and [(6, 0, lines_paid)] 
                            or False
                        })
            # Credits
            credit_line_ids = []
            for line in end_st.credit_vat_account_line_ids:
                ###
                print line.tax_code_id.vat_on_payment_related_tax_code_id.name
                ###
                if not line.tax_code_id.vat_on_payment_related_tax_code_id:
                    continue
                tax_code = line.tax_code_id.vat_on_payment_related_tax_code_id
                total = 0.0
                total_paid = 0.0
                lines_paid = []
                for period in end_st.period_ids:
                    context['period_id'] = period.id
                    context['based_on'] = '' # normal compute
                    total += tax_code_obj.browse(cr, uid, tax_code.id, context).sum_period
                    context['based_on'] = 'vat_on_payment'
                    total_paid += tax_code_obj.browse(cr, uid, tax_code.id, context).sum_period
                    lines_paid += tax_code_obj._get_lines_vat_on_payment(cr, 
                                                                uid, 
                                                                [tax_code.id],
                                                                context)
                if total or total_paid:
                    credit_line_ids.append({
                        'account_id': tax_code.vat_statement_account_id.id,
                        'tax_code_id': tax_code.id,
                        'amount': total * tax_code.vat_statement_sign,
                        'paid': total_paid * tax_code.vat_statement_sign,
                        'line_payment_ids': lines_paid and [(6, 0, lines_paid)] 
                            or False
                        })
            # Unlink existing lines
            for debit_line in end_st.debit_vat_suspension_account_line_ids:
                debit_line.unlink()
            for credit_line in end_st.credit_vat_suspension_account_line_ids:
                credit_line.unlink()
            # Add new lines
            for debit_vals in debit_line_ids:
                debit_vals.update({'statement_id': end_st.id})
                debit_suspension_line_obj.create(cr, uid, debit_vals, context=context)
            for credit_vals in credit_line_ids:
                credit_vals.update({'statement_id': end_st.id})
                credit_suspension_line_obj.create(cr, uid, credit_vals, context=context)
        
        return res
    
class statement_debit_suspension_account_line(orm.Model):
    _name='statement.debit.suspension.account.line'
    _columns = {
        'account_id': fields.many2one('account.account', 'Account'),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', required=True),
        'statement_id': fields.many2one('account.vat.period.end.statement', 'VAT statement'),
        'amount': fields.float('Amount', digits_compute= dp.get_precision('Account')),
        'paid': fields.float('Paid', digits_compute= dp.get_precision('Account')),
        'line_payment_ids': fields.many2many(
            'account.move.line', 'statement_debit_suspension_payment_rel', 'debit_suspension_line_id',
            'account_move_line_id', 'Vat Payment Lines'),
        }

class statement_credit_suspension_account_line(orm.Model):
    _name='statement.credit.suspension.account.line'
    _columns = {
        'account_id': fields.many2one('account.account', 'Account'),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', required=True),
        'statement_id': fields.many2one('account.vat.period.end.statement', 'VAT statement'),
        'amount': fields.float('Amount', digits_compute= dp.get_precision('Account')),
        'paid': fields.float('Paid', digits_compute= dp.get_precision('Account')),
        'line_payment_ids': fields.many2many(
            'account.move.line', 'statement_credit_suspension_payment_rel', 'credit_suspension_line_id',
            'account_move_line_id', 'Vat Payment Lines'),
        }
        