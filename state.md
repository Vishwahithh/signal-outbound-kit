# signal-outbound-kit - state log

## 2026-10-08
**what:**     Created the kit: client-agnostic version of the snippet signal pipeline (scripts, briefs, 2 skills, runbook, Attio CRM)
**why:**      the system only worked for one client and lived in a repo full of client data; needed a clean, reusable, shareable package
**broke:**    nothing; scripts compiled, render_briefs + suppress smoke-tested on the example config; paid-API scripts not run end to end
**outcome:**  15 scripts/templates; no client names, people or keys (grep-checked); proof lines are REPLACE placeholders
**status:**   shipped: public at github.com/Vishwahithh/signal-outbound-kit
**postable:** yes: open-sourcing the grade-before-you-pay outbound pipeline

## 2026-10-09
**what:**     added person research -> persona copy stage: person_research.py, copy_check.py, persona_copy brief, voc bank format, person-copy skill
**why:**      the Twain-style research-to-copy work only lived in the private snippet folder
**broke:**    nothing; scripts made client-agnostic (proof from config, Apify tokens from APIFY_TOKENS, output under runs/<run>/)
**outcome:**  copy_check and render_briefs tested on dummy data; secret scan of files and history clean
**status:**   shipped
**postable:** yes, "the research-to-copy loop that took cold email from 4.6 to 6.3/10 on a blind prospect read, open-sourced"
