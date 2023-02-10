import logging
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from odoo.osv import expression
import ast
import datetime
import json
_logger = logging.getLogger(__name__)


class PlanningShift(models.Model):
    _inherit = 'planning.slot'

    task_id = fields.Many2one(
        'project.task', string="Task", compute='_compute_task_id', store=True, readonly=False,
        copy=True, check_company=True, group_expand='_read_group_task_id',
        domain="[('company_id', '=', company_id), ('project_id', '=?', project_id), ('allow_forecast', '=', True)]")

    @api.depends('project_id', 'template_id.project_id')
    def _compute_task_id(self):
        for slot in self:
            if slot.project_id != slot.task_id.project_id:
                slot.task_id = False
            if slot.template_id:
                slot.previous_template_id = slot.template_id
                if slot.template_id.task_id:
                    slot.task_id = slot.template_id.task_id
            elif slot.previous_template_id and not slot.template_id and slot.previous_template_id.task_id == slot.task_id:
                slot.task_id = False

    def _read_group_task_id(self, tasks, domain, order):
        if 'show_tasks_without_slot' in self.env.context and 'active_ids' in self.env.context:
            return self.env['project.task'].browse(self.env.context.get('active_ids'))
        dom_tuples = [(dom[0], dom[1])
                      for dom in domain if isinstance(dom, list) and len(dom) == 3]
        if self._context.get('planning_expand_task') and ('start_datetime', '<=') in dom_tuples and ('end_datetime', '>=') in dom_tuples:
            if ('task_id', '=') in dom_tuples or ('task_id', 'ilike') in dom_tuples:
                filter_domain = self._expand_domain_m2o_groupby(
                    domain, 'task_id')
                return self.env['project.task'].search(filter_domain, order=order)
            filters = expression.AND(
                [[('task_id.active', '=', True)], self._expand_domain_dates(domain)])
            return self.env['planning.slot'].search(filters).mapped('task_id')
        return tasks


class Task(models.Model):
    _inherit = 'project.task'

    allow_forecast = fields.Boolean(
        'Allow Planning', readonly=True, related='project_id.allow_forecast', store=False)
    forecast_hours = fields.Integer('Forecast Hours', compute='_compute_forecast_hours',
                                    help="Number of hours forecast for this task (and its sub-tasks), rounded to the unit.")

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

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


class Project(models.Model):
    _inherit = 'project.project'

    @api.ondelete(at_uninstall=False)
    def _unlink_except_contains_plannings(self):
        if self.env['planning.slot'].sudo().search_count([('project_id', 'in', self.ids)]) > 0:
            raise UserError(
                _('You cannot delete a project containing plannings. You can either delete all the project\'s forecasts and then delete the project or simply deactivate the project.'))
