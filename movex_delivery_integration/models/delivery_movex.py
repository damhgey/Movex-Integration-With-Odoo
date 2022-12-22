from odoo import api, fields, models
import requests
import json


class ProviderMovex(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[('movex', "Movex")])
    movex_code = fields.Char(string="Movex Code", groups="base_delivery_integration.shipment_admin")
    movex_api_url = fields.Char(string="Movex API URL", groups="base_delivery_integration.shipment_admin")
    movex_username = fields.Char(string="Movex User Name", groups="base_delivery_integration.shipment_admin")
    movex_password = fields.Char(string="Movex Password", groups="base_delivery_integration.shipment_admin")
    movex_cities = fields.One2many(comodel_name="movex.city", inverse_name="movex_id", string="Movex Cities")

    def get_movex_credentials(self):
        url = self.sudo().movex_api_url
        username = self.sudo().movex_username
        password = self.sudo().movex_password

        payload = json.dumps({"username": username, "password": password})
        headers = {'Content-Type': 'application/json'}
        response = requests.request("POST", url + '/user/login', headers=headers, data=payload)
        token = response.json()['token']

        movex_credentials = {'url': url, 'username': username, 'password': password, 'token': token}

        return movex_credentials

    def action_update_movex_cities(self):
        movex_city_object = self.env['movex.city']
        current_movex_cities = movex_city_object.search([]).mapped('city_id')
        movex_credentials = self.get_movex_credentials()
        url = movex_credentials['url']
        token = movex_credentials['token']
        payload = {}
        headers = {'Authorization': f"Bearer {token}"}
        response = requests.request("GET", url + '/cities', headers=headers, data=payload)
        cities = response.json()['subzones']
        for city in cities:
            if str(city['id']) not in current_movex_cities:
                movex_city_object.create({'city_id': city['id'], 'name': city['name'], 'code': city['code'], 'movex_id': self.id})



