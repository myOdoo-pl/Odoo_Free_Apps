
from odoo import api, fields, models, _



class PlanningTemplate(models.Model):
    _inherit = 'planning.slot.template'

    task_id = fields.Many2one('project.task', string="Task",
                              company_dependent=True, domain="[('project_id', '=?', project_id)]")

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.task_id.project_id != self.project_id:
            self.task_id = False

    @api.onchange('task_id')
    def _onchange_task_id(self):
        if self.task_id:
            self.project_id = self.task_id.project_id

    