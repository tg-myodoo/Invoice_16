from odoo import models, fields, api


class CurrencyRate(models.Model):
    _inherit = 'res.currency.rate'

    x_rate_inverted = fields.Float(digits=0, string='Rate Inverted', compute='_x_compute_rate_inverted')

    @api.depends('rate')
    def _x_compute_rate_inverted(self):
        for curr_rate in self:
            curr_rate.x_rate_inverted = 1 / curr_rate.rate

    def name_get(self):
        return [
            (curr_rate.id, f'{curr_rate.currency_id.name} - {curr_rate.name} - {curr_rate.x_rate_inverted}')
            for curr_rate in self
        ]


class Currency(models.Model):
    _inherit = 'res.currency'

    # noinspection PyShadowingBuiltins
    def _convert(self, from_amount, to_currency, company, date, round=True):
        if self._context.get("x_trilab_force_currency_rate"):
            self, to_currency = self or to_currency, to_currency or self
            assert self, "convert amount from unknown currency"
            assert to_currency, "convert amount to unknown currency"
            assert company, "convert amount from unknown company"
            assert date, "convert amount from unknown date"

            if self == to_currency:
                to_amount = from_amount
            else:
                to_amount = from_amount * self._context["x_trilab_force_currency_rate"]
            return to_currency.round(to_amount) if round else to_amount

        return super()._convert(from_amount, to_currency, company, date, round=round)
