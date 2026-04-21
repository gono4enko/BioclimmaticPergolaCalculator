# Биоклиматический Калькулятор Пергол

## Overview
This project is a bilingual (Russian) web application for calculating the cost of bioclimatic pergolas. It serves as a comprehensive tool for generating commercial offers, managing pricing, and streamlining the sales process for various pergola types, including advanced glazing options. The application aims to provide accurate pricing, detailed specifications, and visually appealing proposals to potential customers.

## User Preferences
I prefer clear, concise language. Please ensure that all explanations are straightforward and easy to understand. I appreciate an iterative development approach, where changes are introduced gradually and discussed. Before making any major architectural changes or significant modifications to core business logic, please ask for my approval. I expect the agent to maintain the existing file structure and naming conventions unless explicitly instructed otherwise.

## System Architecture
The application is built on a Flask backend (`flask_app/`) served by Gunicorn on port 5000. It provides both a web-based calculator interface and a robust API for calculations and PDF generation.

**Key Architectural Components:**
-   **Flask Application:** Handles main routing, API endpoints, and HTML page rendering.
-   **Gunicorn:** Production server for the Flask application with 2 workers and a 120-second timeout.
-   **Database:** PostgreSQL is used for storing price data, leads, and administrative configurations, with a fallback to CSV files for pricing.
-   **PDF Generation:** Uses `fpdf2` for creating detailed commercial offers in PDF format, supporting Cyrillic characters and dynamic content.
-   **Admin Panel:** A secure `/admin` interface for managing prices, parsing price lists from images using Claude Vision, and monitoring system health.
-   **Marketing & Sales Features:**
    -   Dynamic commercial offer generation with unique IDs and QR codes.
    -   Integration of marketing content (descriptions, features, benefits) via `decolife` data.
    -   Web-based interactive commercial proposals with multiple blocks (hero, pricing, features, gallery).
    -   Dynamic counter for installations and promotional badges.
-   **Business Logic:**
    -   Complex pricing calculation based on pergola type, dimensions, lamella size, and selected variants (Basic/Light/Pro).
    -   Consideration of modules, additional columns, drainage enhancers, drives (Bansbach, Somfy), remote controls (Simu), and LED lighting.
    -   Pricing adjustments for delivery and installation, and final pricing options (Cash, Bank Transfer, VAT inclusive).
    -   Specialized pricing logic for B500/B700 variants and B600/B200 types, including `get_best_variant_price()` for auto-selection.
    -   Support for "Modification Step 2" to compare different variants with technical specifications.
-   **UI/UX:**
    -   Bootstrap 5 for responsive design.
    -   Hero section with parallax effect and promotional elements.
    -   Interactive forms with client-side JavaScript for calculations.
    -   SVG diagrams for top-view schematics in PDFs.
    -   Yandex Metrika integration for analytics.
-   **Multi-Pergola КП (composite offers):**
    -   Step 3 supports adding multiple pergolas (≥2) into a single commercial offer with per-pergola model/dimensions/openings/options/installation/LED state preserved via tabs in Step 4.
    -   `/api/calculate` is invoked in parallel (Promise.all) per pergola; results page shows a summary block with per-pergola rows + Grand Total (cash / non-cash / VAT).
    -   `/api/export-pdf` accepts `mode: 'multi_pergola'` with `pergolas: [...]` and produces a single PDF: a summary cover page (composition table + grand totals) followed by a full commercial offer per pergola, concatenated via PyPDF2 (`PdfMerger`). КП number appears only on the summary cover.
    -   Single-pergola flow and the existing variant-comparison `mode: 'all'` are unchanged.
-   **Glazing System (W-Series):**
    -   Models: W500 (20mm double glazing), W600 (28mm), W700 (thermal break, 28mm).
    -   Configuration options: sash count, profile color, glass type, "fin" option.
    -   Automatic drive selection (SIMU/SOMFY) based on dimensions and tandem mode requirements.
    -   Integration with remote control channels.

## External Dependencies
-   **PostgreSQL:** Database for persistent storage of prices, leads, and system settings.
-   **Gunicorn:** WSGI HTTP server for production deployment.
-   **fpdf2:** Python library for PDF document generation.
-   **Claude Vision (Anthropic API):** Used for optical character recognition (OCR) to parse price lists from images in the admin panel.
-   **APScheduler:** For scheduling background tasks like calculation cleanup.
-   **Yandex Metrika:** Web analytics service for tracking user interactions and goals.
-   **Bootstrap 5:** Frontend framework for responsive design and UI components.