from odoo import fields, models


class RoomBooking(models.Model):
    _inherit = "room.booking"

    event_id = fields.One2many("calendar.event", "booking_id")
    active = fields.Boolean("Active", related="event_id.active", tracking=True)
