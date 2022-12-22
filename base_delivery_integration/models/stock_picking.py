from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection(selection_add=[('shipment_registered', 'Shipment Registered')])
    shipment_registered = fields.Boolean(string="Shipment Registered")
    shipment_provider = fields.Selection(string="Shipment Provider",
                                         selection=[('aramex', 'Aramex'), ('movex', 'Movex'), ], readonly=False, )
    shipment_state = fields.Char(string="Shipment status", readonly=True)
    tracking_number = fields.Char(string="Tracking Number", readonly=True)
    shipment_awb_url = fields.Char(string="Track By AWB", readonly=True)


