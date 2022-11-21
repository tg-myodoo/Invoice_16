v0.2.2
====
* views/account_move.xml - 2x new display_type field structure

v0.2.1
====
* models/account_move.py - two definitions of _x_compute_corrected_invoice_line_ids method

v0.2 - Correction invoice 16
====
* models/account.move.reversal.py - new 'auto_post' structure (bool->str) in reverse_moves method in AccountMoveReversal model
* models/account_move_line.py - recompute functions are redundant now, so were removed from run_onchanges method
* models/account_move.py - 2x removed redundant method _onchange_invoice_line_ids
* models/account_move_line.py - restored methods _get_price_total_and_subtotal and _get_price_total_and_subtotal_model after odoo removed them
* models/account_move_line.py - changes in method x_get_net_price_unit - computing the new value is no longer necessary


v0.1.9
====
* models/account_move.py - removed method _get_reconciled_info_values
* views/account_move.xml - fixed template "report_invoice_document_with_payments"

v0.1.8
====
* models/account_move.py - created new method _get_reconciled_info_values to replace old _get_reconciled_info_JSON_values

v0.1.7
====
* created models/account_tax.py - refactoring of method _get_tax_totals to _prepare_tax_totals - in model AccountTax _prepare_tax_totals method was created with completely new structure

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

v0.1 - Invoice 16
====
* models/sale_advance_payment_inv.py - into m2m field 'order_ids' in model 'SaleAdvancePaymentInv' was added relation 'sale_order_ref'
* views/account_move.xml - expression in 'bank transfer details' was chenged from <p name (...)> to <xpath (...)>


v0.0 - Odoo 15 module
====
* raw Odoo 15 module