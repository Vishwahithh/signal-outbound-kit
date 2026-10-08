"""merge.py - join every table of a run into one lead master, keyed by company domain.

Inputs (runs/<run>/): prospeo/companies.csv (company + chosen person), prospeo/people_raw.jsonl (full company record:
revenue, funding), prospeo/reveals.jsonl (emails), prospeo/second_contacts.jsonl (optional), qualify/out_*.jsonl
(website grade; qualify/rc_out_*.jsonl re-grades override), research/out_*.jsonl and mv_results*.csv when they exist.
Missing values stay blank. Nothing is guessed.

Domain check: databases sometimes hold the wrong website for a company. If the revealed email's domain differs from the
company domain, the row is flagged domain_mismatch and its grade is not trusted until the domain is re-resolved.

    python scripts/merge.py   -> runs/<run>/leads_master.csv (+ prints counts)
"""
import csv, json
from collections import Counter

from common import config, jl, run_dir


def root(d):
    parts = (d or "").lower().split(".")
    return ".".join(parts[-3:]) if len(parts) > 2 and parts[-2] in ("co", "com", "org", "ac") else ".".join(parts[-2:])


def main():
    cfg = config()
    run = run_dir(cfg)
    base = {r["domain"]: r for r in csv.DictReader(open(run / "prospeo" / "companies.csv", encoding="utf-8"))}
    comp = {}
    for r in jl(run / "prospeo" / "people_raw.jsonl"):
        comp.setdefault(r["domain"], r["company_json"])
    rev = {r["person_id"]: r for r in jl(run / "prospeo" / "reveals.jsonl")}
    second = {r["domain"]: r for r in jl(run / "prospeo" / "second_contacts.jsonl") if r.get("email")}
    qual = {r["domain"]: r for r in jl(run / "qualify" / "out_*.jsonl")}
    qual.update({r["domain"]: r for r in jl(run / "qualify" / "rc_out_*.jsonl")})
    research = {r["domain"]: r for r in jl(run / "research" / "out_*.jsonl")}
    mv = {}
    for f in run.glob("mv_results*.csv"):
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            mv[(r.get("email") or "").lower()] = r.get("result")
    rows = []
    for d, b in base.items():
        c, q, rs, s2 = comp.get(d) or {}, qual.get(d) or {}, research.get(d) or {}, second.get(d) or {}
        email = (rev.get(b["person_id"]) or {}).get("email") or ""
        edom = email.split("@")[1].lower() if "@" in email else ""
        fund = c.get("funding") or {}
        rows.append({
            "domain": d, "company": b["company"], "country": b["country"], "headcount": b["headcount"],
            "revenue_band": c.get("revenue_range_printed") or "",
            "last_funding_date": (fund.get("latest_funding_date") or "")[:10], "last_funding_stage": fund.get("latest_funding_stage") or "",
            "tier": b["tier"], "signal_hint": b["signal_hint"], "person_id": b["person_id"],
            "first_name": b["first_name"], "last_name": b["last_name"], "title": b["title"], "linkedin": b["linkedin"],
            "email": email, "email_domain": edom, "domain_mismatch": bool(edom) and root(edom) != root(d),
            "mv": mv.get(email.lower(), "") if email else "",
            "second_name": f"{s2.get('first_name', '')} {s2.get('last_name', '')}".strip(), "second_title": s2.get("title", ""),
            "second_email": s2.get("email", ""), "second_mv": mv.get((s2.get("email") or "").lower(), ""),
            "grade": q.get("qualify", ""), "sells": q.get("sells", ""), "what_they_sell": q.get("what_they_sell", ""),
            "customers": q.get("customers", ""), "pricing_style": q.get("pricing_style", ""),
            "status": q.get("status", ""), "grade_reason": q.get("reason", ""),
            "best_signal": rs.get("best_signal", ""), "signals": json.dumps(rs.get("signals", []), ensure_ascii=False) if rs else "",
        })
    out = run / "leads_master.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(out, len(rows))
    print("grades", dict(Counter(r["grade"] or "ungraded" for r in rows)))
    print("with email", sum(1 for r in rows if r["email"]), "| domain_mismatch", sum(r["domain_mismatch"] for r in rows))
    print("A/B", sum(1 for r in rows if r["grade"] in ("A", "B")), "| A/B with email", sum(1 for r in rows if r["grade"] in ("A", "B") and r["email"]))


if __name__ == "__main__":
    main()
