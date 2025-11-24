from odoo import models, fields

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_note = fields.Char(string="Delivery Note")
    mode_of_payment = fields.Char(string="Mode of Payment")
    ref_no = fields.Char(string="Reference No")
    other_ref = fields.Char(string="Other References")

