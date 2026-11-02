# AI Log

How I used AI in this assignment.

## 1. AI tools I used

- **Claude (chat):** to plan the work and guide me step by step.
- **Claude Code:** to write the files and the tests in this repo.

## 2. Key prompts

Short versions of my main prompts, one per part.

| Part | Prompt (short version) |
|---|---|
| Setup and rules | CLAUDE.md was drafted with Claude (chat) and reviewed by me. To check that Claude Code reads it: "Read CLAUDE.md and list the hard rules, one short line each. Do not create, change or commit any files." It listed all 8 rules correctly. |
| ARCHITECTURE.md | "Create ARCHITECTURE.md using only my exploration notes. Mark guesses as not verified yet. Add a Mermaid diagram." Then: "Rewrite it in much simpler English, explain technical words in brackets." |
| TEST_PLAN.md | "Focus on edge cases first. Suggest the top 5, then stop and wait for my answer." Then: "Make it bigger: a table per door and cross-door, every test needs a reason, no filler." |
| FINDINGS.md | I gave the AI each finding with my evidence, severity and priority, and asked it to write them up without inventing anything. |
| Tests | "Plan the tests first, do not write code yet." Then: "Do the checks first (API error codes, one look at the storefront) and show me before writing code." |
| README.md | "Create README.md in simple English: total time at the top, the file list, how to set up and run on Windows, what the results mean (29 passed, 4 xfailed), why I automated what I did, and drafts for 'another week' and 'quality strategy', based only on TEST_PLAN.md and FINDINGS.md. Do not commit." |
| AI_LOG.md | "Create AI_LOG.md in simple English. Use only my side notes and what happened in this session. Do not invent anything. Do not commit." |

## 3. Where the AI was wrong and how I caught it

- **The edge case list had no Business Name Generator case.** I caught it by comparing the list with what I saw on the page myself. See section 4.
- **Claude Code linked the Business Name Generator and WHOIS to www.wix.com without proof.** I checked in DevTools. The host was right, and now it is verified.
- **Claude (chat) said `match-labels` was on the domain-search service.** I checked the request URL in DevTools: it is `domains-serverless-services/insights`.
- **Claude (chat) guessed F1 happens only for logged-in users.** I tested logged in and in incognito. The guess was wrong.
- **Claude Code listed the API fields as top-level.** The real path is `availability.available`. Fixed in ARCHITECTURE.md.
- **Claude Code first planned E-02 with a 63-character limit for the label.** The docs say 3-63 characters for the whole domain. I changed it to follow the docs.
- **Claude Code's storefront fix (wait for `networkidle`) passed when it ran it, but all 5 storefront tests failed when I ran the suite myself.** Fixed by waiting for the page load and the search box, and retrying Enter once. Then I got 3 green runs in a row.
- **Claude Code said the API works without a key.** I checked it myself in PowerShell with no headers. Confirmed.

## 4. What I changed or threw away

- **Added a Business Name Generator edge case.** I wrote it from what I saw on the page: the generator gave names with `&` and `'`, so I checked that these characters don't end up in a domain (TEST_PLAN.md, E-05).
- **README drafts:** Claude Code wrote drafts of "What I would do with another week" and "My quality strategy", and I will edit them myself.
- **Replaced finding F5.** The old F5 (a readable paging cursor) was replaced with a stronger one: the API doesn't match its docs.
- **SF-03 changed from xfail to a normal test.** It was planned as an xfail for F1. After I could not reproduce F1, I changed it to a normal test that guards against F1 coming back.
- **Kept 4 changes Claude Code made beyond my request in TEST_PLAN.md** (the Why column, merged sections, a removed row, new IDs). I reviewed each one before keeping it.
- **The 64-character case became an xfail** and part of finding F5.

## 5. What I chose not to give to the AI

- **Running the tests:** I ran them myself and read the results.
- **Git commits and pushes:** I did them myself. CLAUDE.md does not allow the AI to change git history.
- **Checking the API without a key:** I called the API myself in PowerShell with no headers to confirm F5 (see FINDINGS.md).
- **Severity and priority:** I chose them for each finding myself.
- **The final review:** I read every file myself before handing it in.

## 6. Agent config I wrote

I wrote `CLAUDE.md` for Claude Code. It has the context, the stack, the API facts I verified, the hard rules, the domain basics from the brief, and the code style.

The rules worked. Once, Claude Code stopped and asked me before it added a row that wasn't in my notes.

Why each hard rule is there:

1. **No assumptions, ask me:** every fact must come from a real source (live page, network call, docs, real response), not from a guess.
2. **Never print, log or commit the key or account ID:** they are secrets and must stay only in `.env`.
3. **Never complete a purchase:** searching is safe, but a purchase or payment is real and costs money.
4. **Keep API calls low:** a few hundred calls in total for the whole assignment, with no load tests and no loops over many domains.
5. **Test only public pages and my own account:** I'm not allowed to touch anything else.
6. **No git command that changes history unless I ask:** I control what is committed and when.
7. **Do only what I asked:** no extra steps or files, so I know and can explain everything in the repo.
8. **Expected domain behavior is not a bug:** the brief lists normal behavior (prices by location, generated suggestions, redacted WHOIS), and it must not be reported as findings.
