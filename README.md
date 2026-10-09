# signal-outbound-kit

A Claude Code kit for signal-based B2B outbound: find the companies that fit, check them on their own websites, find
a dated reason to reach out right now, and only then pay for contact data.

It is the operating system behind a real outbound engagement, made client-agnostic: one JSON config per client
describes the target, the signals and the proof, and everything else (scripts, agent briefs, skills, CRM) reads from it.

## Why this order
Most outbound burns money in the wrong place: it buys emails for a big list and then discovers most of it was never a
fit. This kit grades first and pays later:

```
spec -> source (native filters) -> suppress -> grade on own website -> signal research + human review
     -> reveal verified emails for A/B only -> verify -> person research -> copy per person -> gate + blind score
     -> launch -> CRM cool-down and routing
```

See [PIPELINE.md](PIPELINE.md) for the gates and the lessons behind each one.

## What's inside

| Path | What it is |
|---|---|
| `config/client.example.json` | Everything client-specific: offer, archetype, filters, grades, signals and windows, proof, suppression, CRM |
| `scripts/prospeo_harvest.py` | Search by tiers with Prospeo's native filters, pick one decision-maker per company, reveal verified emails for approved rows only |
| `scripts/site_fetch.py`, `fetch_pages.py` | Free website crawl (crawl4ai), paid ladder (Tavily -> Firecrawl -> Exa) only on failure, dead-domain check before any paid call |
| `scripts/qualify_batches.py` | Pack site text into compact batches for grading agents |
| `scripts/firecrawl_refetch.py` | Re-read sites that blocked the free crawler |
| `scripts/merge.py` | One lead master per run, with email-domain mismatch flags |
| `scripts/mv_verify.py` | MillionVerifier bulk verification with resume (never re-upload) |
| `scripts/person_research.py` | One dossier per company: buying group, each exec's own recent LinkedIn posts, the company's site, the reviewed signal (Apify, cents per company; optional Explorium events) |
| `scripts/copy_check.py` | Deterministic gate on persona copy: length, banned phrases, proof verbatim, dated and sourced facts, subject, LinkedIn note |
| `scripts/render_briefs.py` | Fill the agent briefs from the config, with signal windows as real dates |
| `scripts/attio_*.py` | Attio as the CRM: fields, import, cool-down, nightly score and route, deals |
| `templates/briefs/` | Agent briefs: grading, signal research, email one on the signal, persona copy from a dossier |
| `config/voc_bank.example.md` | Format for a voice-of-customer phrase bank: how the buyers really talk, used to shape questions, never quoted |
| `.claude/skills/` | `market-map`, `signal-research` and `person-copy` skills for Claude Code |

## Setup

```bash
git clone <this repo> && cd signal-outbound-kit
python -m pip install -r requirements.txt && python -m crawl4ai.install  # or: crawl4ai-setup
cp .env.example .env                                  # add your own keys
cp config/client.example.json config/client.json      # describe your client
python scripts/render_briefs.py
```

Open the folder in Claude Code and ask for what you want ("build a list for the new client", "find signals for these
companies"). The skills load on their own and run the scripts in order.

## A run, by hand

```bash
python scripts/prospeo_harvest.py search --max-credits 150
python scripts/prospeo_harvest.py select
python scripts/site_fetch.py --workers 5
python scripts/qualify_batches.py --all          # then grading agents on runs/<run>/briefs/qualify.md
python scripts/merge.py
python scripts/prospeo_harvest.py reveal --approved runs/<run>/approved.csv
python scripts/merge.py && python scripts/mv_verify.py --input runs/<run>/leads_master.csv --label primary
# research agents on runs/<run>/briefs/research.md, human review, then copy
python scripts/person_research.py            # dossiers for reviewed companies (runs/<run>/research/people_companies.json)
# copy agents on runs/<run>/briefs/persona_copy.md, then:
python scripts/copy_check.py
python scripts/attio_leads.py setup && python scripts/attio_leads.py import-run && python scripts/attio_score.py
```

All output for a run goes to `runs/<run>/`, which is git-ignored, as are `.env` and your client configs.

## Rules the kit enforces or assumes
- Grade before you reveal. No email credits on a company nobody has looked at.
- Only verifier "ok" emails are sent. No catch-alls. Never guess an address from a name pattern.
- A signal is real only if someone opened the page and saw the date. A person reviews every signal before copy.
- Could-not-read is its own verdict, never counted as "no".
- Copy states facts and asks one question. It never judges the prospect's business.
- Every paid call is capped and goes free tool first.

## Requirements
Python 3.10+, crawl4ai (free crawling). Optional paid keys: Prospeo, MillionVerifier, Tavily, Firecrawl, Exa, Attio.

## License
MIT
