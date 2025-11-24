from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_note = fields.Char(string="Delivery Note")
    mode_of_payment = fields.Char(string="Mode of Payment")
    ref_no = fields.Char(string="Reference No")
    other_ref = fields.Char(string="Other References")

    buyer_order_no = fields.Char(string="Buyer Order No")
    dispatch_doc_no = fields.Char(
        string="Dispatch Doc No",
        related="name",
        store=True,
        readonly=False
    )
    delivery_note_date = fields.Char(string="Delivery Note Date")
    dispatch_through = fields.Char(string="Dispatched Through")
    destination = fields.Char(string="Destination")
    bill_of_landing = fields.Char(string="Bill of Landing/LR-RR-No")
    vehicle_no = fields.Char(stirng="Vehicle No")
    delivery_terms = fields.Char(string="Terms of Delivery")

    consignee_name = fields.Char(string="Name")
    consignee_address = fields.Char(string="Address")
    consigness_gst = fields.Char(string="GSTIN/UIN")
    consignee_state = fields.Char(string="State")
    consigness_code = fields.Char(string="Code")

