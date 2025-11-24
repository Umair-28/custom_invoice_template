# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def create_store_accounts(env):
    _logger.info("🚀 Starting Store Account Creation Process")

    # -----------------------------------------------------------
    # 1. Define Stores (Companies)
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

    companies = env["res.company"].search([("name", "in", store_names)])
    if not companies:
        _logger.warning("❌ Some or all store companies not found. Skipping missing stores.")
    else:
        _logger.info(f"🔎 Found {len(companies)} companies for account creation.")

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
    for company in companies:
        _logger.info(f"🏢 Processing company: {company.name}")

        for acc_name, acc_type in all_accounts.items():
            full_name = f"{acc_name} ({company.name})"

            existing = env["account.account"].search([
                ("name", "=", full_name),
                ("company_id", "=", company.id)
            ])

            if existing:
                _logger.warning(f"⚠️ SKIPPED (already exists): {full_name}")
                continue

            try:
                code = env["ir.sequence"].next_by_code("custom.store.account.code") or "999999"

                env["account.account"].create({
                    "name": full_name,
                    "code": code,
                    "company_id": company.id,
                    "account_type": acc_type,
                    "reconcile": False,
                })

                _logger.info(f"✅ CREATED: {full_name} | Code: {code}")

            except Exception as e:
                _logger.error(f"❌ ERROR creating account '{full_name}' for company '{company.name}': {str(e)}")

    _logger.info("🎉 All store accounts have been processed successfully!")


def post_init_hook():
    """
    Hook called after all modules are loaded.
    Safe for accessing fields like account.account.company_id
    """
    import odoo
    env = odoo.api.Environment(odoo.registry(odoo.tools.config.odoo18).cursor(), SUPERUSER_ID, {})
    _logger.info("🔧 Running post_load hook for custom invoice module...")
    create_store_accounts(env)
    _logger.info("🏁 post_load hook execution finished.")

