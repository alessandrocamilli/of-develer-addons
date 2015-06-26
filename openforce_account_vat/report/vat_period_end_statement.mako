<html>
<head>
    <style type="text/css">
        ${css}
/*
table.tax_codes {
	border-width: 1px;
	border-spacing: 2px;
	border-style: outset;
	border-color: gray;
	border-collapse: collapse;
	background-color: white;
    margin-right:auto;
    margin-left:auto;
}*/
.table-condensed {
	width: 100%;
}
.table-condensed > thead > tr > th {
        border-bottom: 2px solid lightgrey !important;
    }

tr {
    page-break-inside: avoid;
	height: 20px;
}
th {
	font-size:12px;
}

.line_data > td {
	font-size:12px;
	padding: 4px;
	border-bottom: 1px solid lightgrey !important;
}
.line_subtotal > td {
	font-size:12px;
	font-weight:bold;
	padding: 4px;
}
/*
td {
	font-size:12px;
	padding: 4px;
	border-bottom: 1px solid lightgrey !important;
}*/
.amount {
	text-align: right;
}
.subtotal {
	font-weight: bold;
}
.text-right {
	text-align: right;
}
.text-left {
	text-align: left;
}
    </style>
</head>
<body>
<% setLang(company.partner_id.lang) %>
% for statement in objects:
##<h2 style="text-align: center;">${_("Date")}: ${formatLang(statement.date, date=True)|entity} </h2>

	## ======================
	## Periods detail
	## ======================
	%for period in statement.period_ids:
		<h3>${ _('Period') + ' ' + period.name}<h3>
		## --------------
		## Purchase
		## --------------
		<% ps_tax_codes = [l.tax_code_id.id for l in statement.credit_vat_account_line_ids] %>
		<% ps_tax_codes_amounts = tax_codes_amounts(period.id, ps_tax_codes) %>
		<h4>${ _('Purchase')} </h4>
		<table class="table table-condensed" >
		<thead>
           	<tr>
               	<th style="width:12%;" class="text-left">${ _('Vat code')} </th>
               	<th style="width:37%;" class="text-left">${ _('Description')} </th>
               	<th style="width:15%;" class="text-right">${ _('Base')}</th>
               	<th style="width:12%;" class="text-right">${ _('Vat')}</th>
               	## Columns Deductible / Undeductible only for purchase
               	<th style="width:12%;" class="text-right">${ _('Deductible')} </th>
               	<th style="width:12%;" class="text-right">${ _('Undeductible')}  </th>
        	</tr>
       	</thead>
       	<tbody>
       		## Reset Totals
       		<% total_vat = 0 %>
			<% total_base = 0 %>
			<% total_vat_deductible = 0 %>
			<% total_vat_undeductible = 0 %>
				
			%for ps_tax_code in ps_tax_codes_amounts :
			
				## Prepare values
				<% code = ps_tax_codes_amounts[ps_tax_code]['code'] %>
				<% tax_code = ps_tax_code %>
				<% tax_code_base = ps_tax_codes_amounts[ps_tax_code]['base'] %>
				<% tax_code_vat = ps_tax_codes_amounts[ps_tax_code]['vat'] %>
				<% tax_code_vat_deductible = ps_tax_codes_amounts[ps_tax_code]['vat_deductible'] %>
				<% tax_code_vat_undeductible = ps_tax_codes_amounts[ps_tax_code]['vat_undeductible'] %>
				## ... Credits are negative : in the report will be positive
				<% tax_code_base = -1 * tax_code_base %>
				<% tax_code_vat = -1 * tax_code_vat %>
				<% tax_code_vat_deductible = -1 * tax_code_vat_deductible %>
				<% tax_code_vat_undeductible = -1 * tax_code_vat_undeductible %>
				
				## Print values
				<tr class="line_data">
					<td>${ code|entity }</td>
					<td>${ tax_code|entity }</td>
					<td class="text-right">${ formatLang(tax_code_base)|entity }</td>
					<td class="text-right">${ formatLang(tax_code_vat)|entity }</td>
					<td class="text-right">${ formatLang(tax_code_vat_deductible)|entity }</td>
					<td class="text-right">${ formatLang(tax_code_vat_undeductible)|entity }</td>
				</tr>
				## Sum Totals
				<% total_base = total_base + tax_code_base %>
				<% total_vat = total_vat + tax_code_vat %>
				<% total_vat_deductible = total_vat_deductible + tax_code_vat_deductible %>
				<% total_vat_undeductible = total_vat_undeductible + tax_code_vat_undeductible %>
        	%endfor
        	
        	## Print Totals
        	<tr class="line_subtotal">
				<td></td>
				<td class="total amount">${ _('Total') }</td>
				<td class="subtotal amount">${ formatLang(total_base)|entity }</td>
				<td class="subtotal amount">${ formatLang(total_vat)|entity }</td>
				<td class="subtotal amount">${ formatLang(total_vat_deductible)|entity }</td>
				<td class="subtotal amount">${ formatLang(total_vat_undeductible)|entity }</td>
			</tr>
        	
        </tbody>
        </table>
		## --------------
		## Sale
		## --------------
		<% ps_tax_codes = [l.tax_code_id.id for l in statement.debit_vat_account_line_ids] %>
		<% ps_tax_codes_amounts = tax_codes_amounts(period.id, ps_tax_codes) %>
		<h4>${ _('Sale')} </h4>
		<table class="table table-condensed">
		<thead>
           	<tr>
               	<th style="width:12%;" class="text-left">${ _('Vat code')} </th>
               	<th style="width:37%;" class="text-left">${ _('Description')} </th>
               	<th style="width:15%;" class="amount">${ _('Base')}</th>
               	<th style="width:12%;" class="amount">${ _('Vat')}</th>
               	## Columns Deductible / Undeductible only for purchase
               	<th style="width:12%;" class="amount"> </th>
               	<th style="width:12%;" class="amount"> </th>
        	</tr>
       	</thead>
       	<tbody>
       		## Reset Totals
       		<% total_vat = 0 %>
			<% total_base = 0 %>
			
			%for ps_tax_code in ps_tax_codes_amounts :
			
				## Prepare values
				<% code = ps_tax_codes_amounts[ps_tax_code]['code'] %>
				<% tax_code = ps_tax_code %>
				<% tax_code_base = ps_tax_codes_amounts[ps_tax_code]['base'] %>
				<% tax_code_vat = ps_tax_codes_amounts[ps_tax_code]['vat'] %>
				<% tax_code_vat_deductible = ps_tax_codes_amounts[ps_tax_code]['vat_deductible'] %>
				<% tax_code_vat_undeductible = ps_tax_codes_amounts[ps_tax_code]['vat_undeductible'] %>
				
				## Print values
				<tr class="line_data">
					<td>${ code|entity }</td>
					<td>${ tax_code|entity }</td>
					<td class="amount">${ formatLang(tax_code_base)|entity }</td>
					<td class="amount">${ formatLang(tax_code_vat)|entity }</td>
					<td class="amount"></td>
					<td class="amount"></td>
				</tr>
				## Sum Totals
				<% total_base = total_base + tax_code_base %>
				<% total_vat = total_vat + tax_code_vat %>
        	%endfor
        	
        	## Print Totals
        	<tr class="line_subtotal">
				<td></td>
				<td class="total amount">${ _('Total') }</td>
				<td class="subtotal amount">${ formatLang(total_base)|entity }</td>
				<td class="subtotal amount">${ formatLang(total_vat)|entity }</td>
				<td class="subtotal amount"></td>
				<td class="subtotal amount"></td>
			</tr>
        </tbody>
        </table>
        
        ## --------------
		## Purchase - Suspension
		## --------------
		%if 'credit_vat_suspension_account_line_ids' in statement:
		<h4>${ _('Purchase Suspension')} </h4>
		<table class="table table-condensed">
		<thead>
           	<tr>
               	<th style="width:12%;" class="text-left">${ _('Vat code')} </th>
               	<th style="width:37%;" class="text-left">${ _('Description')} </th>
               	<th style="width:15%;" class="amount"> </th>
               	<th style="width:12%;" class="amount"> </th>
               	## Columns Deductible / Undeductible only for purchase
               	<th style="width:12%;" class="amount">${ _('Amount Registred')} </th>
               	<th style="width:12%;" class="amount">${ _('Amount Paid')} </th>
        	</tr>
       	</thead>
       	<tbody>
       		## Reset Totals
       		<% total_registred = 0 %>
			<% total_paid = 0 %>
			%for line_suspension in statement.credit_vat_suspension_account_line_ids :
				## Prepare values
				<% amount_registred = line_suspension.amount %>
				<% amount_paid = line_suspension.paid %>
				<tr class="line_data">
					<td>${ line_suspension.tax_code_id.code|entity }</td>
					<td>${ line_suspension.tax_code_id.name|entity }</td>
					<td class="amount"></td>
					<td class="amount"></td>
					<td class="amount">${ formatLang(amount_registred)|entity }</td>
					<td class="amount">${ formatLang(amount_paid)|entity }</td>
				</tr>
				## Sum Totals
				<% total_registred = total_registred + amount_registred %>
				<% total_paid = total_paid + amount_paid %>
        	%endfor
        	## Print Totals
        	<tr class="line_subtotal">
				<td></td>
				<td class="total amount">${ _('Total') }</td>
				<td class="subtotal amount"></td>
				<td class="subtotal amount"></td>
				<td class="subtotal amount">${ formatLang(total_registred)|entity }</td>
				<td class="subtotal amount">${ formatLang(total_paid)|entity }</td>
			</tr>
        </tbody>
        </table>
        %endif
        
        ## --------------
		## Sale - Suspension
		## --------------
		%if 'debit_vat_suspension_account_line_ids' in statement:
		<h4>${ _('Sale Suspension')} </h4>
		<table class="table table-condensed">
		<thead>
           	<tr>
               	<th style="width:12%;" class="text-left">${ _('Vat code')} </th>
               	<th style="width:37%;" class="text-left">${ _('Description')} </th>
               	<th style="width:15%;" class="amount"> </th>
               	<th style="width:12%;" class="amount"> </th>
               	## Columns Deductible / Undeductible only for purchase
               	<th style="width:12%;" class="amount">${ _('Amount Registred')} </th>
               	<th style="width:12%;" class="amount">${ _('Amount Paid')} </th>
        	</tr>
       	</thead>
       	<tbody>
       		## Reset Totals
       		<% total_registred = 0 %>
			<% total_paid = 0 %>
			%for line_suspension in statement.debit_vat_suspension_account_line_ids :
				## Prepare values
				<% amount_registred = line_suspension.amount %>
				<% amount_paid = line_suspension.paid %>
				## ... Debits in suspension are negative : in the report will be positive
				<% amount_registred = -1 * amount_registred %>
				<% amount_paid = -1 * amount_paid %>
				<tr class="line_data">
					<td>${ line_suspension.tax_code_id.code|entity }</td>
					<td>${ line_suspension.tax_code_id.name|entity }</td>
					<td class="amount"></td>
					<td class="amount"></td>
					<td class="amount">${ formatLang(amount_registred)|entity }</td>
					<td class="amount">${ formatLang(amount_paid)|entity }</td>
				</tr>
				## Sum Totals
				<% total_registred = total_registred + amount_registred %>
				<% total_paid = total_paid + amount_paid %>
        	%endfor
        	## Print Totals
        	<tr class="line_subtotal">
				<td></td>
				<td class="total amount">${ _('Total') }</td>
				<td class="subtotal amount"></td>
				<td class="subtotal amount"></td>
				<td class="subtotal amount">${ formatLang(total_registred)|entity }</td>
				<td class="subtotal amount">${ formatLang(total_paid)|entity }</td>
			</tr>
        </tbody>
        </table>
        %endif
        
    %endfor ## >> for periods
    
    	
    
	## ======================
	## Total Statement
	## ======================   
	<h3>${ _('Total Statement') }</h3>
	<table class="table table-condensed">
		## Reset Totals
       	<% total_statement = 0 %>
			
		##----------------------
		## Debit
		##----------------------
		<% vat_accounts = account_vat_amounts('debit', statement.debit_vat_account_line_ids) %>
		%for account_id in vat_accounts :
			<tr class="line_data">
	        	<td class="amount" style="width:50%;">${ _('Debit vat') }</td>
	        	<td class="amount" style="width:30%;">${ vat_accounts[account_id]['account_name'] }</td>
	            <td class="amount">${ formatLang(vat_accounts[account_id]['amount'])|entity }</td>
	        </tr>
	        ## Sum total
	        <% total_statement = total_statement + vat_accounts[account_id]['amount'] %>
		%endfor
		##----------------------
		## Credit
		##----------------------
		<% vat_accounts = account_vat_amounts('credit', statement.credit_vat_account_line_ids) %>
		%for account_id in vat_accounts :
			<tr class="line_data">
	        	<td class="amount" style="width:50%;">${ _('Credit vat') }</td>
	        	<td class="amount" style="width:30%;">${ vat_accounts[account_id]['account_name'] }</td>
	            <td class="amount">${ formatLang(vat_accounts[account_id]['amount'])|entity }</td>
	        </tr>
	        ## Sum total
	        <% total_statement = total_statement + ( -1 * vat_accounts[account_id]['amount']) %>
		%endfor
		##----------------------
		## Total
		##----------------------
		<tr class="line_subtotal">
	        	<td class="amount" style="width:50%;"></td>
	        	<td class="amount" style="width:30%;">${ _('Total Statement') }</td>
	            <td class="amount">${ formatLang(total_statement)|entity }</td>
	    </tr>
	</table>
	
	## ======================
	## Total to pay
	## ======================   
	<table class="table table-condensed">
		## Reset Totals
       	<% total_to_pay = total_statement %>
       	##----------------------
		## Previous Credit
		##----------------------
		<tr class="line_data">
	        	<td class="amount" style="width:80%;">${ _('Previous credit vat') }</td>
	            <td class="amount">${ formatLang(statement.previous_credit_vat_amount)|entity }</td>
	    </tr>
       	## Sum total
	    <% total_to_pay = total_to_pay - statement.previous_credit_vat_amount %>
	    ##----------------------
		## Previous Debit
		##----------------------
		<tr class="line_data">
	        	<td class="amount" style="width:80%;">${ _('Previous debit vat') }</td>
	            <td class="amount">${ formatLang(statement.previous_debit_vat_amount)|entity }</td>
	    </tr>
       	## Sum total
	    <% total_to_pay = total_to_pay + statement.previous_debit_vat_amount %>
	    ##----------------------
		## Other tot debit/credit
		##----------------------
		%for generic_vat in statement.generic_vat_account_line_ids :
			## Prepare description for generic line
			<% line_generic_description =  generic_vat.account_id.name %> 
			%if generic_vat.description:
				<% line_generic_description = generic_vat.description %>
			%endif
			<tr class="line_data">
	        	<td class="amount" style="width:80%;">${ line_generic_description }</td>
	            <td class="amount">${ formatLang(generic_vat.amount)|entity }</td>
	    	</tr>
       		## Sum total
	    	<% total_to_pay = total_to_pay + generic_vat.amount %>
	    %endfor
	    ##----------------------
		## Total to pay
		##----------------------
		%if total_to_pay >= 0:
			<tr class="line_subtotal">
	        	<td class="amount" style="width:80%;">${ _('Total To Pay') }</td>
	            <td class="amount">${ formatLang(total_to_pay)|entity }</td>
	    	</tr>
	    %else:
	    	<tr class="line_subtotal">
	        	<td class="amount" style="width:80%;">${ _('Total Credit') }</td>
	            <td class="amount">${ formatLang( (-1 * total_to_pay))|entity }</td>
	    	</tr>
	    %endif
	</table>
	
%endfor

</body>
</html>
