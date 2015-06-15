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


class account_tax_code(orm.Model):
    _inherit = "account.tax.code"
    _columns = {
        'split_payment': fields.boolean("Subject to Split Payment"),
        }

class account_invoice(orm.Model):
    _inherit = "account.invoice"
    _columns = {
        'split_payment_move_id': fields.many2one("account.move", 
                            "Split Payment Move", 
                            readonly =True),
        }
    
    def invoice_validate(self, cr, uid, ids, context=None):
        '''
        Creation of move to refund the invoice with amount of split payemnt
        '''
        tax_code_obj = self.pool['account.tax.code']
        account_move_obj = self.pool['account.move']
        account_move_line_obj = self.pool['account.move.line']
        of_config_obj = self.pool['account.config.settings']
        vat_config = of_config_obj.get_default_account_vat_sp( 
                                                    cr, uid, fields, 
                                                    context=None)
        domain = [('split_payment', '=', True)]
        tax_code_to_split_ids = tax_code_obj.search(cr, uid, domain)
        
        for inv in self.browse(cr, uid, ids):
            lines_to_reconcile = []
            # Lines with split payment
            domain = [('move_id', '=', inv.move_id.id)]
            acc_inv_line_ids = account_move_line_obj.search(cr, uid, domain)
            lines_to_refund = []
            lines_to_split = []
            for move_line in account_move_line_obj.browse(cr, uid, 
                                                         acc_inv_line_ids):
                if move_line.reconcile_id \
                    or move_line.reconcile_partial_id:
                    continue
                if move_line.tax_code_id.id in tax_code_to_split_ids:
                    lines_to_split.append(move_line)
                elif move_line.account_id.type in ['receivable', "payable"]:
                    lines_to_refund.append(move_line)
                
            if lines_to_split:
                if not vat_config['of_account_end_vat_st_split_payment_transitory_account_id']:
                    raise orm.except_orm(_('Error Missing VAT Config!'),
                                         _("Default Account for split payment"))
                if not vat_config['of_account_end_vat_st_split_payment_transitory_journal_id']:
                    raise orm.except_orm(_('Error Missing VAT Config!'),
                                         _("Default Journal for split payment"))
                # Move
                ref = 'Split Payment ft %s ' % (inv.number,)
                move_id= account_move_obj.create(cr, uid, {
                    'ref': ref,
                    'journal_id': vat_config['of_account_end_vat_st_split_payment_transitory_journal_id'],
                    'date': inv.date_invoice,
                    'period_id': inv.period_id.id
                    }, context=context)
                for line in lines_to_split:
                    # ... Transitory line
                    transitory_line_id = account_move_line_obj.create(cr, uid, {
                            'name': ref,
                            'account_id': vat_config['of_account_end_vat_st_split_payment_transitory_account_id'],
                            'credit': line.debit,
                            'debit': line.credit,
                            'move_id': move_id,
                            #'partner_id': line.partner_id.id or False, 
                            }, context=context)
                    # ... Refund line
                    refund_line_id = account_move_line_obj.create(cr, uid, {
                            'name': 'Split Payment ' + line.tax_code_id.name,
                            'account_id': inv.account_id.id,
                            'credit': line.credit,
                            'debit': line.debit,
                            'move_id': move_id,
                            'partner_id': inv.partner_id.id or False, 
                            }, context=context)
                ## reconcile with the first line
                if lines_to_refund:
                    lines_to_reconcile.append([lines_to_refund[0].id, 
                                              refund_line_id])
            # Reconciliations
            for lines_rec_ids in lines_to_reconcile:
                rec_id = account_move_line_obj.reconcile_partial(cr, uid, 
                                                    lines_rec_ids, 
                                                    context=context)
                # Ref refund move to invoice
                self.write(cr, uid, [inv.id], 
                           {'split_payment_move_id': move_id
                            })        
        
        return super(account_invoice, self).invoice_validate(cr, uid, 
                                                             ids, 
                                                             context=context) 
    def action_cancel(self, cr, uid, ids, context=None):
        '''
        It remove payments generate from split payment before invoice cancel
        '''
        reconcile_obj = self.pool['account.move.reconcile']
        move_obj = self.pool['account.move']
        
        for inv in self.browse(cr, uid, ids):
            if not inv.split_payment_move_id:
                continue
            recs = []
            for split_line in inv.split_payment_move_id.line_id:
                if split_line.reconcile_id:
                    recs += [split_line.reconcile_id.id]
                if split_line.reconcile_partial_id:
                    recs += [split_line.reconcile_partial_id.id]
            if recs:
                reconcile_obj.unlink(cr, uid, recs)
            move_obj.unlink(cr, uid, inv.split_payment_move_id.id)
        
        return super(account_invoice, self).action_cancel(cr, uid, 
                                                             ids, 
                                                             context=context)

class statement_generic_account_line(orm.Model):
    _inherit ='statement.generic.account.line'
    _columns = {
        'split_payment': fields.boolean('Line created by Split Payment'),
        'description': fields.char('Description'),
        }
    
class account_vat_period_end_statement(orm.Model):
    _inherit = "account.vat.period.end.statement"
  
    _columns = {
         'split_payment_line_ids': fields.one2many('account.vat.statement.split.payment.line', 'statement_id', 'Lines for Split Payments', help='', 
                                                   states={'confirmed': [('readonly', True)], 'paid': [('readonly', True)], 'draft': [('readonly', False)]}),       
         #'total_vat_end_period_amount': fields.function(_compute_total_vat_end_period_amount, method=True, string='Total VAT Amount'),
         # for new recompute with prorata
         #'authority_vat_amount': fields.function(_compute_authority_vat_amount, method=True, string='Authority VAT Amount'),
        }
    
    def _prepare_line_to_split(self, cr, uid, line, statement_id, context=None):
        line_to_split = {
            'statement_id': statement_id,
            'tax_code_id': line.tax_code_id.id,
            'tax_amount': line.tax_amount,
            'line_to_split_id': line.id
        }
        return line_to_split
    
    def compute_amounts(self, cr, uid, ids, context=None):
        '''
        Creation of Lines to split  and total in the generic account section
        '''
        dp_obj = self.pool['decimal.precision']
        tax_code_obj = self.pool['account.tax.code']
        account_move_line_obj = self.pool['account.move.line']
        split_payment_line_obj = \
                    self.pool['account.vat.statement.split.payment.line']
        st_generic_line_obj = self.pool['statement.generic.account.line']
        of_config_obj = self.pool['account.config.settings']
        vat_config = of_config_obj.get_default_account_vat_sp( 
                                                    cr, uid, fields, 
                                                    context=None)
        #
        # Delete existing lines
        #
        for end_st in self.browse(cr, uid, ids):
            domain = [('statement_id', '=', end_st.id)]
            line_ids = split_payment_line_obj.search(cr, uid, domain)
            if line_ids:
                split_payment_line_obj.unlink(cr, uid, line_ids)
            
            # generic line
            domain = [('statement_id', '=', end_st.id),
                      ('split_payment', '=', True)]
            gen_line_ids = st_generic_line_obj.search(cr, uid, domain)
            if gen_line_ids:
                st_generic_line_obj.unlink(cr, uid, gen_line_ids)
        #
        # Compute
        #
        res = super(account_vat_period_end_statement, self).compute_amounts(cr, 
                                                    uid, ids, context=context)
        domain = [('split_payment', '=', True)]
        tax_code_to_split_ids = tax_code_obj.search(cr, uid, domain)
        
        for end_st in self.browse(cr, uid, ids):
            amount_to_split = 0.0
            # Find lines to split
            lines_to_split = []
            for period in end_st.period_ids:
                for tax_code_to_split in tax_code_obj.browse(cr, uid, 
                                                    tax_code_to_split_ids):
                    domain = [('tax_code_id', '=', tax_code_to_split.id),
                              ('period_id', '=', period.id)]
                    to_split_ids = account_move_line_obj.search(cr, uid, 
                                                                     domain)
                    # Create Line to split
                    if to_split_ids:
                        for line_to_split in account_move_line_obj.browse(
                                                    cr, uid, to_split_ids):
                            line_data = self._prepare_line_to_split(
                                                    cr, uid, 
                                                    line_to_split, 
                                                    end_st.id, 
                                                    context)
                            split_payment_line_obj.create(cr, uid, line_data)
                    lines_to_split += to_split_ids 
                    
            # Total Split on statement
            # grouped by tax code
            line_generic = {}
            for split_line in end_st.split_payment_line_ids:
                # sub-group tax code    
                if not line_generic.get(split_line.tax_code_id.id):
                    line_generic[split_line.tax_code_id.id] = \
                                                    split_line.tax_amount
                else:
                    line_generic[split_line.tax_code_id.id] += \
                                                    split_line.tax_amount
                
            #for account_id, tax_codes in line_generic.iteritems():
            for tax_code_id, amount in line_generic.iteritems():
                tax_code = tax_code_obj.browse(cr, uid, tax_code_id)
                val = {
                    'split_payment' : True,
                    'statement_id' : end_st.id,
                    'account_id' : vat_config['of_account_end_vat_st_split_payment_transitory_account_id'],
                    'description' : 'Split Payment - %s' % (tax_code.name),
                    'amount' : round( amount, dp_obj.precision_get(
                                                                cr, 
                                                                uid, 
                                                                'Account'))
                }
                st_generic_line_obj.create(cr, uid, val)
        return res

class account_vat_statement_split_payment_line(orm.Model):
    _name='account.vat.statement.split.payment.line'
    
    # Compute invoice ref
    def _get_invoice_data(self, cr, uid, ids, field_names, args, context=None):
        account_move_line_obj = self.pool['account.move.line']
        invoice_obj = self.pool['account.invoice']
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            # Line to pay
            lines_to_pay = []
            domain = [('move_id', '=', line.line_to_split_id.move_id.id),
                      ('reconcile_id', '=', False),
                      ('reconcile_partial_id', '=', False)]
            ml_inv_ids = account_move_line_obj.search(cr, uid, domain)
            for move_line in account_move_line_obj.browse(cr, uid, ml_inv_ids):
                if move_line.account_id.type in['receivable', "payable"]:
                    lines_to_pay.append(move_line.id)
            # Invoice
            inv = False
            domain = [('move_id', '=', line.line_to_split_id.move_id.id)]
            inv_ids = invoice_obj.search(cr, uid, domain)
            if inv_ids:
                inv = invoice_obj.browse(cr, uid, inv_ids[0])
            
            res[line.id] = {
                #'line_to_pay_ids' :(6, 0, lines_to_pay)
                'line_to_pay_id' : lines_to_pay and lines_to_pay[0] or False,  
                'invoice_id' : inv and inv.id or False,  
                'partner_id' : inv and inv.partner_id.id or False,  
            }
        return res
    
    _columns = {
        'statement_id': fields.many2one('account.vat.period.end.statement', 
                'End vat Statement', readonly=True, ondelete="cascade"),
        'tax_code_id': fields.many2one('account.tax.code', 'Tax Code', 
                                       readonly=True),
        'tax_amount': fields.float('tax_amount', 
                digits_compute= dp.get_precision('Account'), readonly=True),
        'reconcile_id': fields.many2one('account.move.reconcile', 'Reconcile', 
                help="Reconciliation with invoice", 
                ondelete="set null", readonly=True),
        'line_to_split_id': fields.many2one('account.move.line', 'Split Line', 
                ondelete="set null", readonly=True),
        'account_to_split_id': fields.related('line_to_split_id', 'account_id', 
                type='many2one', relation='account.account', readonly=True, 
                store=False),
        'line_to_pay_id': fields.function(_get_invoice_data, 
                string='Line to pay', multi='invoice_data', #store=True,
                type='many2one', relation="account.move.line"),
        'invoice_id': fields.function(_get_invoice_data, 
                string='Invoice', multi='invoice_data', #store=True,
                type='many2one', relation="account.invoice"),
        'partner_id': fields.function(_get_invoice_data, 
                string='Partner', multi='invoice_data', #store=True,
                type='many2one', relation="res.partner",
            ),
        }

    