from odoo import models, api, fields, _
import logging

_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    @api.model
    def _get_store_financial_data(self, company_id, date_from, date_to):
        '''Get financial data for a specific store/company using account tags'''
        
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
        
        # Tag name patterns to match (case-insensitive)
        tag_mapping = {
            'revenue from operations': 'revenue_from_operations',
            'other income': 'other_income',
            'cost of materials': 'cost_of_materials',
            'purchases of stock': 'purchases_of_stock',
            'changes in inventory': 'changes_in_inventory',
            'inventory changes': 'changes_in_inventory',
            'employee benefits': 'employee_benefits',
            'direct expenses': 'direct_expenses',
            'finance costs': 'finance_costs',
            'depreciation': 'depreciation',
            'amortization': 'depreciation',
            'freight': 'freight_charges',
            'transport': 'freight_charges',
            'current tax': 'current_tax',
            'deferred tax': 'deferred_tax',
        }
        
        # Query to get balances grouped by account tags
        query = '''
            SELECT 
                aat.name as tag_name,
                aa.account_type,
                SUM(aml.balance) as balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            LEFT JOIN account_account_tag_account_account_rel aatar ON aatar.account_account_id = aa.id
            LEFT JOIN account_account_tag aat ON aat.id = aatar.account_account_tag_id
            WHERE 
                am.state = 'posted'
                AND am.company_id = %s
                AND am.date >= %s
                AND am.date <= %s
            GROUP BY aat.name, aa.account_type
            HAVING SUM(aml.balance) != 0
        '''
        
        self.env.cr.execute(query, (company_id, date_from, date_to))
        results = self.env.cr.dictfetchall()
        
        _logger.info(f"Financial data query returned {len(results)} records for company {company_id}")
        
        for record in results:
            balance = record['balance']
            tag_name = (record.get('tag_name') or '').lower()
            account_type = record['account_type']
            
            # For income accounts, balance is negative (credit), so we negate it
            # For expense accounts, balance is positive (debit), so we use absolute value
            if account_type in ('income', 'income_other'):
                amount = abs(balance)  # Income is normally credit (negative)
            else:
                amount = abs(balance)  # Expenses are normally debit (positive)
            
            # Match tag to category
            matched = False
            if tag_name:
                for tag_pattern, field_name in tag_mapping.items():
                    if tag_pattern in tag_name:
                        store_data[field_name] += amount
                        matched = True
                        _logger.debug(f"Matched tag '{tag_name}' to {field_name}: {amount}")
                        break
            
            # Fallback: categorize by account type if no tag matched
            if not matched:
                if account_type == 'income':
                    store_data['revenue_from_operations'] += amount
                    _logger.debug(f"Untagged income account: {amount}")
                elif account_type == 'income_other':
                    store_data['other_income'] += amount
                    _logger.debug(f"Untagged other income: {amount}")
                elif account_type in ('expense', 'expense_depreciation', 'expense_direct_cost'):
                    store_data['other_expenses'] += amount
                    _logger.debug(f"Untagged expense: {amount}")
        
        # Calculate totals
        store_data['total_income'] = (
            store_data['revenue_from_operations'] + 
            store_data['other_income']
        )
        
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
        
        store_data['profit_before_tax'] = (
            store_data['total_income'] - 
            store_data['total_expenses']
        )
        
        store_data['total_tax'] = (
            store_data['current_tax'] + 
            store_data['deferred_tax']
        )
        
        store_data['profit_after_tax'] = (
            store_data['profit_before_tax'] - 
            store_data['total_tax']
        )
        
        _logger.info(f"Financial Summary - Income: {store_data['total_income']}, "
                    f"Expenses: {store_data['total_expenses']}, "
                    f"Profit: {store_data['profit_after_tax']}")
        
        return store_data
# from odoo import models, api, fields, _
# import logging

# _logger = logging.getLogger(__name__)


# class AccountReport(models.AbstractModel):
#     _inherit = 'account.report'

#     @api.model
#     def _get_store_financial_data(self, company_id, date_from, date_to):
#         '''Get financial data for a specific store/company'''
        
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
        
#         # --- Income Query ---
#         income_query = '''
#             SELECT 
#                 aa.account_type,
#                 aa.name,
#                 SUM(aml.balance) as balance
#             FROM account_move_line aml
#             JOIN account_account aa ON aa.id = aml.account_id
#             JOIN account_move am ON am.id = aml.move_id
#             WHERE 
#                 am.state = 'posted'
#                 AND am.company_id = %s
#                 AND am.date >= %s
#                 AND am.date <= %s
#                 AND aa.account_type IN ('income', 'income_other')
#             GROUP BY aa.account_type, aa.name
#         '''
        
#         self.env.cr.execute(income_query, (company_id, date_from, date_to))
#         income_results = self.env.cr.dictfetchall()
        
#         for record in income_results:
#             balance = abs(record['balance'])
#             name_lower = str(record['name'] or '').lower()
            
#             if record['account_type'] == 'income':
#                 store_data['revenue_from_operations'] += balance
#             else:
#                 store_data['other_income'] += balance
        
#         store_data['total_income'] = store_data['revenue_from_operations'] + store_data['other_income']
        
#         # --- Expense Query ---
#         expense_query = '''
#             SELECT 
#                 aa.account_type,
#                 aa.name,
#                 SUM(aml.balance) as balance
#             FROM account_move_line aml
#             JOIN account_account aa ON aa.id = aml.account_id
#             JOIN account_move am ON am.id = aml.move_id
#             WHERE 
#                 am.state = 'posted'
#                 AND am.company_id = %s
#                 AND am.date >= %s
#                 AND am.date <= %s
#                 AND aa.account_type LIKE 'expense%%'
#             GROUP BY aa.account_type, aa.name
#         '''
        
#         self.env.cr.execute(expense_query, (company_id, date_from, date_to))
#         expense_results = self.env.cr.dictfetchall()
        
#         for record in expense_results:
#             balance = abs(record['balance'])
#             name_lower = str(record['name'] or '').lower()
            
#             # Categorize expenses by keywords
#             if any(keyword in name_lower for keyword in ['material', 'raw material', 'cogs']):
#                 store_data['cost_of_materials'] += balance
#             elif any(keyword in name_lower for keyword in ['purchase', 'stock', 'merchandise']):
#                 store_data['purchases_of_stock'] += balance
#             elif any(keyword in name_lower for keyword in ['inventory', 'stock variation']):
#                 store_data['changes_in_inventory'] += balance
#             elif any(keyword in name_lower for keyword in ['salary', 'wage', 'employee', 'staff', 'payroll']):
#                 store_data['employee_benefits'] += balance
#             elif any(keyword in name_lower for keyword in ['interest', 'finance', 'bank charge']):
#                 store_data['finance_costs'] += balance
#             elif 'depreciation' in name_lower or 'amortisation' in name_lower or 'amortization' in name_lower:
#                 store_data['depreciation'] += balance
#             elif any(keyword in name_lower for keyword in ['freight', 'transport', 'shipping', 'delivery']):
#                 store_data['freight_charges'] += balance
#             elif any(keyword in name_lower for keyword in ['direct', 'manufacturing']):
#                 store_data['direct_expenses'] += balance
#             else:
#                 store_data['other_expenses'] += balance

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
        
#         store_data['profit_before_tax'] = store_data['total_income'] - store_data['total_expenses']
        
#         # --- Tax Query ---
#         tax_query = '''
#             SELECT SUM(aml.balance) as tax_amount
#             FROM account_move_line aml
#             JOIN account_account aa ON aa.id = aml.account_id
#             JOIN account_move am ON am.id = aml.move_id
#             WHERE 
#                 am.state = 'posted'
#                 AND am.company_id = %s
#                 AND am.date >= %s
#                 AND am.date <= %s
#                 AND aa.account_type IN ('expense', 'expense_depreciation', 'expense_direct_cost')
#                 AND (CAST(aa.name AS TEXT) ILIKE '%%tax expense%%' OR CAST(aa.name AS TEXT) ILIKE '%%income tax%%')
#         '''
        
#         self.env.cr.execute(tax_query, (company_id, date_from, date_to))
#         tax_result = self.env.cr.fetchone()
        
#         if tax_result and tax_result[0]:
#             store_data['current_tax'] = abs(tax_result[0])
        
#         store_data['total_tax'] = store_data['current_tax'] + store_data['deferred_tax']
#         store_data['profit_after_tax'] = store_data['profit_before_tax'] - store_data['total_tax']
        
#         return store_data