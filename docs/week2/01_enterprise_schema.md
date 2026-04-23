# Week 2 – Enterprise Schema (iWear)

## Overview

The database is structured into domain-aligned table groups to support full enterprise operations: security, catalog, inventory, eyewear, sales, finance, and AI reporting.

---

## Table Groups

### 1. Security & Access Control

- **users** – app users (email, password_hash)
- **roles** – role names
- **user_roles** – many-to-many User ↔ Role
- **permissions** – permission name, code, description
- **role_permissions** – which permissions each role has
- **sessions** – active sessions (token_jti, expires_at, is_active)
- **audit_logs** – who did what (action, entity_type, entity_id, details_json)

### 2. Catalog (Product Master)

- **product_categories**, **product_brands**, **product_types** – master data
- **products** – product header (name, slug, price, category, brand, type)
- **stock** – legacy: one row per product, qty_on_hand (kept for backward compatibility)

### 3. Inventory Foundation

- **suppliers** – supplier master (name, phone, email, address, city)
- **warehouses** – warehouse master (name, code, location)
- **product_variants** – SKU-level variants (sku, barcode, color, size, unit_price) per product
- **product_images** – image_url, alt_text, is_primary per product
- **stock_movements** – movement-based inventory (product_variant, warehouse, movement_type, quantity, reference)
- **stock_adjustments** – adjustments with reason and created_by (user)
- **inventory_valuation** – snapshot of quantity_on_hand, unit_cost, total_value per variant/warehouse/date

### 4. Eyewear Domain

- **frame_types**, **lens_types**, **lens_indexes**, **lens_coatings** – master data for prescriptions
- **prescription_records** – per customer, with notes
- **prescription_details** – per record: eye_side, sphere, cylinder, axis, add_power, pd

### 5. Sales & Order Management

- **customers** – first_name, last_name, phone, email
- **customer_addresses** – address lines, city, state, postal_code, country, is_default
- **carts**, **cart_items** – cart with items (product_variant, quantity, unit_price)
- **order_statuses** – status name, code
- **orders** – customer, status, order_number, subtotal, discount_total, tax_total, grand_total
- **order_items** – product_variant, quantity, unit_price, discount_amount, tax_amount, line_total
- **returns**, **return_items** – return_number, linked to order and order_item

### 6. Payment & Finance (Accounting Baseline)

- **payment_types** – name, code
- **payments** – order, payment_type, amount, payment_reference, status, paid_at
- **voucher_types** – name, code
- **chart_of_accounts** – account_code, account_name, account_type, parent_id (self-FK for hierarchy)
- **vouchers** – voucher_type, voucher_number, reference_type/id, voucher_date, narration
- **voucher_entries** – voucher_id, chart_of_account_id, debit, credit, line_description
- **journal_entries** – voucher_id, posting_date
- **expense_categories**, **expenses** – category and expense rows (amount, expense_date)
- **purchase_orders**, **purchase_order_items** – PO header/line (supplier, warehouse, product_variant, quantity, unit_cost)
- **supplier_payments** – supplier, payment_type, amount, payment_date
- **sales_transactions** – order, transaction_date, gross/discount/tax/net amounts
- **tax_records** – name, rate_percent, is_active

### 7. Financial Reporting Support

- **daily_sales_summary** – summary_date, gross_sales, discounts, taxes, net_sales
- **monthly_profit_summary** – summary_month, summary_year, gross_profit, net_profit (unique on month+year)
- **inventory_valuation_summary** – summary_date, total_inventory_value
- **financial_reports_log** – report_name, generated_by (user), generated_at, report_parameters_json

### 8. AI Assistant Support

- **reporting_intents** – name, code (e.g. “sales summary”)
- **intent_keywords** – keywords per intent
- **predefined_queries** – query_name, sql_template, active per intent
- **assistant_query_logs** – user_id, raw_query, interpreted_intent_id, response_status

---

## Movement-Based Inventory

The legacy **stock** table (one row per product, `qty_on_hand`) is kept for backward compatibility. Going forward, inventory is driven by:

- **stock_movements** – every IN/OUT (e.g. purchase receipt, sale, return) with movement_type, quantity, and optional reference (e.g. order_id).
- **stock_adjustments** – manual corrections with reason and user.
- **inventory_valuation** – snapshots for reporting (quantity_on_hand, unit_cost, total_value by variant/warehouse/date).

This allows full audit trail, multi-warehouse, and variant-level stock. Current stock can be derived by summing movements (or from valuation snapshots).

---

## Finance Baseline: Vouchers and Accounting

- **Vouchers** are the main document type: each voucher has a type (e.g. SV, PV, JV), unique voucher_number, date, and optional reference to a source transaction (reference_type, reference_id).
- **Voucher entries** are double-entry lines: each line posts to a **chart_of_accounts** account with debit/credit. Total debit = total credit per voucher.
- **Chart of accounts** supports hierarchy via parent_id and is used for financial reporting.
- **Journal entries** link to vouchers with a posting_date for period control.
- Sales, purchases, expenses, and payments can be linked to vouchers via reference_type/reference_id for audit and reporting.
