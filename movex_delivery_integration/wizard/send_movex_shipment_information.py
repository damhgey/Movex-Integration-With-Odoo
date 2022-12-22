# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import requests
import json
import base64


class SendMovexShipmentInformation(models.TransientModel):
    _name = 'send.movex.shipment.information'

    # Shipment information
    shipment_type = fields.Selection(string="Shipment Type",
                                     selection=[('delivery', 'Delivery'),
                                                ('pickup', 'Pickup'),
                                                ('replacement', "Replacement")],
                                     default='delivery', required=True)
    ref = fields.Char(string="Ref", required=True, readonly=True)
    cod = fields.Float(string="COD", required=True)
    from_city = fields.Many2one(comodel_name="movex.city", string="From City", required=True)
    to_city = fields.Many2one(comodel_name="movex.city", string="To City", required=True, )
    pieces_number = fields.Integer(string="Pieces Number", required=True)
    weight = fields.Integer(string="Weight", default=1, required=True)
    width = fields.Integer(string="Width", default=1, required=True)
    length = fields.Integer(string="Length", default=1, required=True)
    height = fields.Integer(string="Height", default=1, required=True)
    # Sender Information
    sender_name = fields.Char(string="Sender Name", required=True)
    sender_address = fields.Char(string="Sender Address", required=True)
    sender_note = fields.Char(string="Sender Note", required=False)
    # Client information fields
    client_name = fields.Char(string="Client Name", required=True)
    client_phone1 = fields.Char(string="Client Phone 1", required=True)
    client_phone2 = fields.Char(string="Client Phone 2", required=False)
    client_email = fields.Char(string="Client Email", required=False)
    client_address = fields.Char(string="Client Address", required=True)
    client_note = fields.Char(string="Client Note", required=False)

    @api.constrains('pieces_number')
    def _check_pieces_number(self):
        if self.pieces_number <= 0.0:
            raise ValidationError(_('Pieces number must be higher than zero.'))

    def get_picking(self):
        active_model = self.env.context.get('active_model')
        active_id = self._context.get('active_id')
        if active_model == 'stock.picking' and active_id:
            picking = self.env['stock.picking'].browse(active_id)
            return picking

    @api.model
    def default_get(self, fields):
        res = super(SendMovexShipmentInformation, self).default_get(fields)
        picking = self.get_picking()
        if picking:
            has_backorder = picking.search([('backorder_id', '=', picking.id)])
            if picking.sale_id.payment_gateway_id.code == 'cod' and not picking.backorder_id and not has_backorder:
                cod = picking.sale_id.amount_total
            else:
                cod = 0.0

            from_city = self.env['movex.city'].search([('code', '=', 'OBR')]).id
            # to_city = self.env['movex.city'].search([('city_id', '=', 1523)]).id
            pieces_number = 0.0
            sender_name = self.env.company.name
            # Sender address
            city = self.env.company.city or ' '
            street = self.env.company.street or ' '
            sender_address = city + ', ' + street
            sender_note = picking.note or ' '
            client_name = picking.partner_id.name
            client_phone1 = picking.partner_id.phone or ' '
            client_phone2 = picking.partner_id.mobile or ' '
            client_email = picking.partner_id.email
            # Client address
            city = picking.partner_id.city or ' '
            street = picking.partner_id.street or ' '
            client_address = city + ', ' + street
            client_note = picking.sale_order_note or ' '

            res['ref'] = picking.origin
            res['cod'] = cod
            res['from_city'] = from_city
            # res['to_city'] = to_city
            res['pieces_number'] = pieces_number
            res['sender_name'] = sender_name
            res['sender_address'] = sender_address
            res['sender_note'] = sender_note
            res['client_name'] = client_name
            res['client_phone1'] = client_phone1
            res['client_phone2'] = client_phone2
            res['client_email'] = client_email
            res['client_address'] = client_address
            res['client_note'] = client_note

        return res

    def prepare_shipment_data(self):
        shipment_data = {'type': self.shipment_type,
                         'ref1': self.ref,
                         'cod': self.cod,
                         'from_city_id': self.from_city.city_id,
                         'to_city_id': self.to_city.city_id,
                         'pieces_number': self.pieces_number,
                         'weight': self.weight,
                         'width': self.width,
                         'length': self.length,
                         'height': self.height,
                         'sender_name': self.sender_name,
                         'sender_address': self.sender_address,
                         'description': self.sender_note,
                         'consignee_name': self.client_name,
                         'phone': self.client_phone1,
                         'mobile': self.client_phone2,
                         'consignee_address': self.client_address,
                         'special_instructions': self.client_note,
                         }
        return shipment_data

    def send_shipment_to_movex(self):
        # Checks on COD
        picking = self.get_picking()
        has_backorder = picking.search([('backorder_id', '=', picking.id)])
        if picking.sale_id.payment_gateway_id.code == 'accept-valu' and self.cod == 0:
            raise ValidationError(_('Put ValU Amount in COD'))
        if (picking.backorder_id or has_backorder) and picking.sale_id.payment_gateway_id.code == 'cod' and self.cod == 0:
            raise ValidationError(_('This picking is split with backorder, you should calculate COD and put right value'))

        try:
            movex_object = self.env['delivery.carrier'].search([('movex_code', '=', 'MOVEX')], limit=1)
            movex_credentials = movex_object.get_movex_credentials()
            url = movex_credentials['url']
            token = movex_credentials['token']
            payload = self.prepare_shipment_data()
            headers = {'Authorization': f"Bearer {token}"}
            response = requests.request("POST", url + '/shipment', headers=headers, data=payload)
        except:
            raise ValidationError(_("Bad Request, Couldn't create shipment in Movex."))
        created_shipment = response.json()['shipments'][0]
        shipment_id = created_shipment['id']
        shipment_file_url = created_shipment['file']
        shipment_awb = created_shipment['awb']
        shipment_status = created_shipment['state']

        shipment_file_pdf = self.get_shipment_file_lable(shipment_file_url, token, shipment_awb)

        picking = self.get_picking()
        if picking:
            logmessage = (_("Shipment Created Into Movex With <br/> <b>Tracking Number : </b>%s") % (shipment_awb))
            picking.message_post(body=logmessage, attachments=[(f"Shipment lable: {shipment_awb}", shipment_file_pdf)])

            picking.write(
                {'shipment_awb_url': shipment_awb, 'shipment_state': shipment_status,
                 'tracking_number': shipment_awb, 'shipment_registered': True, })

    def get_shipment_file_lable(self, shipment_file_url, token, shipment_awb):
        headers = {'Authorization': f"Bearer {token}"}
        response = requests.request("GET", shipment_file_url, headers=headers, data={})
        data = response.content
        return data


