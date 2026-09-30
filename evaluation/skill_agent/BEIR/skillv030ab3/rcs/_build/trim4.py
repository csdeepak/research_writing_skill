p="_build/draft_src.md"
s=open(p,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s,a[:60]; s=s.replace(a,b,1)
rep("in which filling in unjudged results changes the scores of dense systems far more than those of lexical systems (Section 5.5)","in which filling in unjudged results raises ANCE from 0.654 to 0.735 but docT5query only from 0.713 to 0.714 (Section 5.5)")
rep("Even so, dense systems fall far below BM25 on some datasets, for example","Even so, dense systems fall below BM25 on some datasets, for example")
rep("Table 4 shows that Hole@10 on TREC-COVID varies by system:","In Table 4, Hole@10 on TREC-COVID varies by system:")
rep("so this shows that label bias can change","so this illustrates that label bias can change")
open(p,"w",encoding="utf-8").write(s)
