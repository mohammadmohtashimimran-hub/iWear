"""SQLAlchemy models — import so Flask-Migrate can discover them.
   Import order: users, audit, catalog, inventory, sales, eyewear, finance, ai_reporting.
"""
from app.extensions import db

# Security & access
from app.models.users import (
    user_roles,
    User,
    Role,
    Permission,
    RolePermission,
    Session,
)
from app.models.audit import AuditLog

# Catalog (product master + legacy stock)
from app.models.catalog import (
    ProductCategory,
    ProductBrand,
    ProductType,
    Product,
    Addon,
    AddonOption,
    Stock,
)

# Inventory
from app.models.inventory import (
    Supplier,
    Warehouse,
    ProductVariant,
    ProductImage,
    StockMovement,
    StockAdjustment,
    InventoryValuation,
)

# Sales
from app.models.sales import (
    Customer,
    CustomerAddress,
    Cart,
    CartItem,
    CartItemAddon,
    OrderStatus,
    Order,
    OrderItem,
    Return,
    ReturnItem,
)

# Eyewear domain
from app.models.eyewear import (
    FrameType,
    LensType,
    LensIndex,
    LensCoating,
    PrescriptionRecord,
    PrescriptionDetail,
)

# Finance
from app.models.finance import (
    PaymentType,
    Payment,
    VoucherType,
    ChartOfAccount,
    Voucher,
    VoucherEntry,
    JournalEntry,
    ExpenseCategory,
    Expense,
    PurchaseOrder,
    PurchaseOrderItem,
    SupplierPayment,
    SalesTransaction,
    TaxRecord,
)

# Settings (vendor config)
from app.models.settings import StoreSetting, Country, City

# AI reporting
from app.models.ai_reporting import (
    DailySalesSummary,
    MonthlyProfitSummary,
    InventoryValuationSummary,
    FinancialReportLog,
    ReportingIntent,
    IntentKeyword,
    PredefinedQuery,
    AssistantQueryLog,
)

UserRole = user_roles  # compatibility alias

__all__ = [
    "user_roles",
    "UserRole",
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "Session",
    "AuditLog",
    "ProductCategory",
    "ProductBrand",
    "ProductType",
    "Product",
    "Addon",
    "AddonOption",
    "Stock",
    "Supplier",
    "Warehouse",
    "ProductVariant",
    "ProductImage",
    "StockMovement",
    "StockAdjustment",
    "InventoryValuation",
    "Customer",
    "CustomerAddress",
    "Cart",
    "CartItem",
    "CartItemAddon",
    "OrderStatus",
    "Order",
    "OrderItem",
    "Return",
    "ReturnItem",
    "FrameType",
    "LensType",
    "LensIndex",
    "LensCoating",
    "PrescriptionRecord",
    "PrescriptionDetail",
    "PaymentType",
    "Payment",
    "VoucherType",
    "ChartOfAccount",
    "Voucher",
    "VoucherEntry",
    "JournalEntry",
    "ExpenseCategory",
    "Expense",
    "PurchaseOrder",
    "PurchaseOrderItem",
    "SupplierPayment",
    "SalesTransaction",
    "TaxRecord",
    "DailySalesSummary",
    "MonthlyProfitSummary",
    "InventoryValuationSummary",
    "FinancialReportLog",
    "ReportingIntent",
    "IntentKeyword",
    "PredefinedQuery",
    "AssistantQueryLog",
    "StoreSetting",
    "Country",
    "City",
]
