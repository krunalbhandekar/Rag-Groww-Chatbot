# Problem Statement: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## Purpose

Build a **facts-only** FAQ assistant for mutual fund schemes, using **Groww** as the reference product context. For **this repo**, factual answers must be grounded in a **fixed corpus**: **exactly five** public mutual fund URLs on Groww (`groww.in`) listed under **Corpus definition** below—**no other URLs** for retrieval, citations, or linked responses unless that policy is reopened in docs.

It must **never** give investment advice, opinions, or recommendations. Every answer must be concise, accurate, cite a single authoritative link from that fixed set where a link is required, and stay within the compliance-minded rules below.

## Objectives

Design and ship a lightweight **Retrieval-Augmented Generation (RAG)** assistant that:

- Answers factual questions about mutual fund schemes covered by those five URLs.
- Runs only on curated content from **those five pages**.
- Returns short, **source-backed** replies.

## Target users

| Audience | Need |
| -------- | ---- |
| Retail investors | Compare schemes using facts shown on those pages |
| Customer support & content teams | Handle repetitive factual mutual fund queries |

## Scope

### 1. Corpus definition

- **One AMC:** HDFC Mutual Fund (schemes presented on Groww).
- **Five schemes**, with category diversity across the set (large-cap, mid-cap, focused / broad equity, ELSS).

**Exactly these URLs — exclusive corpus**

| Scheme (Groww) | URL |
| ---------------- | --- |
| HDFC Mid Cap Fund — Direct Growth | https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth |
| HDFC Equity Fund — Direct Growth | https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth |
| HDFC Focused Fund — Direct Growth | https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth |
| HDFC ELSS Tax Saver — Direct Plan Growth | https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth |
| HDFC Large Cap Fund — Direct Growth | https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth |

Do **not** ingest AMC PDF microsites, AMFI, SEBI, blogs, aggregators, or additional Groww paths beyond the URLs above unless the problem statement or architecture is deliberately revised.

### 2. Assistant behavior

**Answer factual questions only**, such as:

- Expense ratio  
- Exit load  
- Minimum SIP amount  
- ELSS lock-in period  
- Riskometer level  
- Benchmark index  
- Statement / tax download guidance **if** present on these pages  

**For every valid answer:**

- At most **3 sentences**
- Exactly **one** citation link, and it **must** be one of the corpus URLs listed above  
- Footer: `Last updated from sources: <date>`

### 3. Refusal handling

**Refuse** non-factual or advisory prompts, for example:

- “Should I invest in this fund?”  
- “Which fund is better?”  

**Refusal replies must:**

- Stay polite and explicit about the facts-only scope  
- If including a hyperlink, **only** link to **one** of the URLs from **Corpus definition** (scheme in context where possible)—never to off-list sources  

### 4. User interface (minimal)

- Welcome message  
- **Three** example questions  
- Visible disclaimer: **“Facts-only. No investment advice.”**

## Constraints

### Data and sources

- **Only** the five corpus URLs listed in **Corpus definition** for fetch, retrieval, citations, and bot-emitted links.  

### Privacy and security

Do **not** collect, store, or process:

- PAN or Aadhaar  
- Account numbers  
- OTPs  
- Email addresses or phone numbers  

### Content

- No investment advice or “best pick” language.  
- No performance comparisons or return calculations.  
- For performance-related questions, do **not** invent returns; steer to **verbatim** disclosures on corpus pages if present, otherwise decline numerically—with **only** one link from the corpus URL set  

### Transparency

- Answers stay short, factual, and checkable against the corpus.  
- Every answer includes **one** allowed source link and **last updated** context from snapshots.

## Deliverables

| Item | Contents |
| ---- | -------- |
| **README** | Setup steps, HDFC AMC + **exact five URLs**, RAG architecture overview, limitations of a five-page corpus |
| **Disclaimer** | Reuse: **“Facts-only. No investment advice.”** |

## Success criteria

- Factual information is retrieved **accurately** from corpus derived **only** from the five URLs.  
- Replies stay **facts-only**; advisory questions are **refused** consistently.  
- Citations are **valid**, **single-link**, drawn **only** from the fixed URL table.  
- UI is **minimal**, clear, and easy to use.

## Summary

The product goal is a **transparent, narrowly scoped** mutual fund FAQ: **traceability to a fixed five-URL corpus** over breadth of sources. Users get facts tied to those pages—not open-web or multi-source financial guidance.
