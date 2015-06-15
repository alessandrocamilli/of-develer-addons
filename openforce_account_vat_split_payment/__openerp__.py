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
{
    'name': 'Openforce - VAT Split Payment',
    'version': '0.2',
    'category': 'Localisation/Italy',
    'description': """
    It Handles italian fiscal split payment.
    When Vat period end statement will be create, the tax lines 
    with split payment will be refund.
    It also reconcile the refunds with the relative invoice.
""",
    'author': 'Openforce',
    'website': 'http://www.openforce.it',
    'license': 'AGPL-3',
    "depends" : ['account', 'account_vat_period_end_statement',
                 ],
    "data" : [
        'security/ir.model.access.csv',
        'account_view.xml',
        'res_config_view.xml',
        ],
    "demo" : [],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: