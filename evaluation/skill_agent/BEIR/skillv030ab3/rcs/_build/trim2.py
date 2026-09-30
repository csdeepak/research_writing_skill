p="_build/draft_src.md"
s=open(p,encoding="utf-8").read()
def rep(a,b):
    global s
    assert a in s,a[:60]; s=s.replace(a,b,1)
rep("with one ranking metric, nDCG@10, and add measurements","with one ranking score computed from human relevance judgements (nDCG@10), and add measurements")
rep("A re-ranking pipeline (BM25+CE) scores above BM25","A re-ranking pipeline (BM25 followed by a cross-encoder, BM25+CE) scores above BM25")
rep("On TREC-COVID, judging previously unjudged results raised","On TREC-COVID, a COVID-19 literature search dataset, judging previously unjudged results raised")
rep("such as MS MARCO (Nguyen et al., 2016) or Natural Questions (Kwiatkowski et al., 2019)","such as MS MARCO (Nguyen et al., 2016), a web-search dataset, or Natural Questions (NQ) (Kwiatkowski et al., 2019)")
rep("Elasticsearch BM25 and RM3 expansion;","Elasticsearch BM25 and RM3 query expansion;")
open(p,"w",encoding="utf-8").write(s)
