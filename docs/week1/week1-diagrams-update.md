# Week 1 – Diagrams & updates (ChatGPT ke liye detail)

**Purpose:** Is file mein **har woh cheez detail se** likhi jati hai jo hum Week 1 (aur agay) diagrams / structure ke sath karte hain. ChatGPT ko ye file de do to wo poora context samajh kar commands aur next steps bata sake. **Har update ke baad is file ko update karte raho.**

**Project:** iWear (eyewear ecommerce)  
**Repo path:** `c:\Ali\Webapps\eyewear ecommerce`  
**Environment:** Windows, PowerShell. (Ubuntu pe bhi same structure, commands thode alag.)

---

## 1. Branches (Week 1 diagrams)

| Branch | Status | Kaam |
|--------|--------|------|
| **feature/week1-diagrams** | Active – yahi use kiya | Week 1 architecture diagram, docs/week1/ files |
| **week1-diagrams** | Deleted | Pehle banayi thi, phir delete kar di (duplicate thi) |

**Current branch for diagrams:** `feature/week1-diagrams`. Naya diagram ya Week 1 doc isi branch par add karo.

---

## 2. Files banaye / update kiye (Week 1)

### 2.1 Architecture diagram

- **Path:** `docs/week1/architecture_diagram.md`
- **Title:** iWear System Architecture – Week 1
- **Format:** Mermaid (flowchart)
- **Branch:** feature/week1-diagrams
- **Commit:** Add Week 1 architecture diagram (Mermaid) - three-tier, React/Flask/PostgreSQL, AI assistant

**Kya hai is file mein:**
- **Three-tier architecture:**
  - **Tier 1 – Presentation:** User, React Frontend (Browser). User React use karta hai.
  - **Tier 2 – Application:** Flask Backend API, AI Business Insights Assistant. AI sirf backend ke through kaam karta hai (Flask <-> AI).
  - **Tier 3 – Data:** Docker container ke andar PostgreSQL. Flask DB ko query karta hai.
- **Request flow:** User → React → Flask API → PostgreSQL (solid arrows). AI ka DB tak koi direct link nahi; AI "uses backend only" (Flask).
- **Docker:** PostgreSQL Docker image (postgres:16-alpine) mein chalti hai; host port 5433 (project mein 5432 conflict avoid karne ke liye 5433 use kiya).
- **Colors:** Tier1 blue-ish, Tier2 purple-ish, Tier3 green-ish, Docker orange-ish (Mermaid style).

**Request flow (short):**
1. User → React → Flask → PostgreSQL (data)
2. AI Assistant backend layer mein; DB tak sirf Flask ke through
3. Docker sirf PostgreSQL container ke liye

### 2.2 Business process flow

- **Path:** `docs/week1/business_process_flow.md`
- **Title:** iWear End-to-End Business Workflow – Week 1
- **Format:** Mermaid flowchart TD (top-down)
- **Branch:** feature/week1-diagrams

**Kya hai is file mein (4 flows):**
1. **Procurement:** Supplier → Purchase Order → Stock In → Stock Ledger Update
2. **Sales:** Customer → Product Selection → Prescription Entry → Sales Order → Payment → Stock Deduction → Accounting Entry
3. **Finance:** Voucher Creation → Ledger Posting → Financial Reporting
4. **AI Reporting:** Business User → Natural Language Query → Intent Detection → SQL Query → Report Output

Har flow alag subgraph mein; neeche flow summary table bhi hai.

### 2.3 High-level ER diagram

- **Path:** `docs/week1/high_level_erd.md`
- **Title:** iWear High-Level ER Design – Week 1
- **Format:** Mermaid erDiagram
- **Branch:** feature/week1-diagrams

**Entities:** User, Role, UserRole, ProductCategory, ProductBrand, ProductType, Product, ProductVariant, StockLedger, Customer, Supplier, SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem, Payment, PaymentMethod, Account, Voucher, VoucherLine, Prescription.

**Relationships (summary):** Product → Category, Brand, Type; Product → many ProductVariant; ProductVariant → StockLedger; SalesOrder → many SalesOrderItem; PurchaseOrder → many PurchaseOrderItem; Voucher → many VoucherLine; UserRole links User and Role. Neeche relationship summary table bhi hai.

---

## 3. Project structure (relevant for Week 1)

```
eyewear ecommerce/
  docs/
    week1/
      architecture_diagram.md   ← Mermaid three-tier diagram
      business_process_flow.md  ← Mermaid business workflow (4 flows)
      high_level_erd.md         ← Mermaid ER (entities + relationships)
      week1-diagrams-update.md  ← Ye file (ChatGPT detail)
  docker-compose.yml           ← DB: postgres:16-alpine, port 5433
  backend/
    app/, run.py, manage.ps1, migrations/, .env.example
  CHATGPT_PROGRESS.md          ← Overall project progress (commands, setup)
  DEV_SETUP.md                 ← How to run backend + frontend
```

---

## 4. Backend / DB (jo Week 1 se use ho raha hai)

- **Flask:** App factory, health route `/api/health`, extensions (db, migrate, bcrypt, jwt, cors).
- **DB:** PostgreSQL, Docker se `docker compose up -d`, port 5433, DB name `iwear_dev`, user/pass postgres/postgres.
- **Models:** User, Role, UserRole, ProductCategory, ProductBrand, ProductType, Product, Stock. Migrations: `backend/migrations/versions/` (001_initial, 5ad279ea8cae init schema).
- **Commands:** `.\backend\manage.ps1 start-db`, `upgrade`, `python backend\run.py`. (Detail CHATGPT_PROGRESS.md mein.)

---

## 5. Agay kya karna hai / Updates (yahan add karte raho)

- [ ] Frontend (React) add karna jab start karo – same architecture diagram ke hisaab se React tier.
- [ ] AI Business Insights Assistant implement karna – backend layer mein, DB sirf Flask ke through.
- [ ] Naye diagrams (e.g. ERD, sequence diagrams) agar banaye to isi section mein file path aur short description add karo.
- [ ] Koi bhi naya Week 1 (ya diagrams) ka kaam – date ke sath isi file mein detail likh do taake ChatGPT ko pata rahe.

**Template for new entry:**
```text
### [Date] – [Short title]
- Kya kiya: ...
- Files: ...
- Branch: ...
- Commands (agar relevant): ...
```

---

## 6. ChatGPT ko kaise use karo

1. Is file (**week1-diagrams-update.md**) ko ChatGPT ko paste karo ya attach karo.
2. CHATGPT_PROGRESS.md bhi de do agar commands / setup chahiye.
3. Kehna: "Is hisaab se [X] karo" ya "Is architecture ke mutabiq next step batao".
4. Jab kuch naya karo (diagram, branch, file) to is file ke **Section 5 (Agay kya karna hai / Updates)** ya relevant section mein detail add kar do taake next time ChatGPT updated context use kare.

---

**Last updated:** Week 1 architecture diagram add (feature/week1-diagrams); week1-diagrams branch delete; ye file create – ChatGPT ke liye detail doc. Agay har change yahan add karte rahenge.
