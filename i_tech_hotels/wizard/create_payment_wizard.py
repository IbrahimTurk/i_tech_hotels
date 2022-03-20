import time
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class CreatePaymentWizard(models.TransientModel):
    _name = 'create.payment.wizard'


    reservation_id = fields.Many2many("hotels.reservation", string="Reservation ID", )
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,domain=[('type','in',('bank','cash'))])
    payment_type = fields.Selection([
        ('inbound', 'inbound'),
        ('outbound', 'outbound')
      
    ], string="payment type")
    amount =fields.Float(string="Amount", required=True)
    is_currencyrate = fields.Boolean(default=False)
    currency_rate = fields.Float(readonly=False)
    currency_amount = fields.Float(compute="_onchange_amount",readonly=True)
    notes =fields.Char(string="Notes")
    
    @api.onchange('journal_id')
    def _journal_id(self):
           return {'domain': {'journal_id': [('journal_user_id', '=', self.env.user.name)]}}

    api.model
    def create_payment(self):
     if self.amount < 1:
       raise ValidationError('The Amount should be > 1 ')
     else: 
         atts = self._context.get('default_customer')
         destination_account_id = self._context.get('destination_account_id')
         reservation_id =  self._context.get('reservation_id')
         total_amount = self._context.get('total_amount')
         payment_type = self._context.get('payment_type')
         rate = 1
         rate =self.env['res.currency'].search([('name', '=', self.journal_id.currency_id.name)], limit=1).rate
         pays =self._context.get('pays')
         if self.is_currencyrate == True:
          if self.env.user.company_id.currency_id==self.journal_id.currency_id:
            raise ValidationError('The main currency cannot be revalued')
          else:
           if self.currency_rate ==0:
               raise ValidationError('Currency Error (Rate)')
           else:
                if self.currency_amount ==0:
                 raise ValidationError('Currency Error (Amount)')
                else:
                    if self.currency_amount > total_amount-pays:
                     raise ValidationError('The amount paid should not be greater than the invoice value'+ str(total_amount-pays))
                    else:
                         payment = self.env['account.payment'].create({
                        'payment_type': payment_type,
                        'partner_id': atts,
                        'destination_account_id': destination_account_id,
                        'journal_id': self.journal_id.id,
                        'company_id': self.env.user.company_id.id,
                        'currency_id': self.journal_id.currency_id.id,
                        'ref': self.notes,
                        'amount': self.amount,
                        'is_currencyrate': self.is_currencyrate,
                        'currency_rate': self.currency_rate,
                        'currency_amount': self.currency_amount,
                        'reservation_id': reservation_id,
                        })
                         payment.action_post()
         else:
             if self.env.user.company_id.currency_id==self.journal_id.currency_id:
              if self.amount > total_amount-pays:
                     raise ValidationError('The amount paid should not be greater than the invoice value'+ str(total_amount-pays))
              else:
                     payment = self.env['account.payment'].create({
                        'payment_type': payment_type,
                        'partner_id': atts,
                        'destination_account_id': destination_account_id,
                        'journal_id': self.journal_id.id,
                        'company_id':  self.env.user.company_id.id,
                        'currency_id': self.journal_id.currency_id.id,
                        'ref': self.notes,
                        'amount': self.amount,
                        'is_currencyrate': self.is_currencyrate,
                        'currency_rate': self.currency_rate,
                        'currency_amount': self.currency_amount,
                        'reservation_id': reservation_id,
                        })
                     payment.action_post()
             else:
                 
                 if self.amount > ((total_amount*rate)-pays):
                     raise ValidationError('The amount paid should not be greater than the invoice value   ! '+ str(total_amount*rate-pays))
                     
                 else:
                         payment = self.env['account.payment'].create({
                        'payment_type': payment_type,
                        'partner_id': atts,
                        'destination_account_id': destination_account_id,
                        'journal_id': self.journal_id.id,
                        'company_id': self.env.user.company_id.id,
                        'currency_id': self.journal_id.currency_id.id,
                        'ref': self.notes,
                        'amount': self.amount,
                        'is_currencyrate': self.is_currencyrate,
                        'currency_rate': self.currency_rate,
                        'currency_amount': self.currency_amount,
                        'reservation_id': reservation_id,
                        })
                         payment.action_post()
                         
         if reservation_id != None:                
            totalpaid =0
            ticket_invoice = self.env['account.payment'].sudo().search(
               [('reservation_id', '=', reservation_id),('state','=','posted'),('payment_type','=',payment_type)])
            for pays in ticket_invoice:
                  totalpaid += abs(pays.amount_company_currency_signed)
                  if totalpaid == total_amount:
                     if payment_type =='inbound':
                        self.env['hotels.reservation'].search([('id','=',reservation_id)]).write({'reservation_status': 'paid'})
                     else:
                        self.env['hotels.reservation'].search([('id','=',reservation_id)]).write({'reservation_status': 'paid'})
      
    @api.depends('amount','currency_rate')
    def _onchange_amount(self):
      for rec in self:
            if rec.is_currencyrate == True:
               rec.currency_amount = rec.amount / rec.currency_rate 
            elif rec.is_currencyrate == False:
              rec.currency_rate = 0
              rec.currency_amount = 0
    @api.onchange('is_currencyrate','journal_id')
    def _onchange_currency(self):
      for rec in self:
            if rec.is_currencyrate == True:
               rec.currency_rate =self.env['res.currency'].search([('name', '=', rec.journal_id.currency_id.name)], limit=1).rate
               rec.currency_amount = rec.amount / rec.currency_rate 
            elif rec.is_currencyrate == False:
              rec.currency_rate = 0
              rec.currency_amount = 0 

       

           
         
