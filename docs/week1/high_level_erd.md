# iWear High-Level ER Design – Week 1

```mermaid
erDiagram
    User ||--o{ UserRole : "has"
    Role ||--o{ UserRole : "assigned to"

    ProductCategory ||--o{ Product : "category"
    ProductBrand ||--o{ Product : "brand"
    ProductType ||--o{ Product : "type"
    Product ||--o{ ProductVariant : "has many"
    ProductVariant ||--o{ StockLedger : "ledger entries"

    Customer ||--o{ Prescription : "has"
    Customer ||--o{ SalesOrder : "places"
    SalesOrder ||--o{ SalesOrderItem : "has many"
    SalesOrderItem }o--|| ProductVariant : "product"
    SalesOrder ||--o{ Payment : "payments"

    Supplier ||--o{ PurchaseOrder : "supplies"
    PurchaseOrder ||--o{ PurchaseOrderItem : "has many"
    PurchaseOrderItem }o--|| Product : "product"

    PaymentMethod ||--o{ Payment : "via"

    Account ||--o{ VoucherLine : "posted in"
    Voucher ||--o{ VoucherLine : "has many"
    VoucherLine }o--|| Account : "account"

    User {
        int id PK
        string email
        string password_hash
        datetime created_at
    }

    Role {
        int id PK
        string name
    }

    UserRole {
        int user_id FK
        int role_id FK
    }

    ProductCategory {
        int id PK
        string name
    }

    ProductBrand {
        int id PK
        string name
    }

    ProductType {
        int id PK
        string name
    }

    Product {
        int id PK
        string name
        string slug
        int category_id FK
        int brand_id FK
        int type_id FK
        decimal price
    }

    ProductVariant {
        int id PK
        int product_id FK
        string sku
    }

    StockLedger {
        int id PK
        int variant_id FK
        int qty
        string movement_type
    }

    Customer {
        int id PK
        string name
        string email
    }

    Supplier {
        int id PK
        string name
    }

    Prescription {
        int id PK
        int customer_id FK
        string details
    }

    SalesOrder {
        int id PK
        int customer_id FK
        datetime order_date
        string status
    }

    SalesOrderItem {
        int id PK
        int sales_order_id FK
        int product_variant_id FK
        int qty
        decimal unit_price
    }

    PurchaseOrder {
        int id PK
        int supplier_id FK
        datetime order_date
        string status
    }

    PurchaseOrderItem {
        int id PK
        int purchase_order_id FK
        int product_id FK
        int qty
        decimal unit_price
    }

    Payment {
        int id PK
        int payment_method_id FK
        decimal amount
        datetime paid_at
    }

    PaymentMethod {
        int id PK
        string name
    }

    Account {
        int id PK
        string code
        string name
    }

    Voucher {
        int id PK
        string voucher_type
        datetime voucher_date
    }

    VoucherLine {
        int id PK
        int voucher_id FK
        int account_id FK
        decimal debit
        decimal credit
    }
```

## Relationship summary

| From | To | Relationship |
|------|-----|--------------|
| User ↔ Role | UserRole | Many-to-many (UserRole links User and Role) |
| ProductCategory | Product | One-to-many (Product belongs to Category) |
| ProductBrand | Product | One-to-many (Product belongs to Brand) |
| ProductType | Product | One-to-many (Product belongs to Type) |
| Product | ProductVariant | One-to-many (Product has many Variants) |
| ProductVariant | StockLedger | One-to-many (Variant linked to StockLedger) |
| Customer | SalesOrder | One-to-many |
| SalesOrder | SalesOrderItem | One-to-many |
| SalesOrderItem | ProductVariant | Many-to-one (product) |
| Supplier | PurchaseOrder | One-to-many |
| PurchaseOrder | PurchaseOrderItem | One-to-many |
| PurchaseOrderItem | Product | Many-to-one (product) |
| Voucher | VoucherLine | One-to-many |
| VoucherLine | Account | Many-to-one |
| PaymentMethod | Payment | One-to-many |
| Customer | Prescription | One-to-many |
