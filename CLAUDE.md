# CLAUDE.md

## Context
Home assignment for QA Engineer, Wix Domains team.
Four public "doors" answer "Can I get this name?":
1. Domain storefront - https://www.wix.com/domains
2. Business Name Generator - https://www.wix.com/tools/business-name-generator
3. WHOIS lookup - https://www.wix.com/domains/whois
4. Public Domain Search API - https://dev.wix.com/docs/api-reference/account-level/domains/domain-search/introduction

Deliverables: ARCHITECTURE.md, TEST_PLAN.md, FINDINGS.md, test code, README.md, AI_LOG.md.
Time budget: 3 hours in total.

## Stack
- Python 3.14, virtual environment in `.venv`
- pytest, requests, python-dotenv, pytest-playwright (Chromium)
- All tests must run with one command, documented in README.md
- Secrets live only in `.env` (WIX_API_KEY, WIX_ACCOUNT_ID). `.env` is in `.gitignore`.

## Verified API facts
- Base URL: https://www.wixapis.com/domain-search/v2/
- Headers: `Authorization: <WIX_API_KEY>` and `wix-account-id: <WIX_ACCOUNT_ID>`
- Check availability: GET `check-domain-availability?domain=<name.tld>`
- A domain must include its TLD (`mybakery.com`). The TLD filter is passed without the dot (`com`).

## Hard rules
1. No assumptions. If anything is unclear, stop and ask me. Check the real source (live page, network calls, API docs, actual response) before stating anything as fact.
2. Never print, log or commit the API key or account ID. They exist only in `.env`.
3. Never complete a purchase. Browsing and searching are fine. Never go to checkout or submit any payment.
4. Keep API calls low: a few hundred in total for the whole assignment. No load tests, brute force, scraping or loops over many domains.
5. Test only public pages and my own account.
6. Run no git command that changes history (commit, push, merge, rebase, reset, squash) unless I explicitly ask for it.
7. Do only what I asked. Add no extra steps, files or actions I didn't request. If you think something else is needed, suggest it and wait for my answer.
8. Expected domain behavior is not a bug. See "Domain basics" below.

## Domain basics (from the brief)
This is context, not a list of test cases. Do not report this behavior as bugs.
- Wix doesn't sell every TLD. A TLD is the ending, like `.com` or `.co.il`. A name can be free at the registry and still not be for sale on Wix.
- API input formats differ. In the API, a domain must include its TLD (`mybakery.com`), but the TLD filter is passed without the dot (`com`, not `.com`).
- Premium domains cost more than the standard price for their TLD. Sometimes the higher price applies only in the first year, sometimes on renewal too.
- Prices, currency and some suggestions depend on where you are. For example, a visitor in Israel may be offered `.co.il` names that a visitor elsewhere won't see.
- Suggestions are generated, so they can differ between calls and between doors.
- WHOIS data for most registered domains is redacted for privacy. That's normal.
- Availability is a point-in-time answer. A name that's free now can be taken a minute later.
- To call the public API you need an account-level API key. The key is a secret.

## Code style
- Simple, readable code with no unneeded abstractions. I must be able to explain every line.
- Assertions must not depend on values that change (prices, suggestion lists) unless that is what the test checks.
- After each change, explain in a few simple sentences what you changed and why.
