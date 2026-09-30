import json
import re

draft = open(".rcs/drafts/v001/paper.md", encoding="utf-8").read()
open("paper_tagged_tmp.md", "w", encoding="utf-8").write("")  # placeholder removed below
import os
os.remove("paper_tagged_tmp.md")

out = []
for line in draft.split("\n"):
    if line.startswith("|"):
        cells = line.strip().strip("|").split("|")
        # drop the trailing Claim column (header 'Claim' or a cell that is only tags)
        last = cells[-1].strip()
        if last == "Claim" or re.fullmatch(r"(\{[CL]\d+\}\s*)+", last):
            cells = cells[:-1]
        line = "| " + " | ".join(c.strip() for c in cells) + " |"
    else:
        line = re.sub(r"\s*\{[CL]\d{3}\}", "", line)
    out.append(line)
text = "\n".join(out)
text = re.sub(r" +([.,;:])", r"\1", text)
text = re.sub(r"[ \t]+\n", "\n", text)
open("paper.md", "w", encoding="utf-8").write(text)
words = len(re.sub(r"\|", " ", text.split("## References")[0]).split())
print("words (incl. tables/headings/appendix, excl. references):", words)
assert not re.search(r"\{[CL]\d{3}\}", text)
