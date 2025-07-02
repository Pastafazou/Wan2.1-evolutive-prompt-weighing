"""
Reads feedback/embeddings.jsonl
Outputs feedback/token_weights.json     {token: score}
Outputs feedback/token_ranking.txt      human‑readable list
Scoring:   1‑5  ->  −2 … +2  (centered at 3)
Token cut: keep tokens seen ≥3×
"""

import jsonlines, regex as re, collections, numpy as np, json, pathlib

EMB_FILE = pathlib.Path("feedback/embeddings.jsonl")
OUT_JSON = pathlib.Path("feedback/token_weights.json")
OUT_TXT  = pathlib.Path("feedback/token_ranking.txt")

word_pat = re.compile(r"\p{L}[\p{L}\p{Mn}\p{Pd}'’]*", re.UNICODE)  # words incl. accents

def score(rating):
    """rating 1..5 -> -2..+2"""
    return rating - 3

tok_scores = collections.defaultdict(list)

with jsonlines.open(EMB_FILE) as reader:
    for row in reader:
        prompt  = row.get("prompt", "")
        rating  = int(row.get("ranking", 3))
        s       = score(rating)
        tokens  = word_pat.findall(prompt.lower())
        for t in set(tokens):                # unique per prompt
            tok_scores[t].append(s)

# Compute average score per token & filter
tok_weight = {t: float(np.mean(v)) for t, v in tok_scores.items() if len(v) >= 3}

# Save JSON
OUT_JSON.write_text(json.dumps(tok_weight, ensure_ascii=False, indent=2))
print(f"Wrote {len(tok_weight)} token weights → {OUT_JSON}")

# Save pretty TXT ranking
with OUT_TXT.open("w", encoding="utf-8") as f:
    for t, w in sorted(tok_weight.items(), key=lambda x:-x[1]):
        f.write(f"{w:+.2f}\t{t}\n")
print(f"Wrote human list → {OUT_TXT}")
