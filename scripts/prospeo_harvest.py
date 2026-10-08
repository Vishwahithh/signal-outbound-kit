"""prospeo_harvest.py - source decision-makers at target companies with Prospeo's native filters, in signal-tier order.

Stages run separately so grading can sit between search and reveal (grade before you pay for emails):

  search   For each tier x geography in the config (strongest signal first), /search-person with the company, signal
           and title filters applied by Prospeo itself. Costs 1 credit per page of 25 people; no emails revealed. Rows
           are deduped by domain (first, strongest tier wins), checked against suppression, and appended to
           runs/<run>/prospeo/people_raw.jsonl as they arrive. Progress is kept in state.json, so it resumes.
  select   One decision-maker per unsuppressed company -> companies.csv (input to site fetch + grading).
  reveal   For rows in an approved CSV (column person_id: your A/B companies only), /enrich-person with
           only_verified_email, so a credit is spent only when a verified email comes back. Stops at --min-balance.
  status   Counts and balance.

    python scripts/prospeo_harvest.py search [--tiers hiring,funding] [--max-pages 40] [--max-credits 150]
    python scripts/prospeo_harvest.py select
    python scripts/prospeo_harvest.py reveal --approved runs/<run>/approved.csv [--min-balance 20]
    python scripts/prospeo_harvest.py status

Read Prospeo's full filter reference before editing tiers. Its funding/news data can lag by months, so signal tiers are
a starting point only: every signal is re-verified on the source page in signal research.
"""
import csv, json, sys, time, urllib.error, urllib.request
from collections import Counter

from common import config, env, norm, run_dir
from suppress import load as load_suppression

CFG = config()
OUT = run_dir(CFG, "prospeo")
RAW, REV, STATE = OUT / "people_raw.jsonl", OUT / "reveals.jsonl", OUT / "state.json"
H = {"X-KEY": env("PROSPEO_API_KEY"), "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def post(path, body):
    for attempt in range(6):
        try:
            req = urllib.request.Request("https://api.prospeo.io" + path, data=json.dumps(body).encode(), headers=H, method="POST")
            return json.loads(urllib.request.urlopen(req, timeout=60).read())
        except urllib.error.HTTPError as e:
            b = e.read().decode("utf-8", "replace")[:400]
            if e.code == 429:
                time.sleep(20 + attempt * 10)
                continue
            try:
                return json.loads(b)
            except Exception:
                return {"error": True, "error_code": f"HTTP{e.code}", "body": b}
        except Exception:
            time.sleep(5 + attempt * 5)
    return {"error": True, "error_code": "RETRIES_EXHAUSTED"}


def balance():
    # account-information must be a POST; a GET returns 403
    return post("/account-information", {}).get("response", {}).get("remaining_credits")


def title_filter():
    c = CFG["contacts"]
    return {"person_job_title": {"include": c["title_include"], "exclude": c.get("title_exclude", []), "match_mode": "CONTAINS"},
            "max_person_per_company": c.get("per_company", 3)}  # pick the real CEO in select(); "Founder" also matches co-founder CTOs


def tiers():
    a = CFG["archetype"]
    seg = {"company_industry": {"include": a["industries"]}, "company_headcount_range": a["headcount_ranges"]}
    seg.update(a.get("extra_prospeo_filters", {}))
    out = []
    for t in CFG["tiers"]:
        if t.get("filters", {}).get("company"):  # a fixed domain list: no geography split
            out.append((t["name"], t["filters"], t.get("signal_hint")))
            continue
        for geo in a["geo"]:
            out.append((f"{t['name']}_{geo}", {"company_location_search": {"include": [geo]}, **seg, **t.get("filters", {})}, t.get("signal_hint")))
    return out


def search():
    want = set(arg("--tiers", "").split(",")) - {""}
    max_pages, max_credits = int(arg("--max-pages", 40)), int(arg("--max-credits", 150))
    supp = load_suppression(CFG)
    seen, dom_tier = set(), {}
    if RAW.exists():
        for line in open(RAW, encoding="utf-8"):
            x = json.loads(line); seen.add(x.get("person_id")); dom_tier.setdefault(x["domain"], x["tier"])
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    start = balance()
    print("balance", start, "| suppressed domains", len(supp), "| already banked", len(seen))
    with open(RAW, "a", encoding="utf-8") as f:
        for name, filt, sig in tiers():
            if want and not any(name.startswith(w) for w in want):
                continue
            page = state.get(name, 0) + 1
            if page == 0:
                continue  # tier finished (stored as -1)
            new = 0
            while page <= max_pages:
                if start - (balance() or 0) >= max_credits:
                    print("  credit cap reached"); STATE.write_text(json.dumps(state)); return
                r = post("/search-person", {"page": page, "filters": {**filt, **title_filter()}})
                if r.get("error"):
                    code = r.get("error_code")
                    print(f"  {name} p{page}: {code} {r.get('filter_error') or ''}")
                    if code in ("NO_RESULTS", "PLAN_REQUIRED") or "not supported" in str(r):
                        state[name] = -1
                    break
                for p in r.get("results", []):
                    c, per = p.get("company") or {}, p.get("person") or {}
                    dom = norm(c.get("website") or c.get("domain"))
                    pid = per.get("person_id")
                    if not dom or pid in seen or dom_tier.get(dom, name) != name:
                        continue  # one tier per company; up to per_company people per company
                    seen.add(pid); dom_tier[dom] = name
                    row = {"tier": name, "signal_hint": sig, "domain": dom, "suppressed": dom in supp,
                           "company": c.get("name"), "country": (c.get("location") or {}).get("country"),
                           "headcount": c.get("employee_count"), "headcount_range": c.get("employee_range"),
                           "industry": c.get("industry"), "description": (c.get("description") or "")[:1200],
                           "person_id": pid, "first_name": per.get("first_name"), "last_name": per.get("last_name"),
                           "title": per.get("current_job_title") or per.get("job_title"),
                           "linkedin": per.get("linkedin_url"), "company_json": c}
                    f.write(json.dumps(row, ensure_ascii=False) + "\n"); f.flush()
                    new += 0 if row["suppressed"] else 1
                tp = (r.get("pagination") or {}).get("total_page", 1)
                state[name] = page
                STATE.write_text(json.dumps(state))
                print(f"  {name} page {page}/{tp} | new unsuppressed so far {new}")
                if page >= tp:
                    state[name] = -1; break
                page += 1
                time.sleep(2.5)
            STATE.write_text(json.dumps(state))
    print("balance", balance(), "| spent", start - (balance() or 0))


def title_rank(t):
    """Lower is better. CEO first, then MD/President, then a founder not in a technical or operations seat.
    Co-founder CTO/COO/CPO only as a last resort. Edit to suit the buyer of your client's offer."""
    t = (t or "").lower()
    if any(k in t for k in ("ceo", "chief executive")):
        return 0
    if "managing director" in t or t.strip() in ("president", "president & founder", "founder & president"):
        return 1
    if "founder" in t and not any(k in t for k in ("cto", "technology", "technical", "coo", "operat", "cpo", "product", "engineer", "design")):
        return 2
    if "president" in t:
        return 3
    return 9


def select():
    rows = [json.loads(line) for line in open(RAW, encoding="utf-8")]
    best = {}
    for r in rows:
        if r["suppressed"]:
            continue
        k = (title_rank(r["title"]), r["tier"])
        if r["domain"] not in best or k < best[r["domain"]][0]:
            best[r["domain"]] = (k, r)
    cols = ["domain", "company", "country", "headcount", "headcount_range", "industry", "tier", "signal_hint",
            "person_id", "first_name", "last_name", "title", "title_rank", "linkedin", "description"]
    out = OUT / "companies.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader()
        for (rk, _), r in sorted(best.values(), key=lambda x: (x[1]["tier"], x[0][0])):
            w.writerow({**r, "title_rank": rk, "description": (r.get("description") or "").replace("\n", " ")})
    print(out, len(best), "companies | title ranks", dict(Counter(v[0][0] for v in best.values())))


def reveal():
    approved = [r["person_id"] for r in csv.DictReader(open(arg("--approved"), encoding="utf-8-sig")) if r.get("person_id")]
    done = {json.loads(line)["person_id"] for line in open(REV, encoding="utf-8")} if REV.exists() else set()
    floor = int(arg("--min-balance", 20))
    start = balance()
    print("balance", start, "| to reveal", len([a for a in approved if a not in done]))
    with open(REV, "a", encoding="utf-8") as f:
        for i, pid in enumerate(approved):
            if pid in done:
                continue
            if i % 25 == 0:
                b = balance()
                print(f"  {i}/{len(approved)} balance {b}")
                if b is not None and b <= floor:
                    print("  balance floor reached"); break
            r = post("/enrich-person", {"only_verified_email": True, "data": {"person_id": pid}})
            em = (r.get("person") or {}).get("email") or {}
            f.write(json.dumps({"person_id": pid, "email": em.get("email"), "status": em.get("status"),
                                "error_code": r.get("error_code"), "free": r.get("free_enrichment")}) + "\n"); f.flush()
            time.sleep(1.2)
    print("balance", balance(), "| spent", start - (balance() or 0))


def status():
    rows = [json.loads(line) for line in open(RAW, encoding="utf-8")] if RAW.exists() else []
    print("banked people", len(rows), "companies", len({r["domain"] for r in rows}),
          "unsuppressed companies", len({r["domain"] for r in rows if not r["suppressed"]}))
    for k, v in sorted(Counter(t for d, t in {(r["domain"], r["tier"]) for r in rows if not r["suppressed"]}).items()):
        print(" ", k, v)
    if REV.exists():
        rv = [json.loads(line) for line in open(REV, encoding="utf-8")]
        print("reveals", len(rv), "emails", sum(1 for r in rv if r.get("email")))
    print("balance", balance())


if __name__ == "__main__":
    {"search": search, "select": select, "reveal": reveal, "status": status}[sys.argv[1]]()
