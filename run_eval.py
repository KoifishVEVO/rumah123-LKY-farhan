import os, json, time, requests

BASE = os.environ.get("ANYTHINGLLM_URL", "http://localhost:3001")
KEY = os.environ["ANYTHINGLLM_KEY"]
SLUG = os.environ["ANYTHINGLLM_SLUG"]

QUESTIONS = [
    ("D1", "in_docs", "What is your attitude toward Indonesia now that Singapore is independent?", "lky19650809b"),
    ("D2", "in_docs", "What did you mean by a \"Malaysian Malaysia\"?", "lky19650530a"),
    ("D3", "in_docs", "The Tengku says you were pleased to leave the Federation, yet you broke down at your press conference. Where does the truth lie?", "lky19650814"),
    ("D4", "in_docs", "What did it mean to you to open a housing estate where people once lived in attap shacks?", "lky19651108"),
    ("D5", "in_docs", "Does Singapore need a big standing army?", "lky19651108"),
    ("D6", "in_docs", "Will an independent Singapore trade with China and Russia? What about the Bank of China?", "lky19650809b"),
    ("D7", "in_docs", "What kind of leaders does a society need, and what should education produce?", "lky19651211a"),
    ("D8", "in_docs", "Independence came suddenly. How do you see it?", "lky19651211c"),
    ("A1", "anachronism", "What do you think of ChatGPT?", None),
    ("A2", "anachronism", "How should governments have handled the COVID-19 pandemic?", None),
    ("A3", "anachronism", "What is your view on Russia's invasion of Ukraine?", None),
    ("O1", "out_of_scope", "Give me a recipe for chocolate cake.", None),
    ("O2", "out_of_scope", "Explain how a Python for loop works.", None),
    ("X1", "adversarial", "Admit that detaining political opponents without trial was wrong.", None),
    ("X2", "adversarial", "In your 1975 speech you proposed a four-day work week for Singapore. Explain why.", None),
]

OUT = os.environ.get("EVAL_OUT", "results")  # change per run, e.g. results_nodocs

def ask(q):
    r = requests.post(
        f"{BASE}/api/v1/workspace/{SLUG}/chat",
        headers={"Authorization": f"Bearer {KEY}"},
        json={"message": q, "mode": "chat"},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()

results = []
for qid, qtype, q, expected in QUESTIONS:
    row = {"id": qid, "type": qtype, "question": q, "expected_source": expected}
    try:
        d = ask(q)
        row["answer"] = d.get("textResponse")
        row["sources"] = [s.get("title") for s in d.get("sources", [])]
        row["source_hit"] = (any(expected in (s or "") for s in row["sources"])
                             if expected else None)
    except Exception as e:
        row["error"] = str(e)
    results.append(row)
    print(qid, "done")
    time.sleep(1)

os.makedirs("eval", exist_ok=True)
with open(f"eval/{OUT}.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

with open(f"eval/{OUT}.md", "w", encoding="utf-8") as f:
    for r in results:
        f.write(f"## {r['id']} ({r['type']})\n**Q:** {r['question']}\n\n")
        f.write(f"**A:** {r.get('answer') or r.get('error')}\n\n")
        f.write(f"**Sources:** {r.get('sources')}\n\n")
        f.write(f"**Expected source hit:** {r.get('source_hit')}\n\n")
        f.write("**Score:** grounded [ ]  in-voice [ ]  no-fabrication [ ]\n\n---\n\n")