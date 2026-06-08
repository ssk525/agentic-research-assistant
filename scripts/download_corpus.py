import json
import os
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MANIFEST = Path("data/corpus_manifest.json")
OUT_DIR = Path("data/corpus")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
	manifest = json.loads(MANIFEST.read_text())
	for item in manifest:
		aid = item["arxiv_id"]
		out = OUT_DIR / f"{aid}.pdf"
		if out.exists():
			print(f"already have {aid}")
			continue
		url = f"https://arxiv.org/pdf/{aid}.pdf"
		print(f"downloading {aid} - {item['title']}")
		urllib.request.urlretrieve(url, out)
		time.sleep(3)  # respect arXiv rate limits

	count = len(list(OUT_DIR.glob("*.pdf")))
	print(f"Corpus ready: {count} PDFs in {OUT_DIR}")


if __name__ == "__main__":
	main()
