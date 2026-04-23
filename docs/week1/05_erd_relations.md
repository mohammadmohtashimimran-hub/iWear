# Week 1 – ERD Relations Blueprint (Enterprise)

## 1) Security & RBAC

- users (1) --- (M) user_roles --- (M) roles
- roles (1) --- (M) role_permissions --- (M) permissions
- users (1) --- (M) sessions
- users (1) --- (M) audit_logs

## 2) Master Data (Inventory Core)

- product_types (1) --- (M) products
- product_categories (1) --- (M) products
- brands (1) --- (M) products
- suppliers (1) --- (M) products (optional default supplier)
- products (1) --- (M) product_images
- products (1) --- (M) product_variants

## 3) Warehousing & Stock

- warehouses (1) --- (M) stock_movements
- products (1) --- (M) stock_movements
- product_variants (1) --- (M) stock_movements (if variant-level stock enabled)
- stock_movements -> drives current stock (calculated) OR stock_summary table

- products (1) --- (M) stock_adjustments
- warehouses (1) --- (M) stock_adjustments
- users (1) --- (M) stock_adjustments (who adjusted)

## 4) Procurement (Purchases)

- suppliers (1) --- (M) purchase_orders
- purchase_orders (1) --- (M) purchase_order_items
- products (1) --- (M) purchase_order_items
- product_variants (1) --- (M) purchase_order_items (optional)

- purchase_orders (1) --- (M) goods_receipts
- goods_receipts (1) --- (M) goods_receipt_items
- goods_receipt_items -> create stock_movements (IN)

## 5) Customers & Orders (Sales)

- customers (1) --- (M) customer_addresses
- customers (1) --- (M) orders
- orders (1) --- (M) order_items
- products (1) --- (M) order_items
- product_variants (1) --- (M) order_items (optional)
- orders (1) --- (M) order_status_history

## 6) Eyewear Customisation & Prescription

- orders (1) --- (M) prescriptions (if one order can have multiple prescriptions)
  OR
- order_items (1) --- (1) prescriptions (if per-item prescription)

Prescription support tables:
- lens_types, lens_indexes, lens_coatings
- prescriptions references:
  - lens_type_id
  - lens_index_id
  - lens_coating_id

## 7) Returns

- orders (1) --- (M) returns
- returns (1) --- (M) return_items
- return_items -> create stock_movements (IN) when return accepted

## 8) Finance (Voucher Based Accounting)

- chart_of_accounts (1) --- (M) voucher_entries
- vouchers (1) --- (M) voucher_entries
- vouchers linked to source transaction:
  - vouchers.source_type (SALE / PURCHASE / EXPENSE / PAYMENT / RECEIPT)
  - vouchers.source_id

Finance mapping:
- sales_transactions (1) --- (1) vouchers
- purchase_transactions (1) --- (1) vouchers
- expenses (1) --- (1) vouchers
- supplier_payments (1) --- (1) vouchers

## 9) AI Reporting

- reporting_intents (1) --- (M) intent_keywords
- reporting_intents (1) --- (1) predefined_queries
- users (1) --- (M) assistant_logs
- assistant_logs stores:
  - query_text
  - detected_intent_id
  - execution_time_ms
  - response_status