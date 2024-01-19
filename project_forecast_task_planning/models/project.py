from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.osv import expression

import datetime
import logging
_logger = logging.getLogger(__name__)


class Task(models.Model):
    _inherit = 'project.task'

    allow_forecast = fields.Boolean(
        'Allow Planning', readonly=True, store=False, related='project_id.allow_forecast')
    forecast_hours = fields.Integer('Forecast Hours', compute='_compute_forecast_hours',
                                    help="Number of hours forecast for this task (and its sub-tasks), rounded to the unit.")
    planned_hours = fields.Float("Initially Planned Hours", help='Time planned to achieve this task (including its sub-tasks).', tracking=True)

    def _compute_forecast_hours(self):
        domain = expression.AND([
            self._get_domain_compute_forecast_hours(),
            [('task_id', 'in', self.ids + self._get_all_subtasks().ids)]
        ])
        forecast_data = self.env['planning.slot'].read_group(
            domain, ['allocated_hours', 'task_id'], ['task_id'])
        mapped_data = dict([(f['task_id'][0], f['allocated_hours'])
                           for f in forecast_data])
        for task in self:
            hours = mapped_data.get(task.id, 0) + sum(mapped_data.get(child_task.id, 0)
                                                      for child_task in task._get_all_subtasks())
            task.forecast_hours = int(round(hours))

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contains_plannings(self):
        if self.env['planning.slot'].sudo().search_count([('task_id', 'in', self.ids)]) > 0:
            raise UserError(
                _('You cannot delete a task containing plannings. You can either delete all the task\'s plannings and then delete the task or simply deactivate the task.'))

    def action_get_project_forecast_by_user(self):
        allowed_tasks = (self | self._get_all_subtasks() | self.depend_on_ids)
        action = self.env["ir.actions.actions"]._for_xml_id(
            "project_forecast.project_forecast_action_schedule_by_employee")
        first_slot = self.env['planning.slot'].search([('start_datetime', '>=', datetime.datetime.now(
        )), ('task_id', 'in', allowed_tasks.ids)], limit=1, order="start_datetime")
        action_context = {
            'group_by': ['task_id', 'resource_id'],
        }
        if first_slot:
            action_context.update({'initialDate': first_slot.start_datetime})
        else:
            planned_tasks = allowed_tasks.filtered('planned_date_begin')
            min_date = min(planned_tasks.mapped(
                'planned_date_begin')) if planned_tasks else False
            if min_date and min_date > datetime.datetime.now():
                action_context.update({'initialDate': min_date})
        action['context'] = action_context
        action['domain'] = [('task_id', 'in', allowed_tasks.ids)]
        return action

    # -------------------------------------------
    # Utils method
    # -------------------------------------------

    @api.model
    def _get_domain_compute_forecast_hours(self):
        return []


class Project(models.Model):
    _inherit = 'project.project'

    allow_forecast = fields.Boolean("Planning", default=True, help="Enable planning tasks on the project.")

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contains_plannings(self):
        if self.env['planning.slot'].sudo().search_count([('project_id', 'in', self.ids)]) > 0:
            raise UserError(
                _('You cannot delete a project containing plannings. You can either delete all the project\'s forecasts and then delete the project or simply deactivate the project.'))

    @api.depends('is_fsm')
    def _compute_allow_forecast(self):
        for project in self:
            if not project._origin:
                project.allow_forecast = not project.is_fsm