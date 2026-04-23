# Appendix A.2 — Individual Section: Member 2

**Name:** [Member 2 Name]
**Banner ID:** [Banner ID 2]
**Project area:** E-commerce Customer Experience & Customisation

## A.2.1 Self-Reflection

I was responsible for the customer-facing storefront: product browsing, the product detail page, the cart, the checkout flow, the order history page, the prescription capture form and most of the storefront-side React state. My contribution sits squarely on the `frontend/src/pages/ProductList.jsx`, `ProductDetail.jsx`, `Cart.jsx`, `Checkout.jsx`, `OrderConfirmation.jsx`, `OrderHistory.jsx`, `Login.jsx` and `Register.jsx` files, with backing route changes in `backend/app/routes/sales.py`.

The hardest part of my work was the addon system on the product detail page. Eyewear customisation is conceptually simple — pick a frame, pick a lens type — but the addon group UI has to handle optional groups, required groups, multi-step selections, image uploads for some addons (e.g. uploaded prescriptions) and a running price total. I went through three rewrites before settling on the collapsible-section pattern that ships in `ProductDetail.jsx`. Each rewrite taught me something different. The first rewrite taught me that I had to keep the selected option ids in a single object keyed by addon id, not in nested arrays. The second taught me that the running total needed to be derived from selection state, not stored as a separate piece of state. The third — the one that survived — finally collapsed cleanly enough that the v2 UI redesign could re-style it without touching the underlying logic.

The skills I developed most were React state management, controlled forms and the discipline of separating presentation from data flow. Before this project I would have written the addon UI as one big component with everything coupled together; the third rewrite taught me to factor it into a small number of pure-view child components and let the parent own the state. The literature review nudged me towards this when I noticed how often SME systems collapse under their own UI complexity when domain-specific forms are involved (Chapter 2.3).

My main weakness was that I over-relied on the design that came from the previous iteration. My pages were functional but visually unremarkable, and when the v2 design upgrade landed in the last week I realised how much further the storefront could have gone if I had pushed harder on visual polish from the beginning. The new hero, filter sidebar and product cards belong to the joint v2 effort and I learned a lot watching them come together.

I learned a great deal about how React Router's nested routes interact with shared layout state, and about how to centralise an API client so that authentication headers are not duplicated in every page. I am also more confident about reading academic papers on user experience and translating their lessons into concrete UI choices.

## A.2.2 Critical Appraisal

My module meets FR-4 through FR-9 in Table 3.1. The customer can browse, search, filter (after the new backend filter parameters), view a product detail page, configure addons, manage a cart and place a cash-on-delivery order. Both guest and authenticated checkout flows work, and prescription data is captured into the database tables that Member 1 designed.

The honest weakness in my work is that the prescription capture UI is currently rendered inline on the product detail page rather than as a dedicated step in the checkout flow. The data flows correctly into `prescription_records` and `prescription_details`, but the UX is not as guided as I would like. Optical retail customers are typically nervous about prescription data; a dedicated, clearly-labelled step would reassure them. I would also add front-end validation (axis between 0 and 180, sphere between -20 and +20) which the schema accepts but the UI does not currently enforce.

A second weakness is test coverage. None of my React components have unit tests. I made the conscious choice to spend my limited time on functional polish rather than React Testing Library scaffolding, but in a real production setting this would not be defensible. Adding RTL tests for the addon selection state machine would be the highest-value follow-up.

A third area where my work could improve is accessibility. The product detail page passes the basics — semantic headings, alt text on images, form labels — but I have not run a full WCAG 2.1 audit (W3C, 2018). For an SME selling to an audience that includes many older customers, this is a real gap.

Overall, I am pleased with the functional completeness of the customer flow and disappointed only that I did not push the visual polish and accessibility further. The decisions I made will hold up under inspection; the gaps I left are clearly documented and can be closed quickly in a follow-on iteration.
