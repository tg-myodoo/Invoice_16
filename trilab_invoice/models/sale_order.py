from odoo import fields, models, api, _
from odoo.exceptions import UserError, AccessError
from itertools import groupby

# 15->16: 
from odoo.fields import Command

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    advance_invoices = fields.Many2many('account.move', compute='compute_advance_invoices', store=False)
    x_is_poland = fields.Boolean(compute='_x_compute_is_poland', string='Technical Field: Is Poland')

    @api.depends('company_id')
    def _x_compute_is_poland(self):
        for rec in self:
            rec.x_is_poland = rec.company_id.country_id.id == rec.env.ref('base.pl').id

    def compute_advance_invoices(self):
        for sale in self:
            sale.advance_invoices = (
                sale.order_line.filtered(lambda l: l.is_downpayment)
                .mapped('invoice_lines')
                .filtered(lambda l: l.credit > 0)
                .mapped('move_id')
            )

    def get_taxes_groups(self):
        taxes_groups = dict()
        for line in self.order_line.filtered(lambda l: not l.is_downpayment and not l.display_type):
            taxes_groups.setdefault(
                line.tax_id.tax_group_id.name,
                {'base': 0.0, 'tax': 0.0, 'total': 0.0, 'tax_percent': (line.tax_id.amount / 100.0)},
            )

            group = taxes_groups[line.tax_id.tax_group_id.name]
            group['base'] += line.price_subtotal
            # group['base'] += line.price_subtotal
            # group['tax'] += line.price_tax
            # group['total'] += line.price_subtotal + line.price_tax

        # rounding
        for tax_name in taxes_groups:
            tax_group = taxes_groups[tax_name]
            tax_group['base'] = self.currency_id.round(tax_group['base'])
            tax_group['tax'] = self.currency_id.round(tax_group['base'] * tax_group['tax_percent'])
            tax_group['total'] = tax_group['base'] + tax_group['tax']
            del tax_group['tax_percent']

        return taxes_groups

    def x_get_taxes_summary(self):
        summary = {'base': 0.0, 'tax': 0.0, 'total': 0.0}
        for group in self.get_taxes_groups().values():
            for key, value in group.items():
                summary[key] += value

        return summary

    def check_advance_invoice_values(self):
        taxes = self.order_line.mapped('tax_id')
        for tax in taxes:
            lines = self.order_line.filtered(lambda l: l.tax_id.id == tax.id)
            order_value = sum(line.price_total for line in lines.filtered(lambda l: not l.is_downpayment))
            invoice_lines = (
                lines.filtered(lambda l: l.is_downpayment).mapped('invoice_lines').filtered(lambda l: l.credit > 0)
            )
            advance_value = sum(line.price_total for line in invoice_lines)

            if advance_value - order_value > 0.05:
                raise UserError(_('Value in advance invoices is greater than order value'))

    def _create_invoices(self, grouped=False, final=False, date=None):
        if not any(self.mapped('x_is_poland')):
            # noinspection PyProtectedMember
            return super()._create_invoices(grouped, final, date)

        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        invoice_vals_list = []
        invoice_item_sequence = 0

        for order in self:
            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']
            invoice_vals = order._prepare_invoice()
            invoice_lines_vals = []
            # ZMIANA
            line_list = order.order_line

            if 'selected_invoice_lines' in self.env.context:
                line_list = line_list.filtered(lambda l: l.id in self.env.context['selected_invoice_lines'])

            # KONIEC ZMIANY
            for line in line_list:
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type:
                    if line.is_downpayment:
                        down_payments += line
                        continue

                    if current_section_vals:
                        invoice_item_sequence += 1
                        invoice_lines_vals.append(current_section_vals)
                        current_section_vals = None

                    invoice_item_sequence += 1
                    prepared_line = line._x_prepare_invoice_line(sequence=invoice_item_sequence)
                    invoice_lines_vals.append(prepared_line)

            for down_payment in down_payments:
                invoice_item_sequence += 1
                invoice_down_payment_vals = down_payment._x_prepare_invoice_line(sequence=invoice_item_sequence)
                invoice_lines_vals.append(invoice_down_payment_vals)

            # 15->16: new 'display_type' values
            if not any(new_line['display_type'] in (False, 'product') for new_line in invoice_lines_vals):
            # if not any(new_line['display_type'] is False for new_line in invoice_lines_vals):

                # 15->16: new method _nothing_to_invoice_error_message instead of old _nothing_to_invoice_error
                raise UserError(self._nothing_to_invoice_error_message())
                # raise self._nothing_to_invoice_error()

            # 15->16: new field structure: Command
            invoice_vals['invoice_line_ids'] = [Command.create(invoice_line_id) for invoice_line_id in invoice_lines_vals]
            # invoice_vals['invoice_line_ids'] = [(0, 0, invoice_line_id) for invoice_line_id in invoice_lines_vals]
            invoice_vals_list.append(invoice_vals)
   
        # 15->16:
        if not invoice_vals_list and self._context.get('raise_if_nothing_to_invoice', True):
        # if not invoice_vals_list:  
          
            # 15->16: new method _nothing_to_invoice_error_message instead of old _nothing_to_invoice_error
            raise UserError(self._nothing_to_invoice_error_message())
            # raise self._nothing_to_invoice_error()

        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()

            for grouping_keys, invoices in groupby(
                invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]
            ):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update(
                    {
                        'ref': ', '.join(refs)[:2000],
                        'invoice_origin': ', '.join(origins),
                        'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                    }
                )
                new_invoice_vals_list.append(ref_invoice_vals)

            invoice_vals_list = new_invoice_vals_list

        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']

            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    # noinspection PyProtectedMember
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(
                        new=sequence, old=line[2]['sequence']
                    )
                    sequence += 1

        currency_rate = self.env['res.currency.rate'].browse(self.env.context.get('x_convert_rate', 0))
        if currency_rate:
            for invoice in invoice_vals_list:
                for inv_line in invoice['invoice_line_ids']:
                    inv_line[2]['price_unit'] = inv_line[2]['price_unit'] * currency_rate.x_rate_inverted
                invoice['narration'] = _(
                    'Rate %s with effective date: %s', currency_rate.x_rate_inverted, currency_rate.name
                )

        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()

        for move in moves:
            move.x_onchange_set_currency_rate()
            # 15->16:
            move.message_post_with_view(
                'mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.sale_line_ids.order_id},
                subtype_id=self.env['ir.model.data']._xmlid_to_res_id('mail.mt_note'))
            # move.message_post_with_view(
            #     'mail.message_origin_link',
            #     values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
            #     subtype_id=self.env.ref('mail.mt_note').id,
            # )

        return moves

    @api.depends_context('x_convert_rate', 'x_partner_bank_id')
    def _prepare_invoice(self):
        # noinspection PyProtectedMember
        invoice_vals = super()._prepare_invoice()
        if self.env.context.get('x_convert_rate'):
            invoice_vals['currency_id'] = self.env.ref('base.PLN').id
        if 'x_partner_bank_id' in self.env.context:
            invoice_vals['partner_bank_id'] = self.env.context['x_partner_bank_id']
        return invoice_vals
