from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = "calendar.event"

    room_id = fields.Many2one(
        "room.room", string="Room", help="Room in which meeting will be held."
    )
    booking_id = fields.Many2one("room.booking")

    def _create_booking(self, event):
        """Method to create a new booking based on the events fields."""
        return self.env["room.booking"].create(
            {
                "name": event.name,
                "room_id": event.room_id.id,
                "start_datetime": event.start,
                "stop_datetime": event.stop,
            }
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Overwritten create method to create a new booking while creating an event."""
        records = super(Meeting, self).create(vals_list)
        for record in records:
            if not record.room_id:
                continue
            record.booking_id = self._create_booking(record)
        return records

    def write(self, vals):
        """
        Overwritten write method to handle changes made to event on rooms booking.
        If room_id is cleared - unlink booking.
        If room_id is added - create a new booking.
        If date or name is changed - change it on booking.
        """
        result = super(Meeting, self).write(vals)
        for record in self:
            if vals.get("room_id", True) == False:  # Cleared room_id case
                record.booking_id.unlink()
            elif vals.get("room_id", False):  # New room_id case
                record.booking_id.unlink()
                record.booking_id = self._create_booking(record)
            elif (
                vals.get("start", False)
                or vals.get("stop", False)
                or vals.get("name", False)
            ):  # Date/Name changed case
                record.booking_id.write(
                    {
                        "name": record.name,
                        "start_datetime": record.start,
                        "stop_datetime": record.stop,
                    }
                )
        return result

    def unlink(self):
        """Overwritten unlink method to unlink bookings before unlinking record."""
        self.booking_id.unlink()
        return super(Meeting, self).unlink()
