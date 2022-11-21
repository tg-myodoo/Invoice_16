from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    _sql_constraints = [('check_credit_debit', 'CHECK(True)', 'Wrong credit or debit value in accounting entry!')]

    corrected_line = fields.Boolean(default=False)

    # only for user input/visualization
    # x_price_unit_reverse = fields.Float(compute='x_compute_reverse', inverse='x_set_price_unit_reverse',
    #                                     store=False, readonly=False)
    x_quantity_reverse = fields.Float(
        compute='x_compute_reverse',  # inverse='x_set_quantity_reverse',
        digits='Product Unit of Measure',
        store=False,
        readonly=False,
    )
    x_price_subtotal_reverse = fields.Float(compute='x_compute_reverse', store=False, readonly=True)
    x_price_total_reverse = fields.Float(compute='x_compute_reverse', store=False, readonly=True)

    x_move_type = fields.Selection(related='move_id.move_type', store=False)
    
    # 15->16: restored field account_internal_type after odoo removed it
    # 15->16: new account_id structure: account_id.user_type_id.type -> account_id.account_type
    # ==== Business fields ====
    account_internal_type = fields.Selection(related='account_id.account_type', string="Internal Type", readonly=True)
    # account_internal_type = fields.Selection(related='account_id.user_type_id.type', string="Internal Type", readonly=True)

    # 15->16: restored fields analytic_account_id and analytic_tag_ids after odoo removed them
    # ==== Analytic fields ====
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',
        index=True, compute="_compute_analytic_account_id", store=True, readonly=False, check_company=True, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
        compute="_compute_analytic_tag_ids", store=True, readonly=False, check_company=True, copy=True)

    # 15->16: restored fields recompute_tax_line, is_rounding_line and exclude_from_invoice_tab after odoo removed them
    # ==== Onchange / display purpose fields ====
    recompute_tax_line = fields.Boolean(store=False, readonly=True,
        help="Technical field used to know on which lines the taxes must be recomputed.")
    is_rounding_line = fields.Boolean(help="Technical field used to retrieve the cash rounding line.")
    exclude_from_invoice_tab = fields.Boolean(help="Technical field used to exclude some lines from the invoice_line_ids tab in the form view.")
    

    # 15->16: restored method _compute_analytic_account_id after odoo removed it
    @api.depends('product_id', 'account_id', 'partner_id', 'date')
    def _compute_analytic_account_id(self):
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                if rec:
                    record.analytic_account_id = rec.analytic_id

    # 15->16: restored method _compute_analytic_tag_ids after odoo removed it
    @api.depends('product_id', 'account_id', 'partner_id', 'date')
    def _compute_analytic_tag_ids(self):
        for record in self:
            if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(include_receipts=True):
                rec = self.env['account.analytic.default'].account_get(
                    product_id=record.product_id.id,
                    partner_id=record.partner_id.commercial_partner_id.id or record.move_id.partner_id.commercial_partner_id.id,
                    account_id=record.account_id.id,
                    user_id=record.env.uid,
                    date=record.date,
                    company_id=record.move_id.company_id.id
                )
                if rec:
                    record.analytic_tag_ids = rec.analytic_tag_ids

    @api.depends('quantity', 'price_unit', 'price_subtotal', 'price_total')
    def x_compute_reverse(self):
        for line in self:
            sign = -1  # if line.corrected_line else 1
            # line.x_price_unit_reverse = sign * line.price_unit
            line.x_quantity_reverse = sign * line.quantity
            line.x_price_subtotal_reverse = sign * line.price_subtotal
            line.x_price_total_reverse = sign * line.price_total
            # sign = -1 if line.corrected_line else 1
            # line.price_unit_inverse = sign * line.price_unit
            # line.price_subtotal_inverse = sign * line.price_subtotal
            # line.price_total_inverse = sign * line.price_total

    @api.onchange('x_quantity_reverse', 'x_price_subtotal_reverse', 'x_price_total_reverse')
    def x_set_reverse_values(self):
        for line in self:
            # line.price_unit = -line.price_unit_inverse
            line.quantity = -line.x_quantity_reverse
            line.price_subtotal = -line.x_price_subtotal_reverse
            line.price_total = -line.x_price_total_reverse
            # noinspection PyProtectedMember
            line._onchange_price_subtotal()
            # line.price_unit = -line.price_unit_inverse
            # line.price_subtotal = -line.price_subtotal_inverse
            # line.price_total = -line.price_total_inverse

    def _get_computed_price_unit(self):
        self.ensure_one()

        if self.env.company.country_id.id == self.env.ref('base.pl').id and self.corrected_line:
            return self.price_unit

        # noinspection PyProtectedMember
        return super()._get_computed_price_unit()

    def run_onchanges(self):
        # 15->16: recompute functions are redundant now

        # self._onchange_mark_recompute_taxes()
        # self._onchange_balance()
        # self._onchange_debit()
        # self._onchange_credit()
        # self._onchange_amount_currency()
        # self._onchange_price_subtotal()
        # self._onchange_currency()
        pass

    @api.model
    def _get_fields_onchange_balance_model(
        self, quantity, discount, amount_currency, move_type, currency, taxes, price_subtotal, force_computation=False
    ):
        if self.corrected_line:
            return {}  # do not change anything

        # noinspection PyProtectedMember
        return super()._get_fields_onchange_balance_model(
            quantity, discount, amount_currency, move_type, currency, taxes, price_subtotal, force_computation
        )

    # 15->16: computing the new value is no longer necessary ???
    def x_get_net_price_unit(self):
        self.ensure_one()
        # return self.price_subtotal # no - at this point computing is still necessary
        return self._get_price_total_and_subtotal(quantity=1)['price_subtotal']


    # 15->16: restored method after odoo removed it
    def _get_price_total_and_subtotal(self, price_unit=None, quantity=None, discount=None, currency=None, product=None, partner=None, taxes=None, move_type=None):
        self.ensure_one()
        return self._get_price_total_and_subtotal_model(
            price_unit=self.price_unit if price_unit is None else price_unit,
            quantity=self.quantity if quantity is None else quantity,
            discount=self.discount if discount is None else discount,
            currency=self.currency_id if currency is None else currency,
            product=self.product_id if product is None else product,
            partner=self.partner_id if partner is None else partner,
            taxes=self.tax_ids if taxes is None else taxes,
            move_type=self.move_id.move_type if move_type is None else move_type,
        )

    # 15->16: restored method after odoo removed it
    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        # Compute 'price_total'.
        if taxes:
            taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res


    @api.onchange("quantity", "discount", "price_unit", "tax_ids")
    def _onchange_price_subtotal(self):
        # 15->16: recompute functions are redundant now
        # return super(
        #     AccountMoveLine, self.move_id._x_update_context_with_currency_rate(self)
        # )._onchange_price_subtotal()
        pass

    @api.onchange("amount_currency")
    def _onchange_amount_currency(self):
        return super(
            AccountMoveLine, self.move_id._x_update_context_with_currency_rate(self)
        )._onchange_amount_currency()
