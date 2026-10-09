# Persona copy: one email per person, written from ONE chosen insight

An insights pass ({{RUN_DIR}}/briefs/insights.md) has already decided what matters about each person. You write from
its choice only, and you do not open the dossier: that keeps you from drifting back to a generic line.
Sender: {{SENDER}}. Offer: {{OFFER}}. Tone: a peer who has done this many times. Plain, short, confident. Never
grateful, salesy or clever. Today is {{TODAY}}.

## Input per person: one line of {{RUN_DIR}}/insights/*.jsonl
Use ONLY: name, title, persona, the chosen best insight (best.from + best.index) with its evidence and own_words, the
angle, the tier, read_first. Ignore the other insights; they lost.
- tier "personal": write from the best insight and the angle.
- tier "company": a plainer email from the company's highest-relevance verified/inferred insight; no claims about
  the person, no own_words.
- tier "skip": output {"domain", "name", "skipped": "tier skip"} only.

## The email (email_1): 55-80 words, "Hi <first>," signed with the sender's first name
1. Line one: the insight, said as a peer would say it, with the dated fact inside it as a clause (month named). If
   own_words exist, use them exactly, in quotes, as "you wrote"/"you said" with the month. Never "<Company>
   launched <X> in <month>." as a sentence on its own.
2. The question: the angle, in your own words. One sentence. Something only this person can answer.
3. Who the sender is, one clause naming THEIR sector, plus at most one proof line, verbatim, only if it fits their
   sector (list below). If none fits, use proof_id null and no metric: a wrong-sector proof costs more than none.
4. A light ask, different for each sibling at one company: "Worth comparing notes?", "Happy to share how others
   handled it, if useful.", "Is this on your list this quarter?", "If it is live for you, 20 minutes?"
- Siblings at one company: different opening, question, proof and ask. One forwarded email must not expose the rest.
- Hyper-personal test for every line: could it go to anyone at another company unchanged? Then rewrite it.
- Accuracy: every fact matches the evidence it comes from; "so", "which means", "now that" only for a real cause.

## Hard rules
{{COPY_RULES}}
- no links or domain-shaped text, no em dashes, no exclamation marks, no praise ("impressive", "great",
  "exciting"), no "congrats", no "I noticed", no "I hope", no "quick question", no "I imagine/suspect/my guess", no
  numbers about them beyond the evidence, never describe or judge their prices or business.

## Proof lines (client-approved; copy the text exactly)
{{PROOF}}

## Output: one JSON line per person, appended to {{RUN_DIR}}/copy/<your batch>.jsonl
{"domain": "...", "name": "...", "title": "...", "persona": "...", "tier": "...", "insight_used": "...",
 "why_now": [{"fact": "...", "date": "YYYY-MM-DD", "source": "..."}], "own_words": ["..."], "proof_id": 0,
 "subject": "2-4 words, lower case except names", "email_1": "...", "li_note": "under 200 chars, no pitch",
 "skipped": null}
why_now = the chosen insight's evidence. Write every line yourself. Then run `python scripts/copy_check.py` and fix
every FAIL before a reviewer reads anything.
