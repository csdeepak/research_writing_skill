import json,re
g=json.load(open("_build/grid.json",encoding="utf-8"))
DS,grid,mm,avg=g["datasets"],g["grid"],g["mm"],g["avg"]
SYS=["BM25","DeepCT","SPARTA","docT5query","DPR","ANCE","TAS-B","GenQ","ColBERT","BM25+CE"]
src=open("_build/draft_src.md",encoding="utf-8").read()
reg={s["id"]:s for s in json.load(open("corpus/source_registry.json",encoding="utf-8"))["sources"]}

# ---- Table 1 (README values; task/domain from Figure 1 of the paper)
T1=[("Fact checking","FEVER (Thorne et al., 2018)","Wikipedia","6,666","5.42M","1.2"),
("Fact checking","Climate-FEVER (Diggelmann et al., 2020)","Wikipedia","1,535","5.42M","3.0"),
("Fact checking","SciFact (Wadden et al., 2020)","Scientific","300","5K","1.1"),
("Citation prediction","SCIDOCS (Cohan et al., 2020)","Scientific","1,000","25K","4.9"),
("Duplicate questions","Quora","Quora","10,000","523K","1.6"),
("Duplicate questions","CQADupStack (Hoogeveen et al., 2015)","StackExchange","13,145","457K","1.4"),
("Argument retrieval","Touché-2020 (Bondarenko et al., 2020)","Miscellaneous","49","382K","19.0"),
("Argument retrieval","ArguAna (Wachsmuth et al., 2018)","Miscellaneous","1,406","8.67K","1.0"),
("News retrieval","TREC-NEWS (Soboroff et al., 2019)","News","57","595K","19.6"),
("News retrieval","Robust04 (Voorhees, 2005)","News","249","528K","69.9"),
("Question answering","NQ (Kwiatkowski et al., 2019)","Wikipedia","3,452","2.68M","1.2"),
("Question answering","HotpotQA (Yang et al., 2018)","Wikipedia","7,405","5.23M","2.0"),
("Question answering","FiQA-2018 (Maia et al., 2018)","Finance","648","57K","2.6"),
("Tweet retrieval","Signal-1M (RT) (Suarez et al., 2018)","Twitter","97","2.86M","19.6"),
("Bio-medical","TREC-COVID (Voorhees et al., 2021)","Scientific","50","171K","493.5"),
("Bio-medical","BioASQ (Tsatsaronis et al., 2015)","Scientific","500","14.91M","4.7"),
("Bio-medical","NFCorpus (Boteva et al., 2016)","Scientific","323","3.6K","38.2"),
("Entity retrieval","DBPedia (Hasibi et al., 2017)","Wikipedia","400","4.63M","38.2")]
t1="**Table 1.** BEIR spans 9 tasks and corpora from 3.6K to 14.91M documents, with 1.0 to 493.5 relevant documents per query. Test queries, corpus size and relevant documents per query are from the repository README; domains follow Figure 1 of the paper.\n\n"
t1+="| Task | Dataset | Domain | Test queries | Corpus | Relevant docs per query |\n|---|---|---|---|---|---|\n"
for r in T1: t1+="| "+" | ".join(r)+" |\n"

# ---- Table 2
t2="**Table 2.** BM25+CE is above BM25 on 16 of 18 zero-shot datasets, while DeepCT, SPARTA and DPR are below it on nearly all; no system is best everywhere. nDCG@10 per system, single evaluation each. ‡ marks in-domain scores (MS MARCO for the MS MARCO-trained systems, NQ for DPR). The last row is the paper's 'Avg. Performance vs. BM25' as printed.\n\n"
t2+="| Dataset | "+" | ".join(SYS)+" |\n|---|"+"---|"*len(SYS)+"\n"
row="| MS MARCO (in-domain) | "+" | ".join(("%.3f"%mm[s])+("" if s in("BM25","DPR") else "‡") for s in SYS)+" |\n"
t2+=row
for i,d in enumerate(DS):
    cells=[]
    for s in SYS:
        v="%.3f"%grid[s][i]
        if s=="DPR" and d=="NQ": v+="‡"
        cells.append(v)
    t2+="| "+d+" | "+" | ".join(cells)+" |\n"
t2+="| Avg. vs. BM25 | – | "+" | ".join(avg[s] for s in SYS[1:])+" |\n"

t3="**Table 3.** The best zero-shot systems are the slowest and, for ColBERT, the largest. Estimated single-query latency and index size on 1 million DBPedia documents; – = not reported.\n\n| System | GPU latency | CPU latency | Index size |\n|---|---|---|---|\n| BM25+CE | 450ms | 6100ms | 0.4GB |\n| ColBERT | 350ms | – | 20GB |\n| docT5query | – | 30ms | 0.4GB |\n| BM25 | – | 20ms | 0.4GB |\n| TAS-B | 14ms | 125ms | 3GB |\n| GenQ | 14ms | 125ms | 3GB |\n| ANCE | 20ms | 275ms | 3GB |\n| SPARTA | – | 20ms | 12GB |\n| DeepCT | – | 25ms | 0.4GB |\n| DPR | 19ms | 230ms | 3GB |\n"
H={"BM25":("6.4%",.656,.668),"DeepCT":("19.4%",.406,.472),"SPARTA":("12.4%",.538,.624),"docT5query":("2.8%",.713,.714),"DPR":("30.6%",.332,.445),"ANCE":("14.4%",.654,.735),"TAS-B":("31.8%",.481,.555),"ColBERT":("12.4%",.677,.735),"BM25+CE":("1.6%",.757,.760)}
t4="**Table 4.** Filling TREC-COVID holes barely changes lexical systems but raises dense ones. Hole@10 (share of top-10 results never judged) and nDCG@10 before and after the authors judged the missing pairs; GenQ is not in the source table.\n\n| System | Hole@10 | nDCG@10 original | nDCG@10 annotated |\n|---|---|---|---|\n"
for s,(h,a,b) in H.items(): t4+="| %s | %s | %.3f | %.3f |\n"%(s,h,a,b)
out=src.replace("{{TABLE1}}",t1).replace("{{TABLE2}}",t2).replace("{{TABLE3}}",t3).replace("{{TABLE4}}",t4)

# ---- references: those cited in text
body=out.split("## References")[0]
def key(s):
    a=s["authors"][0].split()[-1];
    return a
lines=[]
used=set()
for sid,s in reg.items():
    first=s["authors"][0]
    sur=first.split()[-1]
    if sid=="SRC-025": sur="van den Oord"
    yr=s["year"]
    pats=[r"%s et al\., %d[ab]?"%(re.escape(sur),yr), r"%s et al\. \(%d\)"%(re.escape(sur),yr), r"%s, %d\b"%(re.escape(sur),yr),r"\(%s, %d\)"%(re.escape(sur),yr)]
    if sid in ("SRC-011","SRC-012","SRC-014","SRC-015"):
        L={"SRC-012":"2019a","SRC-011":"2019b","SRC-014":"2021a","SRC-015":"2021b"}[sid]
        if "%s et al., %s"%(sur,L) in body: used.add(sid)
        continue
    if any(re.search(p,body) for p in pats): used.add(sid)
# disambiguate a/b by manual mapping
AB={"SRC-012":"2019a","SRC-011":"2019b","SRC-014":"2021a","SRC-015":"2021b"}
refs=[]
for sid in sorted(used,key=lambda x:(reg[x]["authors"][0].split()[-1],reg[x]["year"])):
    s=reg[sid]
    au=s["authors"]
    sur=au[0].split()[-1]
    yr=str(s["year"])+AB.get(sid,"")[4:] if sid in AB else str(s["year"])
    names=", ".join(au[:3])+(" et al." if len(au)>3 or "et al." in au else "")
    names=names.replace(", et al. et al.",", et al.")
    ven=(" "+s["venue"]+".") if s.get("venue") else ""
    refs.append("- %s (%s). %s.%s"%(names,yr,s["title"],ven))
out=body+"## References\n\n"+"\n".join(refs)+"\n"
open("drafts/v001/paper.md","w",encoding="utf-8").write(out)
print(len(used),sorted(used))
