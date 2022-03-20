import logging
from odoo import models, fields, _


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'account.journal'

    journal_user_id = fields.Many2one('res.users', string='User Name')
