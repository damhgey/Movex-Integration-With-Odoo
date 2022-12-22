from odoo import api, fields, models
import requests
import json


class MovexCity(models.Model):
    _name = 'movex.city'
    _rec_name = 'name'
    _description = 'Updated Movex City'

    city_id = fields.Char("City ID")
    name = fields.Char("Name")
    code = fields.Char("Code")
    movex_id = fields.Many2one(comodel_name="delivery.carrier", required=True, readonly=True)
