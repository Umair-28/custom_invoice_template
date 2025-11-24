# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

def create_store_accounts(env):
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

    # Find company records
    companies = env["res.company"].search([("name", "in", store_names)])
    if not companies:
        raise ValueError("No store companies found. Check names!")

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

    # Merge all accounts
    all_accounts = {}
    all_accounts.update(income_accounts)
    all_accounts.update(expense_accounts)
    all_accounts.update(tax_accounts)
    all_accounts.update(earning_accounts)

    # -----------------------------------------------------------
    # 3. Create Accounts Per Store
    # -----------------------------------------------------------
    for company in companies:
        print(f"Creating accounts for → {company.name}")

        for acc_name, acc_type in all_accounts.items():
            full_name = f"{acc_name} ({company.name})"

            # Check if already exists
            existing = env["account.account"].search([
                ("name", "=", full_name),
                ("company_id", "=", company.id)
            ])

            if existing:
                print(f"[SKIP] Already exists → {full_name}")
                continue

            # Create account
            env["account.account"].create({
                "name": full_name,
                "code": env["ir.sequence"].next_by_code("custom.store.account.code") or "999999",
                "company_id": company.id,
                "account_type": acc_type,
                "reconcile": False,
            })

            print(f"[CREATED] {full_name}")

    print("All store accounts have been created successfully.")


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    create_store_accounts(env)
