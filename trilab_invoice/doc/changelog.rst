v0.1.6
====
* views/account_move.xml - 2x renamed tax_totals_json field to tax_totals
* models/account_move.py - 2x renamed _compute_tax_totals_json method to _compute_tax_totals

v0.1.5
====
* models/account_move.py - in method _compute_payments_widget_to_reconcile_info - attribute: invoice_outstanding_credits_debits_widget is no longer stored in json
* models/account_move.py - new structure of attribute invoice_outstanding_credits_debits_widget - new keys in 'content' dictionary

v0.1.4
====
* models/account_move.py - recompute functions are redundant now, so were removed from x_onchange_set_currency_rate method
* models/account_move_line.py - recompute functions are redundant now, so were removed from _onchange_price_subtotal method
* created models/account_analytic_default.py - restored AccountAnalyticDefault model after odoo removed them

v0.1.3
====
* models/account_move_line.py - restored field account_internal_type after odoo removed it
* models/account_move_line.py - new account_id structure: account_id.user_type_id.type -> account_id.account_type
* models/account_move_line.py - restored fields recompute_tax_line, is_rounding_line and exclude_from_invoice_tab after odoo removed them

v0.1.2
====
* models/account_move_line.py - restored field analytic_account_id and method _compute_analytic_account_id after odoo removed them
* models/account_move_line.py - restored field analytic_tag_ids and method _compute_analytic_tag_ids after odoo removed them
* created models/analytic_account.py with restored AccountAnalyticTag model after odoo removed them

v0.1.1
====
* models/account_move.py - new account_id structure - 3x: account_id.user_type_id.type -> account_id.account_type & ('receivable', 'payable') -> ('asset_receivable', 'liability_payable')
* views/account_move_views.xml - new account_id structure - 2x: ('user_type_id.type', 'not in', ('receivable', 'payable')) -> ('account_type', 'not in', ('asset_receivable', 'liability_payable'))

v0.1
====
* models/sale_advance_payment_inv.py - into m2m field 'order_ids' in model 'SaleAdvancePaymentInv' was added relation 'sale_order_ref'
* views/account_move.xml - expression in 'bank transfer details' was chenged from <p name (...)> to <xpath (...)>

v0.0
====
* raw Odoo 15 module