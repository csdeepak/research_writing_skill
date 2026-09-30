import re
src=open("project/paper.txt",encoding="utf-8").read()+open("project/README_1.md",encoding="utf-8").read()
t=open(".rcs/drafts/v001/paper.md",encoding="utf-8").read().split("## References")[0]
t=re.sub(r"\{[CL]\d{3}(, [CL]\d{3})*\}","",t)
nums=set(re.findall(r"\d[\d,\.]*\d|\d",t))
miss=[n for n in sorted(nums) if n not in src]
print(miss)
