# Appendix A.1 — Individual Section: Member 1

**Name:** [Member 1 Name]
**Banner ID:** [Banner ID 1]
**Project area:** Inventory Management & Stock Control

## A.1.1 Self-Reflection

My role on the iWear project was to design and deliver the inventory management subdomain. That meant owning the catalog tables (`product_categories`, `product_brands`, `product_types`, `products`, `product_variants`, `product_images`, `addons`, `addon_options`), the warehouse and supplier tables, the stock movement model, and the entire administrative back-office surface for products and addons. By the end of the project the inventory module accounted for roughly a quarter of the backend's lines of code and a similar share of the React admin pages.

The most valuable lesson I learned was the difference between a system that *records* stock and a system that *understands* stock. My first instinct was to put a single `quantity` column on the `products` table. The literature I read for Chapter 2 — and a sharp question from my supervisor in week three — convinced me that this would not survive contact with real operational data. I reworked the schema to use a `stock_movements` table with explicit IN/OUT events and added the `inventory_service.get_current_stock` helper that derives the on-hand quantity from the movements rather than from a denormalised counter. The legacy `quantity` column is still on the `products` table for compatibility and for fast list endpoints, but every write path goes through movements. Doing this rework cost me a week, but it is the change I am most proud of because it is the difference between an academic prototype and something that an actual optical retailer could trust.

My main strengths during the project were patience with database design and comfort with SQLAlchemy. My main challenges were front-end work — I am a more confident backend engineer, and the admin product form took me longer than I expected because I had to learn React state patterns from scratch. My teammates were patient with me on this, and pair-programming the image upload component with Member 4 was one of the highlights of the semester. The skills I developed most were declarative SQL design, Alembic migration authoring and React form state management.

If I were to start the project again, I would build the seed data first instead of last. Several of the bugs I chased in week six turned out to be my admin pages not handling missing relationships, and a richer seed would have surfaced those bugs in week one.

## A.1.2 Critical Appraisal

The inventory module meets the functional requirements in Table 3.1 (FR-1, FR-2, FR-3) and the non-functional requirements that apply to it (NFR-3 and NFR-4). The double-write between `quantity` and `stock_movements` is a deliberate compromise: it accelerates the most common read path (catalog listing) at the cost of a tiny risk of drift if a movement is recorded outside the service layer. I judged this acceptable because the only writers in the current codebase are the service layer and the seed script.

The biggest weakness of my work is that the warehouse subsystem is modelled but barely surfaced in the admin UI. The `Supplier` and `Warehouse` tables are first-class, but the React back office only exposes a thin warehouse list — there is no UI for purchase orders, goods receipts or stock adjustments. I underestimated how long the catalog admin pages would take and ran out of time. The literature on SME inventory systems (OECD, 2021) is clear that this is exactly the area where SME tools tend to fall over, so my honest appraisal is that this gap is the single biggest hole in my contribution and is the first thing I would close in a follow-on iteration.

A second, smaller weakness is that the addon group system is product-category bound rather than product-bound. This is good for the common case (lens options apply to all frames) but it means that two frames in the same category cannot expose different addon groups. I would refactor this to a many-to-many association if I had a second pass.

Overall, I judge my contribution to be solid on the schema and CRUD layers and weaker on the operational UX layers. The schema decisions will outlast the prototype; the missing UI screens are recoverable in a single sprint.
