from odoo import api, fields, models, _, Command
# from odoo.osv import expression
# from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError
# from odoo.tools.misc import formatLang
# from odoo.tools import get_lang, float_compare, format_date, formatLang, ormcache
from odoo.tools import formatLang, ormcache, float_is_zero
# from odoo.tools import frozendict

from collections import defaultdict
# import math
# import re

import logging
_logger = logging.getLogger(__name__)

class AccountTax(models.Model):
    _inherit = 'account.tax'

    # 15->16: copied from AccountMove model
    @api.model
    @ormcache('self')
    def x_get_is_poland(self):
        """ normally x_is_poland should be used, but for the record sets, this method should be used"""
        return self.env.company.country_id.id == self.env.ref('base.pl').id

    # 15->16: refactoring of method _get_tax_totals to _prepare_tax_totals - _prepare_tax_totals was created with completely new structure
    @api.model
    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None):
        result = super()._prepare_tax_totals(base_lines, currency, tax_lines)
        if not self.x_get_is_poland():
            return result

        # 15->16: from _get_tax_totals
        lang_env = self.env # self.with_context(lang=partner.lang).env # 15->16
        pln = self.env.company.currency_id
        tax_amount_in_pln = 0
        x_invoice_sign = 1

        # ==== Compute the taxes ====

        to_process = []
        for base_line in base_lines:
            to_update_vals, tax_values_list = self._compute_taxes_for_single_line(base_line)
            to_process.append((base_line, to_update_vals, tax_values_list))

            # 15->16:
            # x_invoice_sign = base_line.get('x_invoice_sign', 1)
            if base_line['is_refund']: x_invoice_sign = -1
            else: x_invoice_sign = 1


        def grouping_key_generator(base_line, tax_values):
            source_tax = tax_values['tax_repartition_line'].tax_id
            return {'tax_group': source_tax.tax_group_id}

        global_tax_details = self._aggregate_taxes(to_process, grouping_key_generator=grouping_key_generator)

        tax_group_vals_list = []
        for tax_detail in global_tax_details['tax_details'].values():
            tax_group_vals = {
                'tax_group': tax_detail['tax_group'],
                'base_amount': tax_detail['base_amount_currency'],
                'tax_amount': tax_detail['tax_amount_currency'],
                'x_balance_amount': 0.0, # 15->16
            }

            # Handle a manual edition of tax lines.
            if tax_lines is not None:
                matched_tax_lines = [
                    x
                    for x in tax_lines
                    if (x['group_tax'] or x['tax_repartition_line'].tax_id).tax_group_id == tax_detail['tax_group']
                ]
                if matched_tax_lines:
                    tax_group_vals['tax_amount'] = sum(x['tax_amount'] for x in matched_tax_lines)
                    # 15->16:
                    # balance = line_data.get('x_balance', 0.0)
                    balance = sum(x['tax_amount'] for x in matched_tax_lines) # ??? TO DO: revrite in correct way
                    tax_group_vals['x_balance_amount'] = balance # += balance
                    tax_amount_in_pln = balance # += balance

            # 15->16:
            for key in ('base_amount', 'tax_amount', 'x_balance_amount'):
                if not float_is_zero(tax_group_vals.get(key, 0), precision_rounding = self.env.company.currency_id.rounding):
                    tax_group_vals[key] = x_invoice_sign * tax_group_vals.get(key, 0)

            tax_group_vals_list.append(tax_group_vals)

        tax_group_vals_list = sorted(tax_group_vals_list, key=lambda x: (x['tax_group'].sequence, x['tax_group'].id))

        # ==== Partition the tax group values by subtotals ====

        # 15->16:
        amount_untaxed = x_invoice_sign * abs(global_tax_details['base_amount_currency'])
        # amount_untaxed = global_tax_details['base_amount_currency']
        amount_tax = 0.0

        subtotal_order = {}
        groups_by_subtotal = defaultdict(list)
        for tax_group_vals in tax_group_vals_list:
            tax_group = tax_group_vals['tax_group']

            subtotal_title = tax_group.preceding_subtotal or _("Untaxed Amount")
            sequence = tax_group.sequence

            subtotal_order[subtotal_title] = min(subtotal_order.get(subtotal_title, float('inf')), sequence)
            groups_by_subtotal[subtotal_title].append({
                'group_key': tax_group.id,
                'tax_group_id': tax_group.id,
                'tax_group_name': tax_group.name,
                'tax_group_amount': tax_group_vals['tax_amount'],
                'tax_group_base_amount': tax_group_vals['base_amount'],

                # 15->16: from _get_tax_totals
                'x_tax_group_total_amount': tax_group_vals['tax_amount'] + tax_group_vals['base_amount'],
                'x_tax_group_amount_in_pln': tax_group_vals['x_balance_amount'],
                    
                'formatted_tax_group_amount': formatLang(self.env, tax_group_vals['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, tax_group_vals['base_amount'], currency_obj=currency),

                # 15->16: from _get_tax_totals
                'x_formatted_tax_group_amount_in_pln': formatLang(
                        lang_env, tax_group_vals['x_balance_amount'], currency_obj=pln),
                'x_formatted_tax_group_total_amount': formatLang(
                        lang_env, tax_group_vals['tax_amount'] + tax_group_vals['base_amount'], currency_obj=currency),
            })

        # ==== Build the final result ====

        subtotals = []
        for subtotal_title in sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]):
            amount_total = amount_untaxed + amount_tax
            subtotals.append({
                'name': subtotal_title,
                'amount': amount_total,
                'formatted_amount': formatLang(self.env, amount_total, currency_obj=currency),
            })
            amount_tax += sum(x['tax_group_amount'] for x in groups_by_subtotal[subtotal_title])

        amount_total = amount_untaxed + amount_tax
        # 15->16: for tests only: _logger.info("Z: " + str(amount_untaxed) + " " + str(amount_tax) + " " + str(amount_total)) # =============================

        display_tax_base = (len(global_tax_details['tax_details']) == 1 and tax_group_vals_list[0]['base_amount'] != amount_untaxed) \
            or len(global_tax_details['tax_details']) > 1

        return {
            'amount_untaxed': currency.round(amount_untaxed) if currency else amount_untaxed,
            'amount_total': currency.round(amount_total) if currency else amount_total,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals,
            'subtotals_order': sorted(subtotal_order.keys(), key=lambda k: subtotal_order[k]),
            'display_tax_base': display_tax_base,

            # 15->16: from _get_tax_totals
            'x_tax_amount': amount_tax,
            'x_formatted_tax_amount': formatLang(lang_env, amount_tax, currency_obj=currency),
            'x_tax_amount_in_pln': tax_amount_in_pln,
            'x_formatted_tax_amount_in_pln': formatLang(lang_env, tax_amount_in_pln, currency_obj=pln)     
        }
