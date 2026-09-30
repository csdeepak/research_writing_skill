import re

draft = open(".rcs/drafts/v001/paper.md", encoding="utf-8").read()
out = []
drop = False
prev_table = False
for line in draft.split("\n"):
    if line.startswith("|"):
        cells = line.strip().strip("|").split("|")
        if not prev_table:
            drop = cells[-1].strip() == "Claim"
        prev_table = True
        if drop:
            cells = cells[:-1]
        line = "| " + " | ".join(c.strip() for c in cells) + " |"
    else:
        prev_table = False
        line = re.sub(r"\s*\{[CL]\d{3}\}", "", line)
        line = re.sub(r"(?<=\S) +([.,;:])", r"\1", line)
        line = line.rstrip()
    out.append(line)
text = "\n".join(out)
open("paper.md", "w", encoding="utf-8").write(text)
main = text.split("## References")[0]
words_all = len(re.sub(r"[|]", " ", main).replace("---", " ").split())
print("words incl tables, headings, appendix (excl references):", words_all)
assert not re.search(r"\{[CL]\d{3}\}", text)
