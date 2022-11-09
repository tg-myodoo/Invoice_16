v0.1.1
====
* models/account_move.py - 3x: 
    account_id.user_type_id.type -> account_id.account_type 
    ('receivable', 'payable') -> ('asset_receivable', 'liability_payable')
* views/account_move_views.xml - 2x:
    ('user_type_id.type', 'not in', ('receivable', 'payable')) -> ('account_type', 'not in', ('asset_receivable', 'liability_payable'))

v0.1
====
* models/sale_advance_payment_inv.py - into m2m field 'order_ids' in model 'SaleAdvancePaymentInv' was added relation 'sale_order_ref'
* views/account_move.xml - expression in 'bank transfer details' was chenged from <p name (...)> to <xpath (...)>
* name of module was changed back to 'trilab_invoice'

v0.0
====
* Raw Odoo 15 module