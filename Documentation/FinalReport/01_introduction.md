# Chapter 1 — Introduction

## 1.1 Context and Motivation

Digital transformation has become a defining characteristic of contemporary retail. Customers now expect to discover products online, compare prices, customise their purchases and receive support through digital channels. For retailers, web-based systems offer benefits that go beyond a single sales channel: real-time stock visibility, integrated accounting, customer analytics, and the ability to respond quickly to demand patterns. Yet this shift is uneven. Large enterprises invest in expensive enterprise resource planning (ERP) systems, while many small and medium-sized enterprises (SMEs) still depend on a patchwork of spreadsheets, paper records and consumer-grade tools. The eyewear sector is a particularly clear example of this gap: optical retailers manage prescription data, frame variants, lens options and stock locations in environments where data accuracy is critical for customer health and operational efficiency.

Generic e-commerce platforms (Shopify, WooCommerce and similar) offer broad coverage of common retail flows but rarely model eyewear-specific concepts such as prescriptions, lens indices and frame measurements. Conversely, enterprise optical software is typically expensive, hard to customise and inaccessible to independent retailers. The result is an unmet need for a lightweight, domain-aware system that combines storefront capabilities with operational management tools at a cost and complexity that suit SMEs.

## 1.2 Project Aim

The aim of this project is to design and implement *iWear*, an AI-enabled web-based eyewear inventory and e-commerce management system that unifies stock control, an online storefront, prescription-aware product customisation, double-entry finance and a natural-language business insights assistant within a single, modular web platform.

## 1.3 Objectives

To meet this aim, the project pursued the following measurable objectives:

1. Analyse the requirements of an SME eyewear retailer and translate them into functional and non-functional specifications.
2. Design a normalised relational database that captures eyewear-specific entities (frame types, lens types, lens indices, prescriptions) alongside generic e-commerce entities (carts, orders, payments).
3. Implement a Flask REST API exposing role-based endpoints for catalog, inventory, sales, finance, settings and AI assistant operations.
4. Implement a React single-page application that delivers a polished customer storefront and a complete administrative back office.
5. Implement an AI Business Insights Assistant that maps natural-language queries to safe predefined SQL templates.
6. Validate the system through automated unit/integration tests and manual scenarios that exercise the end-to-end customer journey.
7. Document the design, implementation and evaluation in a structured academic report aligned with the supervisor's recent guidance.

## 1.4 Scope

The system is scoped as a functional prototype that demonstrates a credible end-to-end retail experience. The storefront supports browsing, searching and filtering products, managing a cart, customising lens options, capturing prescription data where required, and placing cash-on-delivery orders. The admin portal enables product, addon, customer, order, country and order-status management as well as access to the AI assistant. Online payment integration, courier APIs, full multi-tenant support and machine-learning intent classification are explicitly out of scope and discussed as future work.

## 1.5 Group Project Structure

The project is delivered by a team of four MSc students. Member 1 leads inventory management and stock control, including the catalog admin portal and stock movement schema. Member 2 leads the customer e-commerce experience, including product detail, cart, checkout and prescription capture. Member 3 leads the AI Business Insights Assistant, including intent definitions, the keyword matcher and the chat interface. Member 4 leads system integration, RBAC, security, deployment and the architectural artefacts. The four streams are coordinated through a shared Git workflow on the branch `claude/eyewear-project-completion-UhFBd` and a common Flask + React codebase.

## 1.6 Report Structure

Chapter 2 surveys the academic and industry context. Chapter 3 derives requirements from the project specifications. Chapter 4 presents the system design and architecture. Chapter 5 describes the implementation, including code references, flowcharts and pseudocode. Chapter 6 covers testing. Chapter 7 reports results and discusses limitations. Chapter 8 concludes and outlines future work. References and appendices follow, including individual reflections and a process document.
