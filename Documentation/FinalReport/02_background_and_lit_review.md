# Chapter 2 — Background and Literature Review

## 2.1 Introduction

The literature review situates the iWear project within four related streams of academic and industry work: digital transformation in SME retail, eyewear-specific information systems, modular service-oriented web architectures, and natural-language access to business data. The review draws on the project's own *Literature Review* document and on widely cited public sources to identify the gap that iWear addresses.

## 2.2 Digital Transformation in SME Retail

The shift from manual record-keeping to integrated digital systems is well documented across the retail literature. Studies of SME adoption (e.g. OECD, 2021) consistently find that small retailers struggle to invest in enterprise-grade ERP solutions and instead rely on fragmented combinations of spreadsheets, point-of-sale (POS) hardware and consumer cloud services. The same studies report that this fragmentation directly contributes to inventory inaccuracies, delayed reporting and reduced customer trust. The need is therefore not for *more* features, but for *integrated* features delivered at a price and complexity that match SME constraints.

Several authors emphasise that successful SME systems share three properties: low total cost of ownership, modular extensibility, and data consolidation across the operational subdomains (sales, inventory, finance, customer). iWear is designed against this background — it deliberately avoids bespoke enterprise integrations and instead packages a coherent set of subdomains within a single open codebase.

## 2.3 Eyewear Retail as a Distinct Domain

Eyewear retail differs from generic retail in three ways. First, products are highly variable: a single frame may exist in many colours and sizes, and a single sale may include lens choices that are themselves parameterised by index, coating and prescription. Second, prescription data is medical in nature and demands accurate capture and storage. Third, the customer journey often spans an in-store fitting and an online or off-site lens fulfilment step. None of these properties are first-class in mainstream e-commerce platforms, which typically model only generic product variants and rely on free-text fields or manual phone follow-ups for prescriptions.

A small body of academic work has examined optical retail information systems specifically. These studies argue that without prescription-aware data models, the resulting systems force users to bypass the software for the parts of the workflow that matter most — exactly the integration failure that the literature on SME digital transformation warns against.

## 2.4 Modular Web Architectures

The transition from monolithic web applications to modular and service-oriented architectures is a long-running theme in the software engineering literature. Modular systems offer scalability, maintainability and the ability to evolve subdomains independently, but at the cost of increased integration complexity, eventual consistency issues and the need for stricter API contracts.

For the SME context that iWear targets, full microservice architectures are usually disproportionate. The literature suggests a middle path: a *modular monolith* where blueprints, packages or modules represent subdomains within a single deployable artefact. This pattern preserves architectural separation while keeping deployment, monitoring and authentication simple. iWear adopts this pattern explicitly: each Flask blueprint represents a subdomain (auth, sales, inventory, finance, AI, settings), but the entire backend ships as one Flask app.

## 2.5 Authentication, Authorisation and Audit

JSON Web Tokens (JWT) and role-based access control (RBAC) are now standard for stateless API security. The literature highlights the importance of granular permissions over coarse role checks, particularly in multi-user retail environments where finance, inventory and sales staff need different rights. iWear implements a permission code system (`inventory:read`, `finance:post`, `ai:query`, etc.) inspired by these recommendations and exposes a `require_permission` decorator that wraps every protected endpoint.

Audit logging is similarly emphasised in security literature. Sales and finance events in particular benefit from immutable trails. iWear includes an `audit_logs` table for action tracking and an `assistant_query_logs` table that records every AI query with its outcome.

## 2.6 Natural Language Interfaces to Databases

Natural-language interfaces to databases (NLIDBs) are an active research area. Early NLIDBs relied on grammar parsing and keyword matching; recent work uses transformer language models to translate questions directly into SQL. Production systems often combine the two approaches, using machine learning to interpret intent and predefined SQL templates to safeguard against injection or runaway queries.

For iWear, the AI assistant is deliberately scoped to the *predefined query* end of this spectrum. Each business question is mapped to a curated SQL template parameterised only with safe internal values such as the current date. This trades broad linguistic coverage for predictability and safety — a sensible trade-off for an SME tool that must be maintainable by a small team. Future work (Chapter 8) discusses how a transformer-based intent classifier could replace the keyword matcher without changing the safe-query backend.

## 2.7 Double-Entry Accounting in SME Software

Accounting literature is unanimous that double-entry bookkeeping is the appropriate model for any system that posts financial transactions. The principle is simple — every voucher must balance debits against credits — but the implications for software design are non-trivial: the schema must support multiple entries per voucher, validate balance on persistence, and produce reports such as trial balance and profit-and-loss from the underlying ledger rather than from sales metadata alone. iWear implements these requirements in its `finance_service` module, with `create_voucher` enforcing balance and `post_cod_sale` automatically generating the appropriate entries when an order is placed.

## 2.8 Identified Gap

Putting these strands together, the literature confirms that:

1. SME eyewear retailers need a single integrated system, not a constellation of tools.
2. Eyewear-specific entities (prescriptions, lens parameters, frame variants) must be modelled natively.
3. Modular monolith architectures are well suited to SME constraints.
4. RBAC and audit are non-negotiable for retail operations that touch finance.
5. Natural-language interfaces are valuable for non-technical users, provided that safety is engineered into the query layer.

iWear is the project's attempt to combine all five into a single coherent codebase, and the rest of this report describes how that combination was specified, designed, implemented, tested and evaluated.
