from odoo import api, fields, models
import requests
import json


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def update_movex_shipment_state(self):
        # Movex api data
        movex_object = self.env['delivery.carrier'].search([('movex_code', '=', 'MOVEX')], limit=1)
        movex_credentials = movex_object.get_movex_credentials()
        url = movex_credentials['url']
        token = movex_credentials['token']
        payload = {}
        headers = {'Authorization': f"Bearer {token}"}

        # Movex shipments to update state
        movex_shipments = self.search([('shipment_provider', '=', 'movex'), ('shipment_state', 'in', ('draft', 'progress'))])
        if movex_shipments:
            for shipment in movex_shipments:
                shipment_tracking_number = shipment.tracking_number
                try:
                    response = requests.request("GET", url + '/track' + f'/{shipment_tracking_number}', headers=headers, data=payload)
                    shipment_update_state = response.json()['shipments'][0]['state']
                    shipment.write({'shipment_state': shipment_update_state})
                except:
                    pass

