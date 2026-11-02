# Findings

Summary:

| ID | Title | Type | Severity | Priority |
|----|-------|------|----------|----------|
| F1 | Storefront: "is already registered" message is missing the domain name | Bug | Medium | High |
| F2 | WHOIS: raw registrar data shows "error: __raw: undefined" for some registrars | Bug | Low | Medium |
| F3 | Suggestions include famous brand names | Risk | Medium | Medium |
| F4 | A 403 error is used as a normal answer | Observation | Low | Low |
| F5 | The public API doesn't match its docs | Bug or doc gap | Medium | High |

---

## F1 - Storefront: the "is already registered" message is missing the domain name

**Type:** Bug

**What happens:**
When I search for a taken name, the message shows no domain name. It shows:
" is already registered. Explore some great alternatives below."
The user typed no TLD, so the page checked `.com`. But the message does not say which domain is taken.
The WHOIS page shows the name correctly ("google.com is registered.").

Seen 3 times between 11:48 and 12:43 (screenshots in evidence/). After about 13:00 I could not reproduce it, logged in or in incognito: searching without a TLD now shows no message at all. Maybe an A/B test or a fix. I don't know which. Test SF-03 now guards the version with a TLD.

**Steps to reproduce:**
1. Open https://www.wix.com/domains
2. Search for `mybakery` (no TLD).
3. Read the message above the results.
4. Repeat with `google`.

**Expected:** The message names the domain, for example "mybakery.com is already registered."
**Actual:** The message starts with a space and has no domain name.

**Evidence:**
- [storefront-missing-name-mybakery.png](evidence/storefront-missing-name-mybakery.png)
- [storefront-missing-name-google.png](evidence/storefront-missing-name-google.png)

**Severity:** Medium
**Priority:** High

**Why:** This is the main flow of the main door. It happened on every taken search I tried (2 of 2).

---

## F2 - WHOIS: "Raw Registrar WHOIS Data" shows "error: __raw: undefined" for some registrars

**Type:** Bug

**What happens:**
For some domains, the "Raw Registrar WHOIS Data" section shows `error: __raw: undefined` instead of the data.
- google.com and youtube.com (registrar MarkMonitor): error.
- wix.com (registrar GoDaddy): raw data shows fine.

The rest of the page (Domain Information, Registrar) shows correctly.

**Steps to reproduce:**
1. Open https://www.wix.com/domains/whois
2. Look up `google.com`.
3. Scroll to "Raw Registrar WHOIS Data".
4. Repeat with `youtube.com`.
5. Compare with `wix.com`.

**Expected:** Raw registrar data, or a clear message for the user.
**Actual:** `error: __raw: undefined`

**Evidence:**
- [whois-raw-error-google.png](evidence/whois-raw-error-google.png)
- [whois-raw-error-youtube.png](evidence/whois-raw-error-youtube.png)

**Severity:** Low
**Priority:** Medium

**Why:** Raw code error text is shown to users, and it happens on popular domains.

---

## F3 - Suggestions include famous brand names

**Type:** Risk

**What happens:**
Searching for a famous brand gives suggestions that contain the brand name.
- Storefront search `google`: globalgoogle.org, getgoogle.biz, googlecompany.net, visitgoogle.ai and more.
- WHOIS for google.com also suggested globalgoogle.org and googleclub.org.

This is not a bug by itself. It needs a product/legal decision.

**Steps to reproduce:**
1. Open https://www.wix.com/domains and search for `google`.
2. Look at the suggested alternatives.
3. Open https://www.wix.com/domains/whois and look up `google.com`.
4. Look at the suggested domains.

**Evidence:**
- [storefront-missing-name-google.png](evidence/storefront-missing-name-google.png)

**Severity:** Medium
**Priority:** Medium

**Why:** Trademark risk for Wix and for the user who buys the domain.

---

## F4 - A 403 error is used as a normal answer

**Type:** Observation

**What happens:**
On every search of a taken domain (storefront and WHOIS), the page calls:

```
https://www.wix.com/_api/user-domains/v1/user_domains/google.com?domainName=google.com
```

and gets a 403:

```json
{"code": "DOMAINS_PERMISSION_DENIED", "description": "PERMISSION_DENIED: domainBelongsToDifferentUser"}
```

It looks like the page asks "does this domain belong to the logged-in user?". Nothing breaks on screen.

**Steps to reproduce:**
1. Open the browser DevTools, Network tab.
2. Search for a taken domain (for example `google`) on https://www.wix.com/domains or https://www.wix.com/domains/whois.
3. Find the `user_domains` request and look at the status and response.

**Evidence:**

```
Request:
GET https://www.wix.com/_api/user-domains/v1/user_domains/google.com?domainName=google.com

Response: 403
{"code": "DOMAINS_PERMISSION_DENIED", "description": "PERMISSION_DENIED: domainBelongsToDifferentUser"}
```

**Severity:** Low
**Priority:** Low

**Why:**
- Real errors are harder to see in monitoring when 403 is a normal answer.
- The text "domainBelongsToDifferentUser" may tell people that a domain is at Wix (not verified).

---

## F5 - The public API doesn't match its docs

**Type:** Bug or doc gap

**What happens:**
- `check-domain-availability` returns 200 with the full answer with no Authorization header, with a wrong key, and with no `wix-account-id`. The docs say this call requires an account-level API key.
- The docs say a domain can be 3-63 characters. A 64-character domain gets 200 with a normal answer.

**Steps to reproduce:**
1. Open PowerShell.
2. Call `check-domain-availability` with no headers at all (command in Evidence below).
3. Look at the status and the response.

**Expected:** An auth error without a key (per the docs).
**Actual:** 200 with the full answer.

**Evidence:**

I checked the no-key case myself in PowerShell, with no headers at all:

```
Invoke-RestMethod -Uri "https://www.wixapis.com/domain-search/v2/check-domain-availability?domain=google.com"
-> {"availability":{"domain":"google.com","available":false,"premium":false,"premiumType":"UNKNOWN_PREMIUM_TYPE"}}
```

Tests API-05, API-06, API-07 and the 64-character E-02 case are marked xfail with these reasons.

**Severity:** Medium
**Priority:** High

**Why:** Maybe the API is public on purpose (the storefront calls the same path without a key). Then the docs are wrong. Either way, the API and the docs don't agree. Priority is High because someone at Wix must decide quickly: fix the API or fix the docs.

---

## Checked, no issue found

- **Business names with "&" and "'"** ("Whisk & Whimsy", "Baker's Boutique"): the query is encoded correctly and the domains are valid ("&" becomes "and", "'" is removed).
- **WHOIS on wix.com (GoDaddy):** raw registrar data shows correctly.
