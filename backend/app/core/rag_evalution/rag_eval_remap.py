import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from rag_engine import load_metadata
import json

def remap_eval(eval_path: str, out_path: str):
    meta = load_metadata()
    with open(eval_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # build search map
    mapping = []
    for entry in data:
        answer = entry.get("answer","").strip()
        found_idxs = []
        if not answer:
            # fallback: search by query words
            q = entry.get("query","")
            for i, m in enumerate(meta):
                if q.lower() in m.get("text","").lower():
                    found_idxs.append(i)
        else:
            for i, m in enumerate(meta):
                if answer.lower() in m.get("text","").lower():
                    found_idxs.append(i)
        # fallback heuristics: if nothing found, search tokens
        if not found_idxs:
            # match by any good token
            tokens = [t for t in answer.lower().split() if len(t)>3]
            for i, m in enumerate(meta):
                txt = m.get("text","").lower()
                if all(tok in txt for tok in tokens[:3]):  # require up to 3 tokens
                    found_idxs.append(i)
        entry['expected_chunk_ids'] = found_idxs or entry.get('expected_chunk_ids', [])
        mapping.append(entry)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print(f"Remapped {len(mapping)} entries -> saved {out_path}")

if __name__ == "__main__":
    remap_eval("rag_evalution/eval_dataset.json", "rag_evalution/eval_dataset_remapped.json")
