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