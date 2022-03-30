from odoo import api, fields, models,api,fields, exceptions, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class projects(models.Model):
    _inherit = ['mail.thread']
    _name = "hotels.projects"
    _sql_constraints = [
        ('rooms_uniuqe', 'unique(name)', 'name already exists!')
    ]


    name = fields.Char(string="Room Name", required=True) 
    journal_revenue = fields.Many2one('account.journal', string='Journal For Revenue', required=True)
    revenue_account_id = fields.Many2one('account.account', string='Customer Account: ', required=True)

class rooms(models.Model):
    _inherit = ['mail.thread']
    _name = "hotels.rooms"
    _sql_constraints = [
        ('rooms_uniuqe', 'unique(name)', 'name already exists!')
    ]


    name = fields.Char(string="Room Name", required=True) 
    project_id = fields.Many2one("hotels.projects",string="Project Name", required=True)
    available = fields.Boolean()
    sequnece =fields.Integer(string="Sequnece Number", required=True)
    price = fields.Float(string="Price", required=True)
    

class services(models.Model):
    _inherit = ['mail.thread']
    _name = "hotels.services"
    
    name = fields.Char(string="Name")
    reservation_id = fields.Many2one('hotels.reservation', string='reservation ID')
    create_ondate = fields.Datetime('Date', required=False, readonly=True,
                                    default=lambda self: fields.datetime.now())                              
    notes =fields.Char("Notes")
    qty = fields.Integer("Qty")
    price = fields.Float("Price")
    total = fields.Float("Total",readonly=True,compute="_total", tracking=True,store=True)
    is_admin = fields.Boolean(readonly=True)


    #@api.depends('qty','price')
    #def _total(self):
    #     self.total =self.qty * self.price

class projects(models.Model):
    _name = "hotels.accbal"


    journal_id = fields.Many2one('account.journal', string='Journal', required=True,domain=[('type','in',('bank','cash'))])
    amount = fields.Float(string="Amount",compute="_aomunt", tracking=True,store=True)

    @api.onchange('journal_id')
    def _aomunt(self):
        for record in self:
           if self.journal_id: 
                d = datetime.today()
                aml_ids = self.env['account.move.line'].search([('reconciled', '=', False),
                    ('account_id', '=',self.journal_id.default_account_id.id ),
                    ('move_id.state', '=', 'posted'),
                    ('create_date','<=',d)
                ])
                
                total_credit = 0
                total_debit = 0
                for aml in aml_ids:
                   if self.env.user.company_id.currency_id==self.journal_id.currency_id:      
                    total_credit += aml.credit
                    total_debit += aml.debit
                   else:
                    total_debit += aml.amount_currency
                record.amount = total_debit-total_credit



class reservation(models.Model):
    _inherit = ['mail.thread','mail.activity.mixin']
    _name = "hotels.reservation"
    

    reservation_status = fields.Selection([
        ('draft', 'Draft'),
        ('reservation', 'Basic Reservation'),
        ('submit', 'Submit'),
        ('paid', 'paid'),
        ('cancel', 'Cancel')
    ], string="Reservation Status",
        default="draft", tracking=True)
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True,
                       default=lambda self: _('New'))
    reservation_date = fields.Datetime('Date', required=True, readonly=True,
                                    default=lambda self: fields.datetime.now())
    customername = fields.Many2one("res.partner", domain=[('is_sales_man', '=', False)],string="Customer", required=True, tracking=True)
    salesman = fields.Many2one("res.partner", domain=[('is_sales_man', '=', True)],string="Sales Man", required=True, tracking=True)                                
    notes = fields.Char(string="Notes", tracking=True)
    project_id = fields.Many2one("hotels.projects",string="Project", required=True, tracking=True)
    room_id = fields.Many2one("hotels.rooms",string="Rooms", required=True, tracking=True)
    amount = fields.Float(string="Amount",compute="_price", tracking=True,store=True)
    from_date = fields.Date(string="From Date" ,required=True, tracking=True)
    to_date = fields.Date(string="To Date" ,required=True, tracking=True)
    services_ids = fields.One2many('hotels.services', 'reservation_id', string='Services', tracking=True)
    account_move_ids = fields.One2many('account.move', 'reservation_id', string='Related Journals', tracking=True)
    account_payment_ids = fields.One2many('account.payment', 'reservation_id', string='Related Journals', tracking=True)
    allday =fields.Boolean(default=True)
    chick_line =fields.Boolean(default=False,compute="_price" ,store=True,tracking=True)
    
    def write(self, vals, context=None):  
      roomid =  vals.get('room_id')
      fromdate = vals.get('from_date')
      todate = vals.get('to_date')
      room_id = self.room_id.id
      from_date = self.from_date
      to_date = self.to_date
      if roomid:
          room_id = roomid
      if fromdate:
          from_date = fromdate
      if  todate:
            to_date= todate
#      servisids=vals.get('services_ids')
      
#      if  servisids:
#       service_line=servisids[0][0]
#       if service_line:
#        chick=service_line.get('name')
#       else:
#            chick=None
#       roomids =vals.get('room_id')
#       if roomids:
#        room_id_name =self.env['hotels.rooms'].search([('id','=',roomids)])
#       else:
#        room_id_name =self.env['hotels.rooms'].search([('id','=',self.room_id.id)])
#       riname=room_id_name.name 
#      else:
#       chick = None
#       riname = None
      fromdate = self.env["hotels.reservation"].search([('from_date','>=',str(from_date)),('to_date','<=',str(to_date)),('room_id','=',room_id),('id','!=',self.id),('reservation_status',  'not in', ['draft', 'cancel'])], limit=1)
      if fromdate:
         raise ValidationError('Reservation Must be have uniuqe date and Room  To Can Created ')
      else:
        #if chick!=riname:
              # raise ValidationError('Reservation Must be have Room Service Lines  To Can Created ') 
        result = super(reservation, self).write(vals)                   
        return result 


    @api.model
    def create(self, vals):
#       servisids=vals.get('services_ids')
#       if servisids:
#        service_line=servisids[0][2]
#        chick=service_line.get('name')
#        roomids =vals.get('room_id')
#        room_id =self.env['hotels.rooms'].search([('id','=',roomids)])
#      else:
#          raise ValidationError('Reservation Must be have Room Service Lines  To Can Created ')
      # froma =  vals.get('from_date')
      # to =   vals.get('to_date')
     #  room =   vals.get('room_id')
       fromdate = self.env["hotels.reservation"].search([('from_date','>=',vals.get('from_date')+' 00:00:00'),('to_date','<=',vals.get('to_date')+' 00:00:00'),('room_id','=',vals.get('room_id')),('reservation_status',  'not in', ['draft', 'cancel'])], limit=1)
       if fromdate:
         raise ValidationError('Reservation Must be have uniuqe date and Room  To Can Created ')
       else:

#         if chick==room_id.name:
            if vals.get('name', _('New')) == _('New'):
                    vals['name'] = self.env['ir.sequence'].next_by_code('resersequence') or _('New')
            result = super(reservation, self).create(vals)                   
            return result
#        else:
#             raise ValidationError('Reservation Must be have Room Service Lines  To Can Created ')  
       
     
    def unlink(self):
        if self.reservation_status != 'draft':
             raise ValidationError('Reservation Must be Draft State To Can Deleted ')
        return super().unlink()
    
    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            self.room_id = False
            return {'domain': {'room_id': [('project_id', '=', rec.project_id.id)]}}

    @api.onchange('room_id','from_date','to_date')
    def onchange_room_id(self):
        if self.room_id:
            qty =   self.to_date - self.from_date
            loan_lines = []
            loan_lines.append((0, 0, {'is_admin': True, 'name': self.room_id.name,'qty': qty.days+1,'price':self.room_id.price,'total': self.room_id.price*(qty.days+1)}))
            self.services_ids= [(6, 0, [])]
            self.services_ids=loan_lines 


    @api.depends('services_ids')
    def _price(self):
       total_amount =0.00
       for tot in self.services_ids:
           tot.total =tot.qty*tot.price
           total_amount += tot.total
       self.amount = total_amount
       self.chick_line =False
       for x in self.services_ids:
            if x.is_admin:
                self.chick_line =True
                break


    def action_to_cancel(self):
        for rec in self:
            rec.reservation_status = 'cancel'
            if len(rec.account_move_ids) > 0:
               for move in rec.account_move_ids:
                   move.button_draft()
                   move.button_cancel()
            if len(rec.services_ids) > 0:
               rec.services_ids = [(5, 0, 0)] 


    def action_to_reservation(self):
        for rec in self:
            if rec.reservation_status != 'draft':
                raise ValidationError('Reservation Must be Draft State To Can Passport ')
            else:
                rec.reservation_status = 'reservation'


    def action_to_submit(self):
        for rec in self:
            if rec.reservation_status != 'reservation':
                raise ValidationError('Reservation Must be Reservation State To Can submited ')
            else:
                rec.reservation_status = 'submit'
                if rec.amount > 0:
                   rec._account_move_create_customer()    
      
    def _account_move_create_customer(self):
        journal_revenue = self.env["hotels.projects"].search([('id','=',self.project_id.id)], limit=1).journal_revenue.id
        revenue_account_id = self.env["hotels.projects"].search([], limit=1).revenue_account_id.id
        for reser in self:
            label = reser.notes
            amount = reser.amount
            move = self.env["account.move"].create({
                    "journal_id": journal_revenue,
                    'reservation_id': reser.id,
                    "line_ids": [(0, 0, {
                        "partner_id": reser.customername.id,
                        'name': label,
                        "account_id": reser.customername.property_account_receivable_id.id,  # customer
                        'credit': 0,
                        'debit': amount, }),
                                 (0, 0, {
                                     "partner_id": reser.customername.id,  # customer
                                     "account_id": revenue_account_id,  # customer
                                     'credit': amount,
                                     'debit': 0,
                                 })]
                })
            move.action_post()  

        
    def action_customer_pay(self):
        totalpaid = 0
        atts = self._context.get('active_ids')
        att_ids = self.env['hotels.reservation'].browse(atts)
        for pays in self.account_payment_ids:
            if pays.state =='posted'  and pays.payment_type=='inbound':
                totalpaid += pays.amount_company_currency_signed
        return {'type': 'ir.actions.act_window',
                'name': _('Create Payment'),
                'res_model': 'create.payment.wizard',
                'target': 'new',
                'view_id': self.env.ref('i_tech_hotels.create_payment_wizard_form').id,
                'view_mode': 'form',
                'context': {'default_customer': self.customername.id,'destination_account_id': self.customername.property_account_receivable_id.id , 'payment_type': "inbound",'reservation_id':self.id,'total_amount': self.amount,'pays':totalpaid}

                }
   

                
