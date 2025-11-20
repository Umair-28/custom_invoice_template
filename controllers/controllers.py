# -*- coding: utf-8 -*-
# from odoo import http


# class CustomInvoiceTemplate(http.Controller):
#     @http.route('/custom_invoice_template/custom_invoice_template', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_invoice_template/custom_invoice_template/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_invoice_template.listing', {
#             'root': '/custom_invoice_template/custom_invoice_template',
#             'objects': http.request.env['custom_invoice_template.custom_invoice_template'].search([]),
#         })

#     @http.route('/custom_invoice_template/custom_invoice_template/objects/<model("custom_invoice_template.custom_invoice_template"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_invoice_template.object', {
#             'object': obj
#         })

