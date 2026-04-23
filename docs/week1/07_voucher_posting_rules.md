# Voucher Posting Rules (Double-Entry)

## Objective
Define how business transactions generate vouchers and ledger entries.

---

## Voucher Types

1) Sales Voucher (SV)
2) Purchase Voucher (PV)
3) Receipt Voucher (RV)
4) Payment Voucher (PayV)
5) Journal Voucher (JV)
6) Expense Voucher (EV)
7) Sales Return Voucher (SRV)
8) Purchase Return Voucher (PRV)

---

## 1) Cash on Delivery Sale (Most Common)

### When Order is Delivered (COD confirmed):
DR 1100 Cash in Hand
CR 4100 Sales (Frames/Lenses/Accessories as per items)

### COGS Posting (optional but recommended):
DR 5100/5110/5120 COGS
CR 1130/1140/1150 Inventory Asset

---

## 2) Sale with Discount

DR 1100 Cash in Hand (Net Amount)
DR 4200 Sales Discounts (Discount)
CR 4100 Sales Revenue (Gross Amount)

COGS entry same as above.

---

## 3) Purchase Stock from Supplier (On Credit)

DR 1130/1140/1150 Inventory Asset
CR 2100 Supplier Payables

---

## 4) Supplier Payment (Bank)

DR 2100 Supplier Payables
CR 1110 Cash at Bank

---

## 5) Operating Expense (Cash)

DR 6xxx Expense Account (e.g., 6200 Electricity)
CR 1100 Cash in Hand

---

## 6) Customer Return (Sales Return)

### If refund in cash:
DR 4300 Sales Returns
CR 1100 Cash in Hand

### Stock back in inventory (if return accepted):
DR 1130/1140/1150 Inventory Asset
CR 5100/5110/5120 COGS  (reverse cost)

---

## 7) Stock Adjustment / Shrinkage

### Stock loss:
DR 5200 Inventory Loss / Shrinkage
CR 1130/1140/1150 Inventory Asset

### Stock increase (manual correction):
DR 1130/1140/1150 Inventory Asset
CR 6590 Misc Income / Adjustment (or JV)

---

## Implementation Note (Database)
- vouchers table = voucher header (date, type, source_id, totals)
- voucher_entries table = multiple lines per voucher (account_id, DR/CR, amount)
- Each voucher must satisfy:
  Total Debit = Total Credit