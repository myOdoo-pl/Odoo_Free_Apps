{
    'name': 'Project Forecast Task Planning',
    'summary': 'Adds missing functionality to project_forecast module.',
    'description': '''    
    Module's functionality:
    * Adds option to assign shifts to tasks.
    * Allows to group by tasks on shift views.
    * Allows to see forecasted hours for each task.
    * Adds task to shift notification.
    ''',
    'author': 'myOdoo.pl',
    'website': 'https://myodoo.pl',
    'category': 'Project Management',
    'version': '[V16]_1.0.2.2',
    'depends': [
        'project',
        'planning',
        'project_forecast'
    ],
    'data': [
        'views/planning_views.xml',
        'views/planning_template_views.xml',
        'views/planning_templates.xml',
        'views/project_views.xml',
    ],
    "images": [
        "static/description/banner.png",
        "static/description/shift_creation.png",
        "static/description/task_forecast.png",
        "static/description/shift_notification.png"
    ],
    'installable': True,
    'auto_install': False
}
