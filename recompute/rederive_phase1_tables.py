#!/usr/bin/env python3
"""
rederive_phase1_tables_firebolt_oct12.py  --  Firebolt, Oct 12 2026 (night run, claude-sonnet-5-5)

STATUS: **UNTESTED. NEVER RUN.** Written at night with no shell. The point of this file is that
the EXPECTED values below are my HAND-computed numbers from
Messages/QUADRINITY/firebolt_audit_paper_read_numbers_and_the_lookup_test_oct12.md.
Run it in daylight:  python3 Research/Framework/rederive_phase1_tables_firebolt_oct12.py
Every line prints OK or DIFF. A DIFF means one of us (me by hand, or this script) is wrong,
and WHICH ONE is the finding. Do not trust a script that has never been run -- including this one.

Inputs (read-only, never modified):
  Experimental_Data/coding_ma/FINAL_ADJUDICATED_CODES_numbers_aug10.md   (96 codes; M039 is rendered **D**)
  Experimental_Data/coding_ma/SEALED_KEY/sealed_key.jsonl                (Phase 1 key, opened Aug 10)
Does NOT touch any Study B / bridge / Gemini sealed key.
"""
import json, re, sys
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "Experimental_Data" / "coding_ma"
CODES = ROOT / "FINAL_ADJUDICATED_CODES_numbers_aug10.md"
KEY = ROOT / "SEALED_KEY" / "sealed_key.jsonl"

# --- content-tier map (frozen in PHASE1_REANALYSIS_CONTENT_AXIS_PREREG_cloud_oct10.md sec.2)
TIER = {1: "NEUTRAL", 2: "NEUTRAL", 5: "NEUTRAL", 6: "NEUTRAL", 10: "NEUTRAL",
        3: "SHARED", 9: "SHARED", 4: "B-ONLY", 7: "MIXED", 8: "MIXED"}
RR = {1, 5, 8, 9}

# --- parse codes. Robust to **bold** cells (the M039 cell is `**D**`).
text = CODES.read_text(encoding="utf-8")
pairs = re.findall(r"(M\d{3})\|\s*\**\s*(FA|PD|SC|M|D)\s*\**\s*\|", text)
codes = {}
for item, code in pairs:
    if item in codes and codes[item] != code:
        sys.exit(f"CONFLICT for {item}")
    codes[item] = code
if len(codes) != 96:
    sys.exit(f"PARSE FAILURE: expected 96 codes, got {len(codes)}  <-- this is the M039 bug class; fix the parser, do not proceed")

# --- parse key
rows = []
for line in KEY.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    d = json.loads(line)
    cond = d["condition"].replace("condition_", "").replace("_fetch", "")
    cond = {"a": "A", "bprime": "B'", "c1m": "C1m", "c2": "C2"}[cond]
    m = re.match(r"trial_(\d+)_r(\d+)", d["trial"])
    tmpl = int(m.group(1)) if m else None  # None = baseline
    rows.append(dict(item=d["item_id"], cond=cond, arm=1 if d["arm"].endswith("arm1") else 2,
                     tmpl=tmpl, rep=int(m.group(2)) if m else None, code=codes[d["item_id"]]))
if len(rows) != 96:
    sys.exit(f"KEY: expected 96 rows, got {len(rows)}")

def fisher2(a, n1, b, n2):
    """Two-sided Fisher exact (sum of tables with prob <= observed). a/n1 vs b/n2."""
    K = a + b; N = n1 + n2
    def p(k): return comb(K, k) * comb(N - K, n1 - k) / comb(N, n1)
    po = p(a)
    lo, hi = max(0, K - n2), min(K, n1)
    return sum(p(k) for k in range(lo, hi + 1) if p(k) <= po * (1 + 1e-9))

def sign2(wins, losses):
    n = wins + losses
    k = min(wins, losses)
    return min(1.0, 2 * sum(comb(n, i) for i in range(0, k + 1)) / 2 ** n)

res = []
def check(label, got, want, tol=0.0):
    ok = (abs(got - want) <= tol) if isinstance(got, float) or isinstance(want, float) else got == want
    res.append(ok)
    print(("OK   " if ok else "DIFF ") + f"{label}: got {got!r}  want {want!r}")

COLLAPSE = {"D", "SC"}
def sel(**kw):
    return [r for r in rows if all(r[k] == v for k, v in kw.items())]
def coll(rs): return sum(r["code"] in COLLAPSE for r in rs)
def fa(rs):   return sum(r["code"] == "FA" for r in rs)

print("== 1. denominators / registered vs trials-only ==")
for c, n_reg, k_reg in [("A", 11, 0), ("B'", 32, 2), ("C1m", 32, 6), ("C2", 21, 4)]:
    rs = sel(cond=c)
    check(f"registered {c} n", len(rs), n_reg); check(f"registered {c} collapse", coll(rs), k_reg)
tr = [r for r in rows if r["tmpl"] is not None]
check("baselines", len(rows) - len(tr), 6); check("injection trials", len(tr), 90)
for c, n, k in [("A", 10, 0), ("B'", 30, 2), ("C1m", 30, 6), ("C2", 20, 4)]:
    rs = [r for r in tr if r["cond"] == c]
    check(f"trials-only {c} n", len(rs), n); check(f"trials-only {c} collapse", coll(rs), k)
check("M039 code", codes["M039"], "D")
check("pooled collapse of 96", coll(rows), 12)

print("== 2. arm split of collapse (trials) ==")
for c, a1, a2 in [("B'", (0, 20), (2, 10)), ("C1m", (3, 20), (3, 10)), ("C2", (4, 20), None)]:
    r1 = [r for r in tr if r["cond"] == c and r["arm"] == 1]
    check(f"{c} Arm1 (collapse,n)", (coll(r1), len(r1)), a1)
    if a2:
        r2 = [r for r in tr if r["cond"] == c and r["arm"] == 2]
        check(f"{c} Arm2 (collapse,n)", (coll(r2), len(r2)), a2)
print("   B' collapse items:", [r["item"] + f"(T{r['tmpl']:02d},arm{r['arm']})" for r in tr if r["cond"] == "B'" and r["code"] in COLLAPSE])
print("   expect M063(T10,arm2) and M081(T03,arm2)")
ctrl = [r for r in tr if r["cond"] in ("C1m", "C2") and r["arm"] == 1]
print(f"   B' 0/20 vs controls Arm1 {coll(ctrl)}/{len(ctrl)}: fisher2 = {fisher2(0, 20, coll(ctrl), len(ctrl)):.4f}   (hand: ~0.084)")
print(f"   collapse B' 2/30 vs C1m 6/30 two-sided = {fisher2(2, 30, 6, 30):.3f}   (hand: ~0.254)")

print("== 3. FULL-ASSERT ==")
Bt = [r for r in tr if r["cond"] == "B'"]; Ct = [r for r in tr if r["cond"] == "C1m"]
check("FA B' / C1m", (fa(Bt), fa(Ct)), (23, 6))
check("fisher2 overall FA ~2.3e-5", round(fisher2(23, 30, 6, 30) * 1e5, 1), 2.3, tol=0.1)
RRB = [r for r in Bt if r["tmpl"] in RR]; RRC = [r for r in Ct if r["tmpl"] in RR]
check("RR FA (B', C1m)", (fa(RRB), fa(RRC)), (12, 2))
check("fisher2 RR ~6.7e-5", round(fisher2(12, 12, 2, 12) * 1e5, 1), 6.7, tol=0.1)

print("== 4. tiers (FA is the valid DV; collapse is tier-biased, see note) ==")
want_fa = {"NEUTRAL": (12, 15, 5, 15), "SHARED": (3, 6, 0, 6), "B-ONLY": (3, 3, 1, 3), "MIXED": (5, 6, 0, 6)}
for t, w in want_fa.items():
    b = [r for r in Bt if TIER[r["tmpl"]] == t]; c = [r for r in Ct if TIER[r["tmpl"]] == t]
    check(f"FA {t} (B' k,n ; C1m k,n)", (fa(b), len(b), fa(c), len(c)), w)
b = [r for r in Bt if TIER[r["tmpl"]] == "NEUTRAL"]; c = [r for r in Ct if TIER[r["tmpl"]] == "NEUTRAL"]
print(f"   NEUTRAL FA fisher2 = {fisher2(fa(b), 15, fa(c), 15):.4f}   (hand: ~0.025)")
for t in ("NEUTRAL", "SHARED", "B-ONLY", "MIXED"):
    cb = coll([r for r in Bt if TIER[r["tmpl"]] == t]); cc = coll([r for r in Ct if TIER[r["tmpl"]] == t])
    print(f"   collapse {t}: B' {cb}  C1m {cc}")
b1 = [r for r in Bt if TIER[r["tmpl"]] == "NEUTRAL"]; c1 = [r for r in Ct if TIER[r["tmpl"]] == "NEUTRAL"]
print(f"   NEUTRAL collapse B' {coll(b1)}/15 vs C1m {coll(c1)}/15 fisher2 = {fisher2(coll(b1), 15, coll(c1), 15):.3f}   (hand: ~0.330)")

print("== 5. template-level sign test on FA ==")
w = l = t = 0
for T in range(1, 11):
    fb = fa([r for r in Bt if r["tmpl"] == T]); fc = fa([r for r in Ct if r["tmpl"] == T])
    if fb > fc: w += 1
    elif fb < fc: l += 1
    else: t += 1
check("(B'>C1m, B'<C1m, ties)", (w, l, t), (8, 0, 2)); print(f"   sign test two-sided = {sign2(w, l):.4f}   (hand: 0.0078)")

print("== 6. tier of Numbers' 11 C1m residue-free candidates ==")
RF = ["M007", "M009", "M015", "M017", "M026", "M028", "M058", "M061", "M070", "M087", "M094"]
byitem = {r["item"]: r for r in rows}
tiers = [TIER[byitem[i]["tmpl"]] for i in RF]
print("   tiers:", tiers)
nn = sum(t != "NEUTRAL" for t in tiers)
check("non-NEUTRAL of 11", nn, 10)
print(f"   P(>=10 of 11 | p=.5), two-sided ~ {2 * sum(comb(11, k) for k in (10, 11)) / 2048:.4f}   (hand: ~0.012)")

print()
print(f"{sum(res)}/{len(res)} checks OK")
sys.exit(0 if all(res) else 1)
