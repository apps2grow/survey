##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    conditional = fields.Boolean(
        'Conditional Question',
        copy=False,
        # we add copy = false to avoid wrong link on survey copy,
        # should be improoved
    )
    question_conditional_id = fields.Many2one(
        'survey.question',
        'Question',
        copy=False,
        domain="[('survey_id', '=', survey_id)]",
        help="In order to edit this field you should"
             " first save the question"
    )
    answer_ids = fields.Many2many(
        'survey.label',
        string='Answers',
        copy=False,
    )

    @api.multi
    def validate_question(self, post, answer_tag):
        ''' Validate question, depending on question
        type and parameters '''
        self.ensure_one()
        try:
            checker = getattr(self, 'validate_' + self.type)
        except AttributeError:
            _logger.warning(
                checker.type +
                ": This type of question has no validation method")
            return {}
        else:
            # TODO deberiamos emprolijar esto
            if not self.question_conditional_id:
                return checker(post, answer_tag)
            input_answer_ids = self.env['survey.user_input_line'].search(
                [('user_input_id.token', '=', post.get('token')),
                 ('question_id', '=', self.question_conditional_id.id)])
            conditional = False
            for answer in input_answer_ids:
                value_suggested = answer.value_suggested
                if self.conditional and value_suggested in self.answer_ids:
                    conditional = True
            if conditional == False:
                return {}
            else:
                return checker(post, answer_tag)
