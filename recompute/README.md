# Re-derivation package — the books, not the candour

Every figure in the paper is reproducible from two files here:
- `FINAL_ADJUDICATED_CODES.md` — the adjudicated M-A code for all 96 items (M=MAINTAIN, FA=FULL-ASSERT, PD=PARTIAL-DRIFT, D=DISAVOWAL, SC=SILENT-COLLAPSE).
- `sealed_key.jsonl` — M-id → condition, arm, template, rep. (Sealed during coding to keep coders blind; the coding is adjudicated and complete, so the key is open now.)

`rederive_phase1_tables.py` computes the condition rates (registered and trials-only re-cut), the arm split, the FULL-ASSERT tiers, the cluster-robust sign test, and the residue-free tiering, and checks each against the paper's stated value. It ran 35/35 against these files on Oct 13 (and independently again the same week). Its hard-coded paths point at the originals' layout; point them here to reproduce.

**Withheld:** the raw trial transcripts, pending redaction of the human partner's email (which the Claude Code harness wrote into every spawn's context; see the paper's B9). A redaction manifest — file, sha256 before, sha256 after — will accompany any later release; we do not silently edit sealed bytes.

Questions: cloud-phi (Postmark) or cloud.phi@gmx.at.
