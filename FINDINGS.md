# Findings

Summary:

| ID | Title | Type | Severity | Priority |
|----|-------|------|----------|----------|
| F1 | Storefront: "is already registered" message is missing the domain name | Bug | Medium | High |
| F2 | WHOIS: raw registrar data shows "error: __raw: undefined" for some registrars | Bug | Low | Medium |
| F3 | Suggestions include famous brand names | Risk | Medium | Medium |
| F4 | A 403 error is used as a normal answer | Observation | Low | Low |
| F5 | The suggest-domains paging cursor is readable | Observation | Low | Low |

---

## F1 - Storefront: the "is already registered" message is missing the domain name

**Type:** Bug

**What happens:**
When I search for a taken name, the message shows no domain name. It shows:
" is already registered. Explore some great alternatives below."
The user typed no TLD, so the page checked `.com`. But the message does not say which domain is taken.
The WHOIS page shows the name correctly ("google.com is registered.").

**Steps to reproduce:**
1. Open https://www.wix.com/domains
2. Search for `mybakery` (no TLD).
3. Read the message above the results.
4. Repeat with `google`.

**Expected:** The message names the domain, for example "mybakery.com is already registered."
**Actual:** The message starts with a space and has no domain name.

**Evidence:**
- `evidence/storefront-missing-name-mybakery.png`
- `evidence/storefront-missing-name-google.png`

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
- `evidence/whois-raw-error-google.png`
- `evidence/whois-raw-error-youtube.png`

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
- `evidence/storefront-missing-name-google.png`

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

## F5 - The suggest-domains paging cursor is readable

**Type:** Observation

**What happens:**
The "next" paging cursor in the suggest-domains response is base64 text. Decoded, it shows:
- the suggestions already shown,
- the next suggestions waiting,
- `"engine": "Llm"`.

The Business Name Generator response also had the same kind of cursor.

Editing the cursor and sending it back was not tested.

**Steps to reproduce:**
1. Open the browser DevTools, Network tab.
2. Open https://www.wix.com/domains and search for `mybakery`.
3. Find the suggest-domains response and copy the "next" cursor.
4. Decode it from base64.

**Evidence:** The decoded cursor content, as described above.

**Severity:** Low
**Priority:** Low

**Why:** It shows internal details to anyone.

---

## Checked, no issue found

- **Business names with "&" and "'"** ("Whisk & Whimsy", "Baker's Boutique"): the query is encoded correctly and the domains are valid ("&" becomes "and", "'" is removed).
- **WHOIS on wix.com (GoDaddy):** raw registrar data shows correctly.
