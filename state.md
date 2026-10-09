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

## 2026-10-09
**what:**     insights stage before persona copy (insights.md brief: 3 company + 3 person insights, confidence, relevance, tier); persona_copy.md now writes from one chosen insight
**why:**      one writer doing research and writing at once fell back on stock lines (blind score stalled at 6.3)
**broke:**    copy_check failed proof_id null although the brief allows it; fixed in the private copy (the kit version already allowed it)
**outcome:**  shuffled blind test, same 29 people: researched 7.07 vs 6.62, human 5.48 vs 5.45, "no reply" 7 vs 12, v4 won 15 / lost 9 / tied 5
**status:**   shipped
**postable:** yes, "splitting thinking from writing: why the AI's cold email got more specific when we stopped letting it read the research"

## 2026-10-09
**what:**     clean_people.py (names: company/person/title cleaning; verify: each contact against their own LinkedIn) + proof matched by the problem it solved (config proof gets solves + facts; copy_check checks facts, wording free)
**why:**      vendor titles and employers were trusted unchecked; one fixed proof sentence on every email was the top blind-review tell
**broke:**    Apify free plan caps runs at 10 items (first run returned only an error row); internal ACoAA... LinkedIn ids come back under vanity slugs, so lookup now uses every handle plus a name fallback; "SVP" vs "Senior vice president" false CHECK fixed with title abbreviation expansion
**outcome:**  29 pilot contacts: 27 OK, 1 LEFT (CPO had moved to another company; his email had scored 8/10), 1 NO_PROFILE. Blind v4 vs v4.1 on 27: human 5.07 -> 6.19, no-reply 11 -> 4, won 16/lost 5/tied 6
**status:**   shipped
**postable:** yes, "our best-scoring cold email was going to a man who had left the company"
