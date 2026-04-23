# iWear

## An AI-Enabled Web-Based Eyewear Inventory and E-Commerce Management System with an AI Business Insights Assistant

### MSc Masters Project — Final Report

Supervisor: Tariq Alsboui

Group members:

- [Member 1 Name] — [Banner ID 1] — Inventory Management & Stock Control
- [Member 2 Name] — [Banner ID 2] — E-commerce Customer Experience & Customisation
- [Member 3 Name] — [Banner ID 3] — AI Business Insights Assistant
- [Member 4 Name] — [Banner ID 4] — System Integration, Security & Architecture

### Declaration of Originality and Use of Generative AI

We confirm that this report is the work of the named members above. All sources have been acknowledged and any use of generative AI tools is declared in the appropriate place. The contents have not been submitted, in whole or in part, for any other academic award.

### Abstract

The eyewear retail sector is shaped by a unique combination of medical and commercial requirements. Customers expect online catalogues, prescription customisation and fast checkout, while retailers need accurate stock tracking, accounting and decision support. Generic e-commerce platforms rarely satisfy both sides at once, and small and medium-sized optical retailers (SMEs) frequently rely on disconnected spreadsheets and ad-hoc tools. This project, *iWear*, designs and implements an integrated, modular web platform that unifies inventory management, an eyewear-aware e-commerce storefront, double-entry finance posting, role-based administration and a natural-language AI Business Insights Assistant. The system is built as a three-tier application using React, Flask and PostgreSQL, with JWT-based authentication, an Alembic-migrated database of forty tables and an extensible service layer. Eyewear-specific features such as frame and lens type catalogues, prescription capture and lens addons are first-class citizens of the data model. The AI assistant maps natural-language phrases to predefined safe SQL queries, enabling non-technical store owners to ask questions such as "sales today" or "monthly profit" and receive structured answers. Functional and unit tests, manual end-to-end scenarios and a redesigned user interface confirm that the system delivers the originally proposed scope. The report describes the requirements, design, implementation, testing, results and reflections of the four-member project team.

### Table of Contents

1. Introduction
2. Background & Literature Review
3. Requirements Analysis
4. System Design
5. Implementation
6. Testing
7. Results & Discussion
8. Conclusion & Future Work
9. References
- Appendix A — Individual Reflections (Members 1–4)
- Appendix B — Project Process Document
- Appendix C — Annotated Code Snippets

### List of Figures

- Figure 4.1 — System Architecture (three-tier overview)
- Figure 4.2 — Entity Relationship overview
- Figure 5.1 — Order Checkout Flow
- Figure 5.2 — Voucher Posting Flow
- Figure 5.3 — AI Intent Detection Flow
- Figure 5.4 — RBAC Request Flow
- Figure 7.1 — Storefront home page (placeholder for screenshot)
- Figure 7.2 — Admin AI Insights chat (placeholder for screenshot)

### List of Tables

- Table 3.1 — Functional Requirements
- Table 3.2 — Non-Functional Requirements
- Table 6.1 — Automated test coverage summary
- Table 7.1 — Functional acceptance scenarios
