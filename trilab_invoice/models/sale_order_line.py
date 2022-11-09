from odoo import models, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _x_prepare_invoice_line(self, line_list=False, **optional_values):
        self.ensure_one()
        quantity = self.qty_to_invoice
        if self.is_downpayment and line_list and quantity < 0:
            sum_field = 'price_total' if self.tax_id.price_include else 'price_subtotal'
            invoice_lines = line_list.filtered(lambda l: not l.is_downpayment and l.tax_id.ids == self.tax_id.ids)
            so_lines = self.order_id.order_line.filtered(
                lambda l: not l.is_downpayment and l.tax_id.ids == self.tax_id.ids
            )
            invoice_value = sum(
                line.qty_to_invoice * (line[sum_field] / line.product_uom_qty) for line in invoice_lines
            )
            so_value = sum(line[sum_field] for line in so_lines)
            quantity = -1 * (invoice_value / so_value)
        res = self._prepare_invoice_line(sequence=optional_values['sequence'])
        res['quantity'] = quantity
        return res

    @api.depends('invoice_lines.move_id.state', 'invoice_lines.quantity')
    def _compute_qty_invoiced(self):
        super()._compute_qty_invoiced()
        for line in self.filtered(lambda x: x.is_downpayment and x.order_id.x_is_poland):
            # For down payment sale.order.line count only qty_invoiced from down payment invoices
            qty_invoiced = 0.0
            for invoice_line in line.invoice_lines.filtered(lambda x: x.move_id.is_downpayment):
                if invoice_line.move_id.state != 'cancel':
                    if invoice_line.move_id.move_type == 'out_invoice':
                        qty_invoiced += invoice_line.product_uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
                    elif invoice_line.move_id.move_type == 'out_refund':
                        qty_invoiced -= invoice_line.product_uom_id._compute_quantity(
                            invoice_line.quantity, line.product_uom
                        )
            line.qty_invoiced = qty_invoiced

    def write(self, values):
        if 'price_unit' in values and self._context.get('x_block_changing_price') and self.is_downpayment:
            raise UserError('It is forbidden to change price_unit after Posting Invoice')
        return super().write(values)
