{
    "name": "Project Forecast Task Planning",
    "summary": "Adds missing functionality to project_forecast module.",
    "description": """    
    Module's functionality:
    * Adds option to assign shifts to tasks.
    * Allows to group by tasks on shift views.
    * Allows to see forecasted hours for each task.
    * Adds task to shift notification.
    """,
    "author": "myOdoo.pl",
    "website": "https://myodoo.pl",
    "category": "Project Management",
    "version": "17.0.1.3.0",
    "depends": ["project", "planning", "project_forecast"],
    "data": [
        "views/planning_views.xml",
        "views/planning_template_views.xml",
        "views/planning_templates.xml",
        "views/project_views.xml",
    ],
    'images': ['static/description/banner.png'],
    "installable": True,
    "auto_install": False,
}
