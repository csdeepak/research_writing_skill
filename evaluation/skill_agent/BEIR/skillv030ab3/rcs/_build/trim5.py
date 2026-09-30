def edit(p,pairs):
    s=open(p,encoding="utf-8").read()
    for a,b in pairs:
        assert a in s,a[:60]; s=s.replace(a,b,1)
    open(p,"w",encoding="utf-8").write(s)
edit("_build/assemble.py",[
(" Test queries, corpus size and average relevant documents per query are from the repository README (MS MARCO, used for training and in-domain scores, has 6,980 dev queries, an 8.84M corpus and 1.1 relevant documents per query). Domains follow Figure 1 of the paper."," Test queries, corpus size and relevant documents per query are from the repository README; domains follow Figure 1 of the paper."),
(" The last row is the paper's 'Avg. Performance vs. BM25' as printed. The source table's bold and underline marks and its Recall@100 companion are not reproduced."," The last row is the paper's 'Avg. Performance vs. BM25' as printed."),
])
edit("_build/draft_src.md",[
("Practical constraints shaped three more settings {C015}. SPARTA was re-implemented because the original code is not public, GenQ was capped at 100K target documents per dataset because of resource constraints, and the TREC-NEWS and Touché-2020 label formats were converted for simplicity.","Practical constraints shaped three more settings {C015}: SPARTA was re-implemented because the original code is not public, GenQ was capped at 100K target documents per dataset for lack of resources, and the TREC-NEWS and Touché-2020 label formats were converted for simplicity."),
("None of the following explanations was tested by ablation. The authors read","None of these explanations was tested by ablation. The authors read"),
(" Each dataset has a corpus, test queries and qrels, the relevance judgements: labelled (query, document) pairs, binary or graded, that say which documents are relevant."," Each dataset has a corpus, test queries and qrels: labelled (query, document) pairs, binary or graded, that say which documents are relevant (the relevance judgements)."),
("Lexical retrieval scores a document by the words it shares with the query. BM25 (Robertson et al., 2009), the standard lexical method, weights matching words by their frequency and rarity, and it is the reference against which every neural system in this study is compared {C006}.","Lexical retrieval scores a document by the words it shares with the query. BM25 (Robertson et al., 2009), the standard lexical method, weights matching words by frequency and rarity and is the reference for every neural system in this study {C006}."),
("The authors of BEIR motivate their study with two observations. Creating","The authors motivate the study with two observations. Creating"),
("This presentation of the study reports four contributions.","The study makes four contributions."),
("Table 2 gives nDCG@10 for every system on MS MARCO and on the 18 BEIR datasets. On the MS MARCO","Table 2 gives nDCG@10 per system on MS MARCO and the 18 BEIR datasets. On the MS MARCO"),
("Differences of a few points, such as ArguAna's 0.311 versus 0.315, come without intervals {L007}. ","Small differences, such as ArguAna's 0.311 versus 0.315, come without intervals {L007}. "),
])
