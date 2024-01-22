{
    "name": "Calendar Room Booker",
    "summary": "Reserve a room with calendar event creation.",
    "description": """    
    The Calendar Room Booker module is your comprehensive solution for efficient room reservation management within Odoo. 
    Seamlessly integrated with the calendar, this module simplifies the process of reserving meeting rooms.
    """,
    "author": "myOdoo.pl",
    "website": "https://myodoo.pl",
    "category": "Tools",
    "version": "17.0.1.0.0",
    "depends": [
        "calendar",
        "room",
    ],
    "data": [
        "views/calendar_views.xml",
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "auto_install": False,
}
