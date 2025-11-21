from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import xlsxwriter
from io import BytesIO
import base64
import logging

_logger = logging.getLogger(__name__)


class MultiStorePLWizard(models.TransientModel):
    _name = 'multi.store.pl.wizard'
    _description = 'Multi-Store P&L Report Wizard'

    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=lambda self: fields.Date.today().replace(month=1, day=1)
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.today
    )
    company_ids = fields.Many2many(
        'res.company',
        string='Stores/Companies',
        required=True,
        default=lambda self: self.env.companies.ids
    )
    cin_number = fields.Char(
        string='CIN Number',
        help='Corporate Identification Number'
    )
    
    def action_generate_report(self):
        '''Generate and download Excel report'''
        self.ensure_one()
        
        if not self.company_ids:
            raise UserError(_('Please select at least one store/company.'))
        
        # Generate Excel file
        excel_file = self._generate_excel_report()
        
        # Create attachment
        filename = 'Multi_Store_PL_Report_%s_to_%s.xlsx' % (
            self.date_from.strftime('%Y%m%d'),
            self.date_to.strftime('%Y%m%d')
        )
        
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': excel_file,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
    
    def _generate_excel_report(self):
        '''Generate Excel file with multi-store P&L'''
        
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('P&L Statement')
        
        # Define formats
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#D3D3D3',
            'text_wrap': True
        })
        
        section_format = workbook.add_format({
            'bold': True,
            'align': 'left',
            'border': 1,
            'bg_color': '#E8E8E8'
        })
        
        text_format = workbook.add_format({
            'align': 'left',
            'border': 1,
            'text_wrap': True
        })
        
        number_format = workbook.add_format({
            'align': 'right',
            'border': 1,
            'num_format': '#,##0.00'
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'align': 'right',
            'border': 1,
            'num_format': '#,##0.00',
            'bg_color': '#E8E8E8'
        })
        
        # Set column widths
        worksheet.set_column(0, 0, 50)  # Particulars column
        worksheet.set_column(1, len(self.company_ids) + 1, 15)  # Data columns
        
        # Collect data for all stores
        stores_data = {}
        company_names = []
        
        for company in self.company_ids:
            company_names.append(company.name)
            stores_data[company.name] = self.env['account.report']._get_store_financial_data(
                company.id,
                self.date_from,
                self.date_to
            )
        
        # Calculate totals
        totals = self._calculate_totals(stores_data)
        
        # Write report
        row = 0
        
        # Title
        cin = self.cin_number or self.env.company.company_registry or 'CIN-XXXXXXXXX'
        worksheet.merge_range(
            row, 0, row, len(company_names) + 1,
            '%s%s' % (cin, self.env.company.name),
            title_format
        )
        row += 1
        
        # Subtitle
        period_str = 'STATEMENT OF PROFIT AND LOSS ACCOUNT FOR THE YEAR ENDED %s' % self.date_to.strftime('%dst %B %Y')
        worksheet.merge_range(
            row, 0, row, len(company_names) + 1,
            period_str,
            title_format
        )
        row += 1
        
        # Empty row
        row += 1
        
        # Column headers
        worksheet.write(row, 0, 'Particulars', header_format)
        col = 1
        for company_name in company_names:
            worksheet.write(row, col, company_name, header_format)
            col += 1
        worksheet.write(row, col, 'For the year ended\\n%s\\nRs.' % self.date_to.strftime('%dst %B, %Y'), header_format)
        row += 1
        
        # INCOME Section
        worksheet.write(row, 0, 'INCOME', section_format)
        row += 1
        
        # Revenue from operations
        self._write_data_row(worksheet, row, 'I    Revenue from operations', 
                           stores_data, company_names, 'revenue_from_operations', totals,
                           text_format, number_format, total_format)
        row += 1
        
        # Other Income
        self._write_data_row(worksheet, row, 'II   Other Income',
                           stores_data, company_names, 'other_income', totals,
                           text_format, number_format, total_format)
        row += 1
        
        # Total Income
        self._write_data_row(worksheet, row, 'III  TOTAL INCOME (I + II)',
                           stores_data, company_names, 'total_income', totals,
                           section_format, total_format, total_format)
        row += 1
        
        # Empty row
        row += 1
        
        # EXPENSES Section
        worksheet.write(row, 0, 'IV   EXPENSES', section_format)
        row += 1
        
        expense_items = [
            ('(a) Cost of materials consumed', 'cost_of_materials'),
            ('(b) Purchases of Stock in Trade', 'purchases_of_stock'),
            ('(c) Changes in inventories of finished goods', 'changes_in_inventory'),
            ('(d) Employee benefits expenses', 'employee_benefits'),
            ('(e) Direct Expenses', 'direct_expenses'),
            ('(f) Finance costs/benefits expenses', 'finance_costs'),
            ('(g) Depreciation and amortisation expenses', 'depreciation'),
            ('(h) Freight Charges', 'freight_charges'),
            ('(i) Other expenses', 'other_expenses'),
        ]
        
        for label, key in expense_items:
            self._write_data_row(worksheet, row, label,
                               stores_data, company_names, key, totals,
                               text_format, number_format, total_format)
            row += 1
        
        # Total Expenses
        self._write_data_row(worksheet, row, 'TOTAL EXPENSES',
                           stores_data, company_names, 'total_expenses', totals,
                           section_format, total_format, total_format)
        row += 1
        
        # Empty row
        row += 1
        
        # Profit calculations
        self._write_data_row(worksheet, row, 'V    Profit before exceptional and extraordinary items and tax (III-IV)',
                           stores_data, company_names, 'profit_before_tax', totals,
                           text_format, number_format, total_format)
        row += 1
        
        self._write_data_row(worksheet, row, 'VI   Exceptional items',
                           stores_data, company_names, None, totals,
                           text_format, number_format, total_format)
        row += 1
        
        self._write_data_row(worksheet, row, 'VII  Profit before extraordinary items and tax (V - VI)',
                           stores_data, company_names, 'profit_before_tax', totals,
                           text_format, number_format, total_format)
        row += 1
        
        self._write_data_row(worksheet, row, 'VIII Extraordinary Items',
                           stores_data, company_names, None, totals,
                           text_format, number_format, total_format)
        row += 1
        
        self._write_data_row(worksheet, row, 'IX   Profit before tax (VII-VIII)',
                           stores_data, company_names, 'profit_before_tax', totals,
                           text_format, number_format, total_format)
        row += 1
        
        # Tax Expense
        worksheet.write(row, 0, 'X    Tax Expense:', section_format)
        row += 1
        
        self._write_data_row(worksheet, row, '     (a) Current tax expense',
                           stores_data, company_names, 'current_tax', totals,
                           text_format, number_format, total_format)
        row += 1
        
        self._write_data_row(worksheet, row, '     (b) Deferred tax',
                           stores_data, company_names, 'deferred_tax', totals,
                           text_format, number_format, total_format)
        row += 1
        
        # Profit after tax
        self._write_data_row(worksheet, row, 'XI   Profit / (Loss) from continuing operations (IX-X)',
                           stores_data, company_names, 'profit_after_tax', totals,
                           section_format, total_format, total_format)
        row += 1
        
        # Close workbook
        workbook.close()
        output.seek(0)
        
        return base64.b64encode(output.read())
    
    def _write_data_row(self, worksheet, row, label, stores_data, company_names, 
                       data_key, totals, label_format, number_format, total_format):
        '''Write a data row to the worksheet'''
        worksheet.write(row, 0, label, label_format)
        
        col = 1
        for company_name in company_names:
            if data_key and data_key in stores_data[company_name]:
                value = stores_data[company_name][data_key]
            else:
                value = 0
            worksheet.write(row, col, value, number_format)
            col += 1
        
        # Write total
        if data_key and data_key in totals:
            total_value = totals[data_key]
        else:
            total_value = 0
        worksheet.write(row, col, total_value, total_format)
    
    def _calculate_totals(self, stores_data):
        '''Calculate totals across all stores'''
        totals = {}
        
        if not stores_data:
            return totals
        
        # Get all keys from first store
        first_store = list(stores_data.values())[0]
        
        for key in first_store.keys():
            totals[key] = sum(store_data.get(key, 0) for store_data in stores_data.values())
        
        return totals
