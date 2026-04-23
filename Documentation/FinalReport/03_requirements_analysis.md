# Chapter 3 — Requirements Analysis

## 3.1 Stakeholders

The primary stakeholders of iWear are SME optical retailers (the store owner and operational staff), end customers shopping for eyewear and the project's academic supervisor. Each stakeholder group informs a distinct slice of requirements: store staff demand reliable operational tools, customers expect a polished and trustworthy storefront, and the supervisor expects clear academic documentation, evidence of testing and adherence to project guidelines.

## 3.2 Requirements Capture Method

Requirements were elicited from four sources: the shared *Project Specification* document, the four individual *Member 1–4 Project Specification* documents, supervisor conversations and the supplied *Literature Review*. Each source contributed a different lens. The shared specification framed the project's overall ambition. The individual specifications scoped each member's contribution. The supervisor's recent instructions clarified the report-level expectations: a system architecture section, key features with explanations, flowcharts or pseudocode for algorithms, code snippets with brief explanations, a results-and-discussion chapter and a conclusion-and-future-work chapter. The literature review supplied the academic framing.

## 3.3 Functional Requirements

Table 3.1 lists the functional requirements that the system must satisfy. They are grouped by subdomain and traced back to the responsible team member.

**Table 3.1 — Functional Requirements**

| ID | Requirement | Owner |
|----|-------------|-------|
| FR-1 | Manage product categories, brands, types, products and variants. | Member 1 |
| FR-2 | Maintain stock levels with movement-based tracking and low-stock thresholds. | Member 1 |
| FR-3 | Manage suppliers, warehouses and purchase orders. | Member 1 |
| FR-4 | Browse, search, filter and paginate the customer-facing product catalogue. | Member 2 |
| FR-5 | View a product detail page with image gallery, variants and addons. | Member 2 |
| FR-6 | Add items to a cart (guest or authenticated) and manage quantities/addons. | Member 2 |
| FR-7 | Capture customer details and ship-to address during checkout. | Member 2 |
| FR-8 | Place a cash-on-delivery order and view order confirmation/history. | Member 2 |
| FR-9 | Capture eyewear-specific data: frame type, lens type, lens index, lens coating and prescription values. | Member 2 |
| FR-10 | Maintain a chart of accounts and post double-entry vouchers automatically when an order is placed. | Member 4 |
| FR-11 | Produce trial-balance and profit-and-loss reports from the ledger. | Member 4 |
| FR-12 | Authenticate users with JWT, hash passwords with bcrypt, and enforce role-based permissions on every protected endpoint. | Member 4 |
| FR-13 | Audit user actions and AI assistant queries. | Member 4 |
| FR-14 | Accept natural-language business queries and return structured answers. | Member 3 |
| FR-15 | Allow administrators to manage reporting intents, keywords and predefined queries. | Member 3 |
| FR-16 | Provide store settings and master data (countries, cities, order statuses) via the admin portal. | Member 4 |

## 3.4 Non-Functional Requirements

**Table 3.2 — Non-Functional Requirements**

| ID | Quality attribute | Statement |
|----|-------------------|-----------|
| NFR-1 | Usability | The customer storefront and admin portal must be navigable on desktop and mobile breakpoints down to 360 px. |
| NFR-2 | Performance | Catalog list endpoints must respond in under one second for typical SME volumes (≤10 000 products). |
| NFR-3 | Security | All write endpoints must require JWT and an explicit permission. Passwords must be bcrypt hashed. The AI query layer must reject any non-`SELECT` SQL. |
| NFR-4 | Maintainability | The codebase must be organised into clearly named modules and use migrations for schema evolution. |
| NFR-5 | Portability | The system must run on PostgreSQL in production and SQLite in local development without code changes. |
| NFR-6 | Auditability | Every login and AI query must be logged with the actor and the outcome. |
| NFR-7 | Documentation | The repository must contain end-to-end setup, vendor handover and architecture documentation. |
| NFR-8 | Testability | Critical business logic must have unit or integration tests runnable with `pytest`. |

## 3.5 Use Cases at a Glance

The system supports two primary actors: the customer and the administrator. The customer browses products, manages a cart, places orders and views past orders. The administrator manages products, addons, customers, orders, masters, store settings and queries the AI assistant. Both flows are protected by JWT, with customer endpoints requiring storefront sessions and admin endpoints requiring an explicit permission code.

## 3.6 Constraints and Assumptions

The project assumes that:

- The store operates in a single currency at a time (multi-currency is out of scope).
- Online payments are not required: cash-on-delivery is the only payment method.
- Email and SMS notifications are not required for the prototype.
- A small set of demo products is sufficient for evaluation; the system does not need to be loaded with thousands of real records.

The project is also constrained by the academic timeline: development happens over a single semester with a four-person team, so scope reductions are accepted where the literature review supports them (notably the keyword-based AI assistant in place of an ML-based one).

## 3.7 Mapping Requirements to the Final Report

Each functional requirement maps to an implementation section in Chapter 5 and is exercised by either an automated test (Chapter 6) or a manual scenario in Chapter 7. This explicit mapping is what allows the discussion in Chapter 7 to claim that the project objectives have been met.
