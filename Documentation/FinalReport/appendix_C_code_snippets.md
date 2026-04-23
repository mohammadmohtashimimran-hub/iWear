# Appendix C — Annotated Code Snippets

This appendix collects the most important code snippets from across the iWear codebase, with a brief explanation of each. Snippets are provided for the supervisor's "code snippets with brief explanation" requirement and are deliberately short — full source files live in the repository at the indicated paths.

## C.1 RBAC Decorator

**File:** `backend/app/auth/decorators.py`

```python
def require_permission(code: str):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None:
                return jsonify({"error": "auth required"}), 401
            granted = {p.code for r in user.roles for p in r.permissions}
            if code not in granted:
                return jsonify({"error": "forbidden", "needed": code}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

The decorator is the project's single point of authorisation enforcement. Every protected endpoint composes `@jwt_required()` (provided by Flask-JWT-Extended) with `@require_permission("permission_code")`. The permission set is computed by joining through the role-permission matrix; missing the required code returns 403. *(Reference screenshot: open `backend/app/routes/inventory.py` and observe how each write endpoint stacks the decorator.)*

## C.2 Filtered Public Product List

**File:** `backend/app/routes/sales.py`

```python
@sales_bp.get("/products")
def list_products():
    page = request.args.get("page", 1)
    per_page = request.args.get("per_page", 20)
    category_id = request.args.get("category_id", type=int)
    brand_id = request.args.get("brand_id", type=int)
    type_id = request.args.get("type_id", type=int)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = (request.args.get("sort") or "").strip().lower()
    search = (request.args.get("search") or "").strip()

    q = Product.query.filter(Product.active.is_(True))
    if category_id is not None: q = q.filter(Product.category_id == category_id)
    if brand_id is not None:    q = q.filter(Product.brand_id == brand_id)
    if type_id is not None:     q = q.filter(Product.type_id == type_id)
    if min_price is not None:   q = q.filter(Product.price >= min_price)
    if max_price is not None:   q = q.filter(Product.price <= max_price)
    if search:                  q = q.filter(Product.name.ilike(f"%{search}%"))
    if sort == "price_asc":     q = q.order_by(Product.price.asc().nullslast())
    elif sort == "price_desc":  q = q.order_by(Product.price.desc().nullslast())
    elif sort == "newest":      q = q.order_by(Product.id.desc())
    else:                       q = q.order_by(Product.id)
```

The handler composes filter parameters incrementally onto the SQLAlchemy query, applies pagination and serialises the result with the variant and primary-image data the storefront needs. The filter coverage is exercised by the unit tests in `backend/tests/test_sales_filters.py`.

## C.3 Double-Entry Voucher Posting

**File:** `backend/app/services/finance_service.py`

```python
def create_voucher(voucher_type, entries, reference_type=None, reference_id=None):
    debit_total  = sum(Decimal(e["debit"])  for e in entries)
    credit_total = sum(Decimal(e["credit"]) for e in entries)
    if debit_total != credit_total:
        raise ValueError("voucher unbalanced: debit %s vs credit %s" % (debit_total, credit_total))
    voucher = Voucher(
        voucher_type_id=voucher_type.id,
        voucher_number=_next_voucher_number(),
        voucher_date=date.today(),
        reference_type=reference_type,
        reference_id=reference_id,
    )
    db.session.add(voucher)
    db.session.flush()
    for e in entries:
        db.session.add(VoucherEntry(voucher_id=voucher.id, **e))
    db.session.commit()
    return voucher
```

The function enforces the double-entry invariant before any rows are written. `post_cod_sale`, `post_purchase` and `post_expense` are thin wrappers that build the appropriate entry list and delegate here. The unit test `tests/test_finance.py::test_voucher_raises_when_unbalanced` proves the invariant.

## C.4 AI Intent Detection

**File:** `backend/app/services/ai_assistant_service.py`

```python
def detect_intent(query_text):
    normalized = normalize(query_text)
    if not normalized:
        return None
    words = set(normalized.split())
    best, best_score = None, 0
    for intent in ReportingIntent.query.all():
        for kw in intent.intent_keywords:
            kw_lc = normalize(kw.keyword)
            if kw_lc in normalized or kw_lc in words or any(w in kw_lc for w in words):
                score = len(kw_lc) if len(kw_lc) > best_score else 0
                if score > best_score:
                    best_score, best = score, intent
        if normalize(intent.name) in normalized or normalize(intent.code) in normalized:
            if 3 > best_score:
                best, best_score = intent, 3
    return best
```

The matcher iterates through every reporting intent, checks each of its keywords against the normalised user text and tracks the longest match. The intent's own name and code are also matched as a fall-back. Six unit tests in `backend/tests/test_ai_assistant.py` cover positive paths, the no-match path and downstream formatting.

## C.5 Safe Predefined Query Execution

**File:** `backend/app/services/ai_assistant_service.py`

```python
def run_predefined_query(intent_id):
    pq = PredefinedQuery.query.filter_by(reporting_intent_id=intent_id, active=True).first()
    if not pq or not pq.sql_template:
        return None, None
    sql = pq.sql_template
    for key, val in get_safe_params().items():
        sql = sql.replace("{{" + key + "}}", str(val))
    if not sql.strip().upper().startswith("SELECT"):
        return None, None
    try:
        result = db.session.execute(text(sql))
        return [list(r) for r in result.fetchall()], list(result.keys() or [])
    except Exception:
        return None, None
```

The function only accepts statements that start with `SELECT`, only substitutes values from a whitelisted parameter map (`today`, `year`, `month`, `day`) and is wrapped in a defensive try/except so a malformed admin-curated template cannot crash the request. User text is never concatenated into the SQL string.

## C.6 React API Client Helper

**File:** `frontend/src/api.js`

```js
export async function aiQuery(query) {
  const r = await fetch(`${API}/ai-assistant/query`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({ query }),
  })
  if (!r.ok) await _apiError(r, 'AI query failed')
  return r.json()
}
```

The frontend's API client centralises every backend call. `getAuthHeaders` injects the JWT, `_apiError` standardises error parsing, and the resulting helpers are the only thing that React components ever touch. Adding the AI page in this iteration was therefore a single helper plus a new component, with no other client-side glue required.

## C.7 AI Insights Chat Component

**File:** `frontend/src/pages/admin/AdminAIInsights.jsx` (excerpt)

```jsx
const send = async (text) => {
  const q = (text ?? input).trim()
  if (!q || busy) return
  setMessages(m => [...m, { role: 'user', text: q }])
  setInput('')
  setBusy(true)
  try {
    const res = await aiQuery(q)
    setMessages(m => [...m, {
      role: 'bot',
      text: res.summary || 'No response',
      table: res.table,
      intent: res.intent,
    }])
  } catch (e) {
    setMessages(m => [...m, { role: 'bot', text: `Error: ${e.message}`, error: true }])
  } finally {
    setBusy(false)
  }
}
```

The chat component keeps a messages array, appends a `user` message immediately on submit, calls `aiQuery`, then appends the `bot` response with both the natural-language summary and the structured table. The `busy` flag disables the input while the request is in flight. The full file lives at `frontend/src/pages/admin/AdminAIInsights.jsx`.

## C.8 Storefront Hero (JSX)

**File:** `frontend/src/pages/ProductList.jsx` (excerpt)

```jsx
<section className="hero">
  <div className="hero-inner">
    <div>
      <span className="hero-eyebrow">New Collection · 2026</span>
      <h1>See the world clearly. In style.</h1>
      <p>{storeName} brings you premium eyewear with prescription customisation, expertly crafted lenses, and cash-on-delivery convenience.</p>
      <div className="hero-actions">
        <a href="#shop" className="btn btn-primary">Shop frames</a>
        <Link to="/size-guide" className="btn btn-secondary">Find your fit</Link>
      </div>
    </div>
    <div className="hero-visual"><div className="hero-visual-frame"><HeroSvg /></div></div>
  </div>
</section>
```

The hero is implemented as a single section bound to the design tokens defined in `frontend/src/index.css`. Because the design system is layered, no other JSX file needed to change to absorb the new visual identity.
