v1.0.0
=======
* Added fields room_id/booking_id on calendar.event model.
* Added fields event_id/active on room.booking model.
* Overwritten create/write/unlink method on calendar.event to create room.booking and edit it accordingly.
* Added room_id field on calendar.event views.

