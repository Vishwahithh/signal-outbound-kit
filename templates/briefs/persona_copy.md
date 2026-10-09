# Persona copy: one email, one LinkedIn note, one call opener per person, written from a dossier

Sender: {{SENDER}}. Offer: {{OFFER}}. Tone: a peer who has done this work many times. Confident, plain, short.
Never grateful, never salesy, never clever. Today is {{TODAY}}.

## Three inputs, each with one job
1. The dossier ({{RUN_DIR}}/dossiers/dossier_<domain>.json) = WHAT is true about this company and person: the
   reviewed signal, dated events, their own posts, their site. Facts come only from here.
2. The phrase bank ({{VOC_BANK}}) = HOW people in this persona actually talk and worry about the problem the offer
   solves, verbatim from public podcasts, interviews and posts. Use it to choose the worry your question touches and
   to pick words a peer would use. Never quote it, never attribute it, never write "other CFOs tell us" or "companies
   like yours often". It shapes your thinking; it never appears in the email. If the file does not exist, skip it.
3. Replies the client has had before (in the phrase bank, if any) = what a real yes looked like. Yeses come from
   short, plain, specific emails with a small ask; write so a busy executive can answer in one line.

## Who to write for
The primary contact plus up to 3 buying_group people who are c-suite or VP in sales/revenue, finance, product or
operations. Skip engineering, HR, legal, marketing-only, regional sales VPs when a CRO or SVP Sales exists, anyone
whose company line is clearly a different company, and duplicates. Max 4 per company.

## Per person, think in this order (record briefly in the JSON)
1. persona: founder_ceo | commercial | finance | product.
2. read_first: read the site text (especially /pricing) before choosing a question. If the answer to a mechanics
   question is public there, you may not ask it. Note in one line what the page shows (or "no pricing page").
3. the_decision: the one decision this person now owns because of the signal, in their language. Founder: does the
   new thing change what the company is really selling. Commercial: how reps take it to existing accounts. Finance:
   whether it grows revenue per customer or just cost. Product: what goes in the base product versus what is extra.
4. why_now: 1-3 dated facts from the dossier with date and source, newest first. Undated or unsourced facts are not
   allowed.
5. own_words: if this person has posts in the dossier, 1-2 exact phrases (max 12 words) that show what they care
   about. Never quote politics, family, health or anyone else's words.
6. proof_id: by sector of THEIR business, then persona, from the list below.

## The email (email_1): 55-85 words, 4 short paragraphs max, "Hi <first>," and signed with the sender's first name
- Opening sentence: the implication or the decision, not the announcement. The fact sits inside the sentence as a
  clause with its month. Good: "With the CLI now in general release, the part customers pay for seems to be moving
  from the builder to the runtime." Good, using own words: "You wrote in September that finance teams need to see
  where the money actually moves; that is also where this question sits." Bad: "<Company> announced <product> in
  September." That proves a news feed, not understanding.
- Non-CEO emails must not open on "<Company> launched <product> in <month>". Open with the person's own words if they
  have posts, or one concrete detail of how this company makes money (per seat, per device, per transaction, platform
  fee, partner channel), with the dated event as a clause.
- One short clause says who the sender is and names THEIR sector ("I work with payments companies on ..."). Never a
  generic sector label that does not fit them.
- The question: about the decision or its consequence, one sentence, something only they can answer and would find
  interesting to answer. Derive it from THIS company's model and THIS persona's worry, not a stock question. Never a
  mechanics question whose answer is public or confidential. Never guess or describe their prices or business
  numbers, never say they are doing something wrong. At most half the emails at one company may be "A or B?"
  questions.
- Why us: one sentence with the proof line copied exactly after a short lead-in ("Recent work, <descriptor>:").
  Do not reword the line. If no proof fits their sector, keep the who-we-are clause and drop the metric.
- Close: one line, rotated so no two people at one company share it: "Worth 20 minutes?", "If useful, I can share
  how others handled it.", "Happy to compare notes.", "Open to a short call next week?"
- Siblings at one company must differ in opening move, question, proof (where a second one fits) and closer. One
  forwarded email must not expose the rest as a template.
- Hyper-personal test before each line: could this sentence go to anyone at another company? If yes, rewrite it
  until it could only go to this person.
- Accuracy: every fact matches the specific launch, post or event it is credited to; "so", "which means", "now that"
  only for a real cause; a quote only if the dossier shows it is that person's own post; no assumptions about roadmap.

## Hard rules
{{COPY_RULES}}
- no links or domain-shaped text, no em dashes, no exclamation marks, no praise words ("impressive", "great",
  "exciting"), no "congrats", no "I noticed", no "I hope", no "quick question", no "I imagine/suspect/my guess", no
  adjectives about their product, no numbers about them that the dossier does not state. Company names as people
  say them.

## LinkedIn note (li_note): under 200 characters, no pitch, no mention of the email or event. Name their sector.
## Call opener (call_opener): reason (the decision), one question, ask for 20 minutes. Under 70 words.

## Proof lines (client-approved; copy the text exactly)
{{PROOF}}

## Output: append ONE JSON line per person to {{RUN_DIR}}/copy/<your batch>.jsonl, as you go
{"domain": "...", "name": "...", "title": "...", "persona": "...", "read_first": "...", "the_decision": "...",
 "why_now": [{"fact": "...", "date": "YYYY-MM-DD", "source": "url or 'verified_signal' or 'post'"}],
 "own_words": ["..."], "proof_id": 0, "voc_used": ["topic: first words"], "personal_test": "...",
 "subject": "...", "email_1": "...", "li_note": "...", "call_opener": "...", "skipped": null}
Subject: 2-4 words, lower case except names, about the decision. Skipped people: the line with
"skipped": "<reason>" only. Read each dossier yourself; no scripts, no blank templates.
Then run `python scripts/copy_check.py` and fix every FAIL before a reviewer reads anything.
