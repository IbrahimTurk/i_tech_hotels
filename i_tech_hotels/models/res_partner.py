import logging
from odoo import models, fields, _


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_sales_man = fields.Boolean(default=False)
