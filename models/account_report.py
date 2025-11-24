# from odoo import models, api, fields, _
# import logging

# _logger = logging.getLogger(__name__)


# class AccountReport(models.AbstractModel):
#     _inherit = 'account.report'

#     @api.model
#     def _get_store_financial_data(self, company_id, date_from, date_to):
#         '''
#         Get financial data for a specific store/company using account tags
        
#         :param company_id: ID of the company to get data for
#         :param date_from: Start date for the period
#         :param date_to: End date for the period
#         :return: Dictionary with categorized financial data
#         '''
        
#         store_data = {
#             'revenue_from_operations': 0,
#             'other_income': 0,
#             'total_income': 0,
#             'cost_of_materials': 0,
#             'purchases_of_stock': 0,
#             'changes_in_inventory': 0,
#             'employee_benefits': 0,
#             'direct_expenses': 0,
#             'finance_costs': 0,
#             'depreciation': 0,
#             'freight_charges': 0,
#             'other_expenses': 0,
#             'total_expenses': 0,
#             'profit_before_tax': 0,
#             'current_tax': 0,
#             'deferred_tax': 0,
#             'total_tax': 0,
#             'profit_after_tax': 0,
#         }
        
#         # Tag name patterns to match (case-insensitive)
#         tag_mapping = {
#             'revenue from operations': 'revenue_from_operations',
#             'other income': 'other_income',
#             'cost of materials': 'cost_of_materials',
#             'purchases of stock': 'purchases_of_stock',
#             'changes in inventory': 'changes_in_inventory',
#             'inventory changes': 'changes_in_inventory',
#             'employee benefits': 'employee_benefits',
#             'direct expenses': 'direct_expenses',
#             'finance costs': 'finance_costs',
#             'depreciation': 'depreciation',
#             'amortization': 'depreciation',
#             'freight': 'freight_charges',
#             'transport': 'freight_charges',
#             'current tax': 'current_tax',
#             'deferred tax': 'deferred_tax',
#         }
        
#         # Query to get balances grouped by account tags
#         # Only for the SPECIFIC company provided
#         query = '''
#             SELECT 
#                 aat.name as tag_name,
#                 aa.account_type,
#                 aa.code as account_code,
#                 aa.name as account_name,
#                 SUM(aml.balance) as balance,
#                 SUM(aml.debit) as total_debit,
#                 SUM(aml.credit) as total_credit
#             FROM account_move_line aml
#             JOIN account_account aa ON aa.id = aml.account_id
#             JOIN account_move am ON am.id = aml.move_id
#             LEFT JOIN account_account_tag_account_account_rel aatar ON aatar.account_account_id = aa.id
#             LEFT JOIN account_account_tag aat ON aat.id = aatar.account_account_tag_id
#             WHERE 
#                 am.state = 'posted'
#                 AND am.company_id = %s
#                 AND am.date >= %s
#                 AND am.date <= %s
#                 AND aa.account_type IN ('income', 'income_other', 'expense', 'expense_depreciation', 'expense_direct_cost')
#             GROUP BY aat.name, aa.account_type, aa.code, aa.name
#             HAVING SUM(aml.balance) != 0
#             ORDER BY aa.code
#         '''
        
#         self.env.cr.execute(query, (company_id, date_from, date_to))
#         results = self.env.cr.dictfetchall()
        
#         company = self.env['res.company'].browse(company_id)
#         _logger.info(f"Processing financial data for company: {company.name} (ID: {company_id})")
#         _logger.info(f"Period: {date_from} to {date_to}")
#         _logger.info(f"Found {len(results)} account records with balances")
        
#         for record in results:
#             balance = record['balance']
#             tag_name = (record.get('tag_name') or '').lower()
#             account_type = record['account_type']
#             account_code = record.get('account_code', '')
#             account_name = record.get('account_name', '')
            
#             # Income accounts have CREDIT balance (negative in Odoo)
#             # Expense accounts have DEBIT balance (positive in Odoo)
#             # We need absolute values for reporting
#             amount = abs(balance)
            
#             # Match tag to category
#             matched = False
#             if tag_name:
#                 for tag_pattern, field_name in tag_mapping.items():
#                     if tag_pattern in tag_name:
#                         store_data[field_name] += amount
#                         matched = True
#                         _logger.debug(f"[{account_code}] {account_name}: {amount} → {field_name} (via tag: {tag_name})")
#                         break
            
#             # Fallback: categorize by account type if no tag matched
#             if not matched:
#                 if account_type == 'income':
#                     store_data['revenue_from_operations'] += amount
#                     _logger.debug(f"[{account_code}] {account_name}: {amount} → revenue_from_operations (untagged income)")
#                 elif account_type == 'income_other':
#                     store_data['other_income'] += amount
#                     _logger.debug(f"[{account_code}] {account_name}: {amount} → other_income (untagged)")
#                 elif account_type == 'expense_depreciation':
#                     store_data['depreciation'] += amount
#                     _logger.debug(f"[{account_code}] {account_name}: {amount} → depreciation (by type)")
#                 elif account_type == 'expense_direct_cost':
#                     store_data['direct_expenses'] += amount
#                     _logger.debug(f"[{account_code}] {account_name}: {amount} → direct_expenses (by type)")
#                 elif account_type == 'expense':
#                     store_data['other_expenses'] += amount
#                     _logger.debug(f"[{account_code}] {account_name}: {amount} → other_expenses (untagged)")
        
#         # Calculate totals
#         store_data['total_income'] = (
#             store_data['revenue_from_operations'] + 
#             store_data['other_income']
#         )
        
#         store_data['total_expenses'] = sum([
#             store_data['cost_of_materials'],
#             store_data['purchases_of_stock'],
#             store_data['changes_in_inventory'],
#             store_data['employee_benefits'],
#             store_data['direct_expenses'],
#             store_data['finance_costs'],
#             store_data['depreciation'],
#             store_data['freight_charges'],
#             store_data['other_expenses']
#         ])
        
#         store_data['profit_before_tax'] = (
#             store_data['total_income'] - 
#             store_data['total_expenses']
#         )
        
#         store_data['total_tax'] = (
#             store_data['current_tax'] + 
#             store_data['deferred_tax']
#         )
        
#         store_data['profit_after_tax'] = (
#             store_data['profit_before_tax'] - 
#             store_data['total_tax']
#         )
        
#         _logger.info(f"=== FINANCIAL SUMMARY for {company.name} ===")
#         _logger.info(f"Total Income: {store_data['total_income']:,.2f}")
#         _logger.info(f"  - Revenue from Operations: {store_data['revenue_from_operations']:,.2f}")
#         _logger.info(f"  - Other Income: {store_data['other_income']:,.2f}")
#         _logger.info(f"Total Expenses: {store_data['total_expenses']:,.2f}")
#         _logger.info(f"Profit Before Tax: {store_data['profit_before_tax']:,.2f}")
#         _logger.info(f"Total Tax: {store_data['total_tax']:,.2f}")
#         _logger.info(f"Profit After Tax: {store_data['profit_after_tax']:,.2f}")
#         _logger.info(f"=========================================")
        
#         return store_data
    
    
#     @api.model
#     def _get_all_stores_financial_data(self, date_from, date_to, company_ids=None):
#         '''
#         Get financial data for multiple companies/stores
        
#         :param date_from: Start date for the period
#         :param date_to: End date for the period
#         :param company_ids: List of company IDs (if None, gets all companies user has access to)
#         :return: Dictionary with company_id as key and financial data as value
#         '''
        
#         if company_ids is None:
#             # Get all companies the user has access to
#             company_ids = self.env['res.company'].search([]).ids
        
#         all_stores_data = {}
        
#         for company_id in company_ids:
#             company = self.env['res.company'].browse(company_id)
#             _logger.info(f"Fetching data for company: {company.name}")
            
#             store_data = self._get_store_financial_data(company_id, date_from, date_to)
#             all_stores_data[company_id] = {
#                 'company_name': company.name,
#                 'data': store_data
#             }
        
#         return all_stores_data
from odoo import models, api, fields, _
import logging

_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _get_store_financial_data(self, company_id, date_from, date_to):
        '''Get financial data for a specific store/company'''
        
        store_data = {
            'revenue_from_operations': 0,
            'other_income': 0,
            'total_income': 0,
            'cost_of_materials': 0,
            'purchases_of_stock': 0,
            'changes_in_inventory': 0,
            'employee_benefits': 0,
            'direct_expenses': 0,
            'finance_costs': 0,
            'depreciation': 0,
            'freight_charges': 0,
            'other_expenses': 0,
            'total_expenses': 0,
            'profit_before_tax': 0,
            'current_tax': 0,
            'deferred_tax': 0,
            'total_tax': 0,
            'profit_after_tax': 0,
        }
        
        # --- Income Query ---
        income_query = '''
            SELECT 
                aa.account_type,
                aa.name,
                SUM(aml.balance) as balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE 
                am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type IN ('income', 'income_other')
            GROUP BY aa.account_type, aa.name
        '''
        
        self.env.cr.execute(income_query, (company_id, date_from, date_to))
        income_results = self.env.cr.dictfetchall()
        
        for record in income_results:
            balance = abs(record['balance'])
            name_lower = str(record['name'] or '').lower()
            
            if record['account_type'] == 'income':
                store_data['revenue_from_operations'] += balance
            else:
                store_data['other_income'] += balance
        
        store_data['total_income'] = store_data['revenue_from_operations'] + store_data['other_income']
        
        # --- Expense Query ---
        expense_query = '''
            SELECT 
                aa.account_type,
                aa.name,
                SUM(aml.balance) as balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE 
                am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type LIKE 'expense%%'
            GROUP BY aa.account_type, aa.name
        '''
        
        self.env.cr.execute(expense_query, (company_id, date_from, date_to))
        expense_results = self.env.cr.dictfetchall()
        
        for record in expense_results:
            balance = abs(record['balance'])
            name_lower = str(record['name'] or '').lower()
            
            # Categorize expenses by keywords
            if any(keyword in name_lower for keyword in ['material', 'raw material', 'cogs']):
                store_data['cost_of_materials'] += balance
            elif any(keyword in name_lower for keyword in ['purchase', 'stock', 'merchandise']):
                store_data['purchases_of_stock'] += balance
            elif any(keyword in name_lower for keyword in ['inventory', 'stock variation']):
                store_data['changes_in_inventory'] += balance
            elif any(keyword in name_lower for keyword in ['salary', 'wage', 'employee', 'staff', 'payroll']):
                store_data['employee_benefits'] += balance
            elif any(keyword in name_lower for keyword in ['interest', 'finance', 'bank charge']):
                store_data['finance_costs'] += balance
            elif 'depreciation' in name_lower or 'amortisation' in name_lower or 'amortization' in name_lower:
                store_data['depreciation'] += balance
            elif any(keyword in name_lower for keyword in ['freight', 'transport', 'shipping', 'delivery']):
                store_data['freight_charges'] += balance
            elif any(keyword in name_lower for keyword in ['direct', 'manufacturing']):
                store_data['direct_expenses'] += balance
            else:
                store_data['other_expenses'] += balance

        store_data['total_expenses'] = sum([
            store_data['cost_of_materials'],
            store_data['purchases_of_stock'],
            store_data['changes_in_inventory'],
            store_data['employee_benefits'],
            store_data['direct_expenses'],
            store_data['finance_costs'],
            store_data['depreciation'],
            store_data['freight_charges'],
            store_data['other_expenses']
        ])
        
        store_data['profit_before_tax'] = store_data['total_income'] - store_data['total_expenses']
        
        # --- Tax Query ---
        tax_query = '''
            SELECT SUM(aml.balance) as tax_amount
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE 
                am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
                AND aa.account_type IN ('expense', 'expense_depreciation', 'expense_direct_cost')
                AND (CAST(aa.name AS TEXT) ILIKE '%%tax expense%%' OR CAST(aa.name AS TEXT) ILIKE '%%income tax%%')
        '''
        
        self.env.cr.execute(tax_query, (company_id, date_from, date_to))
        tax_result = self.env.cr.fetchone()
        
        if tax_result and tax_result[0]:
            store_data['current_tax'] = abs(tax_result[0])
        
        store_data['total_tax'] = store_data['current_tax'] + store_data['deferred_tax']
        store_data['profit_after_tax'] = store_data['profit_before_tax'] - store_data['total_tax']
        
        return store_data