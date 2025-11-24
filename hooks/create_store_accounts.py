# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def create_store_accounts(env):
    _logger.info("🚀 Starting Store Account Creation Process")

    # -----------------------------------------------------------
    # 1. Define Stores (Sub-Companies)
    # -----------------------------------------------------------
    store_names = [
        "Store-1 Downtown Location",
        "Store 2 - Northside Location",
        "Store 3 - Eastside Location",
        "Store 4 - Westside Location",
        "Store 6 - Airport Location",
        "Store 5 - Southside Location",
        "Store 7 - Mall Location",
        "Store 8 - Suburb Location",
        "Store 9 - Business District",
        "Store 10 - Warehouse Center",
    ]

    # Search for sub-companies (companies with a parent)
    companies = env["res.company"].search([
        ("name", "in", store_names),
        ("parent_id", "!=", False)  # Ensure they are sub-companies
    ])
    
    if not companies:
        _logger.warning("❌ No sub-companies found with the specified names. Checking all companies...")
        # Fallback: search without parent_id filter
        companies = env["res.company"].search([("name", "in", store_names)])
        if not companies:
            _logger.error("❌ No companies found at all. Please check company names.")
            return
    
    _logger.info(f"🔎 Found {len(companies)} sub-companies for account creation:")
    for company in companies:
        parent_info = f" (Parent: {company.parent_id.name})" if company.parent_id else " (No Parent)"
        _logger.info(f"   - {company.name}{parent_info}")

    # -----------------------------------------------------------
    # 2. Account Definitions
    # -----------------------------------------------------------
    income_accounts = {
        "Revenue from Operations": "income",
        "Other Income": "income_other",
    }

    expense_accounts = {
        "Cost of Material Consumed": "expense",
        "Purchase of Stock in Trade": "expense",
        "Changes in Inventories of finished Goods": "expense",
        "Employee Benefits Expenses": "expense",
        "Direct Expenses": "expense",
        "Finance Costs": "expense",
        "Depreciation and Amortisation Expenses": "expense",
        "Freight Charges": "expense",
        "Other Expenses": "expense",
    }

    tax_accounts = {
        "Current Tax Expense": "expense",
        "Deffered Tax": "expense",
        "Profit/Loss from Continuing Operations": "expense",
        "Profit/Loss from Discontinuing Operations": "expense",
        "Profit/Loss from Discontinuing Operations(After-Tax)": "expense",
    }

    earning_accounts = {
        "Basic": "income",
        "Diluted": "income",
    }

    all_accounts = {}
    all_accounts.update(income_accounts)
    all_accounts.update(expense_accounts)
    all_accounts.update(tax_accounts)
    all_accounts.update(earning_accounts)

    _logger.info(f"📘 Total accounts to create per company: {len(all_accounts)}")

    # -----------------------------------------------------------
    # 3. Create Accounts Per Store
    # -----------------------------------------------------------
    AccountModel = env["account.account"]
    
    for company in companies:
        _logger.info(f"🏢 Processing company: {company.name} (ID: {company.id})")

        # Switch to the company context
        AccountModelCompany = AccountModel.with_company(company.id)

        for acc_name, acc_type in all_accounts.items():
            full_name = f"{acc_name} ({company.name})"

            # Check if account already exists
            # Search in the company context
            existing = AccountModelCompany.search([
                ("name", "=", full_name)
            ], limit=1)

            if existing:
                _logger.warning(f"⚠️ SKIPPED (already exists): {full_name}")
                continue

            try:
                # Generate sequence code
                code = env["ir.sequence"].next_by_code("custom.store.account.code") or "999999"

                # Create the account with company context
                AccountModelCompany.create({
                    "name": full_name,
                    "code": code,
                    "account_type": acc_type,
                    "reconcile": False,
                })

                _logger.info(f"✅ CREATED: {full_name} | Code: {code}")

            except Exception as e:
                _logger.error(f"❌ ERROR creating account '{full_name}' for company '{company.name}': {str(e)}")
                # Continue with next account even if one fails
                continue

    _logger.info("🎉 All store accounts have been processed successfully!")


def post_init_hook(env):
    """Called automatically after module installation"""
    _logger.info("🔧 Running post_init_hook for custom_invoice_template")
    create_store_accounts(env)
    _logger.info("🏁 post_init_hook finished")