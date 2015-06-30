<html>
<head>
    <style type="text/css">
        ${css}
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

h4 {
	margin-bottom: 2px;
}
.section {
	background-color: lightgrey;
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
    <h2>Liquidazione IVA Annuale - ${ year() }</h2>
    ## ======================
	## Tax Details 
	## ======================  
    <% total = {'credit': 0.0, 'debit': 0.0} %>
    %for type in ('credit', 'debit'):
        <h3 class="section">${ type=='credit' and 'Acquisti' or 'Vendite' }</h3>
        <table class="table table-condensed">
            <thead>
                <tr>
                    <th style="width:12%;" class="text-left">${ _('Cod IVA')} </th>
               		<th style="width:37%;" class="text-left">${ _('Descrizione')} </th>
               		<th style="width:15%;" class="text-right">${ _('Imponibile')}</th>
               		<th style="width:12%;" class="text-right">${ _('Imposta')}</th>
               		## Columns Deductible / Undeductible only for purchase
               		%if type == 'credit':
               			<th style="width:12%;" class="text-right">${ _('Detraibile')} </th>
               			<th style="width:12%;" class="text-right">${ _('Indetraibile')}  </th>
               		%else:
               			<th style="width:12%;" class="text-right"></th>
               			<th style="width:12%;" class="text-right"> </th>
               		%endif
                </tr>
            </thead>
            <tbody>
            
            	## Reset Totals
       			<% total_vat = 0 %>
				<% total_base = 0 %>
				<% total_vat_deductible = 0 %>
				<% total_vat_undeductible = 0 %>
                
                <% taxes = tax_codes_amounts(type) %>
                %for tax,vals in taxes.items():
                
                ## Prepare Vals
                <% tax_code_code = vals['code'] %>
                <% tax_code_base = vals['base'] %>
				<% tax_code_vat = vals['vat'] %>
				<% tax_code_vat_deductible = vals['vat_deductible'] %>
				<% tax_code_vat_undeductible = vals['vat_undeductible'] %>
				## ... Credits are negative : in the report will be positive
				%if type == 'credit':
					<% tax_code_base = -1 * tax_code_base %>
					<% tax_code_vat = -1 * tax_code_vat %>
					<% tax_code_vat_deductible = -1 * tax_code_vat_deductible %>
					<% tax_code_vat_undeductible = -1 * tax_code_vat_undeductible %>
				%endif
                
				## Print values
                <tr class="line_data">
                    <td>${ tax_code_code }</td>
                    <td>${ tax }</td>
                    <td class="amount">${ formatLang(tax_code_base)|entity }</td>
                    <td class="amount">${ formatLang(tax_code_vat)|entity }</td>
                    ## Columns Deductible / Undeductible only for purchase
                    %if type == 'credit':
                    	<td style="width:12%;" class="text-right">${ formatLang(tax_code_vat_deductible)|entity }</td>
               			<td style="width:12%;" class="text-right">${ formatLang(tax_code_vat_undeductible)|entity } </td>
                    %else:
                    	<td style="width:12%;" class="text-right"> </td>
               			<td style="width:12%;" class="text-right"> </td>
                    %endif
                </tr>
                <% total_base += tax_code_base %>
                <% total_vat += tax_code_vat %>
                %if type == 'credit':
                	<% total_vat_deductible += tax_code_vat_deductible %>
                	<% total_vat_undeductible += tax_code_vat_undeductible %>
                	<% total[type] += tax_code_vat_deductible %>
                %else:
                	<% total[type] += tax_code_vat %>
                %endif
                
                %endfor
                
        		## Print Totals
                <tr class="line_subtotal">
                    <td></td>
                    <td class="total amount">${ _('Totale') }</td>
                    <td class="total amount">${ formatLang(total_base)|entity }</td>
                    <td class="total amount">${ formatLang(total_vat)|entity }</td>
                    %if type == 'credit':
                    	<td class="subtotal amount">${ formatLang(total_vat_deductible)|entity }</td>
						<td class="subtotal amount">${ formatLang(total_vat_undeductible)|entity }</td>
					%endif
                </tr>
            </tbody>
        </table>
    %endfor
    
    ## ======================
	## Total Statement
	## ======================   
    <h3 class="section">${ 'Totali'}</h3>
    <% total_end_vat_period = total['debit'] - total['credit'] %>
    ##<table class="table table-bordered table-condensed" style="margin-left:20%;width:80%;">
    <table class="table table-bordered table-condensed" >
        <tr class="line_data">
            <td style="width:80%;" class="amount" colspan="3">Iva Debito</td>
            <td style="width:20%;" class="amount">${ formatLang(total['debit'])|entity }</td>
        </tr>
        <tr class="line_data">
            <td colspan="3" class="amount">Iva Credito</td>
            <td class="amount">${ formatLang(total['credit'])|entity }</td>
        </tr>
        ##----------------------------------
        ## Altra iva x compensazioni
        ##----------------------------------
        <% generic_lines = lines_generic_amounts() %>
        <% total_generic = 0.0 %>
        
        %if generic_lines:
        	<tr>
        		<td colspan="3">Altra IVA per compensazioni o interessi</td>
            	<td class="amount"></td>
        	</tr>	
        %endif
        %for gen_data in generic_lines:
        	<tr class="line_data">
        		<td>${gen_data['period'] |entity } </td>
        		<td style="width:200px;">${gen_data['description'] |entity } - ${gen_data['account_name'] |entity }</td>
            	<td class="amount">${ formatLang(gen_data['amount']) |entity } </td>
            	<td></td>
        	</tr>
        	<% total_generic += gen_data['amount'] %>
        %endfor
        
        %if total_generic:
        	<tr class="line_data">
        		<td class="amount"> </td>
        		<td colspan="2" class="amount"> Totale Altra IVA per compensazioni o interessi</td>
            	<td  class="amount">${ formatLang(total_generic) |entity } </td>
        	</tr>	
        %endif
        
        
        <% total_end_vat_period = total_end_vat_period + total_generic %>
        ##----------------------------------
        ## Iva a credito/debito del periodo
        ##----------------------------------
        <tr class="line_subtotal">
        %if total_end_vat_period > 0:
            <td class="total amount" colspan="3" >IVA del Periodo Da Versare</td>
        %else:
        	<td class="total amount" colspan="3" >IVA del Periodo A Credito</td>
        %endif
            <td class="total amount">${ formatLang(total_end_vat_period)|entity }</td>
        </tr>
        
    </table>
    ##
    ## Versamenti e altri crediti e debiti
    ##
    % if amount_paid() > 0:
    <% total_to_pay = total_end_vat_period -  amount_paid() %>
    <table class="table table-bordered table-condensed" style="margin-left:50%;width:50%;">
        <tr class="line_subtotal">
            <td style="width:50%;">Iva Versata</td>
            <td style="width:50%;" class="amount">${ formatLang(amount_paid()) |entity } </td>
        </tr>
        <tr class="line_subtotal">
        	%if total_to_pay > 0:
            	<td class="total">Totale IVA Da Versare</td>
        	%else:
        		<td class="total">Totale IVA A Credito</td>
        	%endif
            <td style="width:50%;" class="total amount">${ formatLang(total_to_pay)|entity } </td>
        </tr>
    </table>
    %endif
</body>
</html>
