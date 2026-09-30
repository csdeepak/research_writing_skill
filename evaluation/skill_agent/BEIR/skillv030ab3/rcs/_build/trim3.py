def edit(p,pairs):
    s=open(p,encoding="utf-8").read()
    for a,b in pairs:
        assert a in s,a[:60]; s=s.replace(a,b,1)
    open(p,"w",encoding="utf-8").write(s)
edit("_build/claims.py",[
("with average query lengths of 3 to 192 words and average document lengths of 11 to 635 words; only 8 of the 19 datasets (counting MS MARCO) have training data.","with average query lengths of 3 to 192 words and average document lengths of 11 to 635 words; 8 of the 19 datasets (counting MS MARCO) have training data."),
("BM25 remains a strong baseline, with only BM25+CE (16 of 18) scoring above it on nearly all datasets, while","BM25 remains a strong baseline, with BM25+CE (16 of 18) the one system scoring above it on nearly all datasets, while"),
("while ANCE rose from 0.654 to 0.735, 6.7 points","while ANCE rose from 0.654 to 0.735 nDCG@10, 6.7 points"),
])
edit("_build/draft_src.md",[
("a COVID-19 literature search dataset, judging","a search dataset over COVID-related papers, judging"),
("Every score is a single evaluation without variance estimates, all datasets are English, and the label-bias measurement covers one dataset","Every score is a single evaluation without variance estimates, the benchmark is English-only, and the label-bias measurement covers one dataset"),
])
