import logging
from odoo import models, fields, _


_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
   _inherit = "account.move"
   reservation_id = fields.Many2one('hotels.reservation', string='Reservation ID')

