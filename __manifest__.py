{
    'name': 'Indian GST Invoice & Tax Invoice Template',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Custom Indian GST compliant invoice templates for Customer Invoices and Vendor Bills',
    'description': """
        Custom Invoice Templates for Indian GST
        =======================================
        * GST compliant Tax Invoice format for Vendor Bills
        * GST compliant Customer Invoice format
        * E-invoice QR code support
        * HSN/SAC code display with summary
        * Detailed tax breakdown (IGST/CGST/SGST)
        * IRN and acknowledgment details
        * Amount in words (Indian format)
        * Company declaration and authorized signatory
        * Professional layout matching Indian tax requirements
        
        This module provides comprehensive invoice templates that comply with
        Indian GST regulations for both incoming (vendor bills) and outgoing
        (customer invoices) transactions.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    "post_init_hook": "post_init_hook",
    'depends': [
        'account',
        'l10n_in',
        'l10n_in_edi',
        'account_reports'
    ],
    'data': [
        'data/create_store_accounts.py'
        'data/ir_sequence.xml', 

        # 'data/account_tags.xml', 
        'views/report_invoice.xml',
        'views/multi_store_pl_wizard_views.xml',
        'views/report_multi_store_pl_template.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}