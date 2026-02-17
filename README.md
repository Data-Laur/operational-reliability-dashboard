# Operational Performance Audit: A Longitudinal Data Study
**Authored by Lauren | MS in Data Science, Boston University**

## 🎯 Project Objective
This dashboard serves as a "Subject Matter Expert" audit of 561 professional tasks executed between 2018 and 2026. This audit establishes a framework for service-level agreement (SLA) verification, translating qualitative client sentiment into actionable operational reliability metrics.

## 🚀 Live Demo
**[Launch the Dashboard](https://lauren-ops-audit.streamlit.app/)**

## 🛠️ Technical Implementation
**Framework: Streamlit (Python)** for high-performance, reactive front-end delivery.

**Analytical Engine: Altair** for declarative statistical visualization, ensuring mathematical validity in trend analysis.

**Data Integrity:** Implemented a **Schema-First** pipeline. While the raw taskrabbit_reviews.csv is restricted for **PII Compliance**, a taskrabbit_reviews_TEMPLATE.csv is provided to demonstrate the architectural requirements of the regex-based parsing engine.

**Optimization:** Engineered for minimal **Inference Latency** by utilizing static data structures, bypassing the overhead of traditional database connections for a more **Green AI** footprint.

## System Design & Optimization:

Inference Latency: Optimized data loading via pandas with explicit dtypes to reduce memory overhead.

Agentic Readiness: Structured the data pipeline to support future integration with LLM-based sentiment analysis agents.

## 📝 Data Governance & Sample Selection  
To ensure the highest level of Data Integrity, this audit utilizes a verified sample of 190 text-based reviews—representing 100% of the qualitative data accessible for external export. While the host platform tracks 319 total ratings and 561 lifetime tasks, I chose to isolate the text reviews to perform a deeper longitudinal study of client sentiment and operational reliability. This methodology allows for a transparent 'subject matter expert' deep dive while maintaining strict compliance with the data available through platform constraints.

Note: The raw taskrabbit_reviews.csv is excluded from this public repository to maintain strict PII compliance. A template.csv is provided to demonstrate the required schema for the data pipeline."

## ♿ Accessibility (A11y) & Inclusive Design
This project was built with a "Privacy & Inclusion First" mindset:
- **Screen Reader Optimized:** Implemented WAI-ARIA labels and semantic HTML landmarks for 100% blind-user compatibility.
- **Cognitive UX:** High-contrast typography (Figtree) and color-blind friendly palettes (Indigo/Slate).
- **System Messaging:** Strategic isolation of null values to prevent data leakage and maintain "Sure Bet" hiring signals.

## 🌿 Green AI & Sustainability
I prioritized Algorithmic Efficiency by architecting this dashboard as a green energy solution. Instead of utilizing energy-intensive LLM inference or high-frequency API polling, I engineered a Lean Architecture using static regex-based parsing and declarative visualizations. This approach minimizes the carbon footprint of the application and reduces compute costs, demonstrating my commitment to Green AI principles and sustainable engineering in a production environment.
