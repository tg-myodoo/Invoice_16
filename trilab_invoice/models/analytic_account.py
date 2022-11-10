from odoo import api, fields, models

# 15->16: restored AccountAnalyticTag model after odoo removed them
class AccountAnalyticTag(models.Model):
    _name = 'account.analytic.tag'
    _description = 'Analytic Tags'
    # name = fields.Char(string='Analytic Tag', index=True, required=True)
    # color = fields.Integer('Color Index')
    # active = fields.Boolean(default=True, help="Set active to false to hide the Analytic Tag without removing it.")
    # active_analytic_distribution = fields.Boolean('Analytic Distribution')
    # analytic_distribution_ids = fields.One2many('account.analytic.distribution', 'tag_id', string="Analytic Accounts")
    company_id = fields.Many2one('res.company', string='Company')

    # @api.constrains('company_id')
    # def _check_company_consistency(self):
    #     analytic_tags = self.filtered('company_id')

    #     if not analytic_tags:
    #         return

    #     self.flush(['company_id'])
    #     self._cr.execute('''
    #         SELECT line.id
    #         FROM account_analytic_tag_account_move_line_rel tag_rel
    #         JOIN account_analytic_tag tag ON tag.id = tag_rel.account_analytic_tag_id
    #         JOIN account_move_line line ON line.id = tag_rel.account_move_line_id
    #         WHERE tag_rel.account_analytic_tag_id IN %s
    #         AND line.company_id != tag.company_id
    #     ''', [tuple(analytic_tags.ids)])

    #     if self._cr.fetchone():
    #         raise UserError(_("You can't set a different company on your analytic tags since there are some journal items linked to it."))

