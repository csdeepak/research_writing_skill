def edit(p,pairs):
    s=open(p,encoding="utf-8").read()
    for a,b in pairs:
        assert a in s,a[:60]; s=s.replace(a,b,1)
    open(p,"w",encoding="utf-8").write(s)
edit("_build/draft_src.md",[
(", so documents are encoded once in advance",""),
("Earlier benchmarks do not fill this need. According to the paper, MultiReQA","According to the paper, earlier benchmarks do not fill this need. MultiReQA"),
("The repository README lists 17 preprocessed datasets for download; four (BioASQ, Signal-1M (RT), TREC-NEWS and Robust04) are not public and come with reproduction instructions {C021}.","The README lists 17 preprocessed datasets for download; four (BioASQ, Signal-1M (RT), TREC-NEWS, Robust04) are not public and come with reproduction instructions {C021}."),
])
edit("_build/assemble.py",[
("Estimated single-query latency and index size for 1 million DBPedia documents; – means not reported.","Estimated single-query latency and index size on 1 million DBPedia documents; – = not reported."),
(" Hole@10 (share of top-10 results never judged) and nDCG@10 before and after the authors judged the missing pairs. GenQ is not in the source table."," Hole@10 (share of top-10 results never judged) and nDCG@10 before and after the authors judged the missing pairs; GenQ is not in the source table."),
])
