import json
N=[]
def n(id,t,text,claims=None,evidence=None,sources=None,note=None):
    d={"id":id,"type":t,"text":text}
    if claims: d["claims"]=claims
    if evidence: d["evidence"]=evidence
    if sources: d["sources"]=sources
    if note: d["audience_note"]=note
    N.append(d)
n("N01","PROBLEM","Neural retrieval models are usually trained and tested on the same dataset, so their behaviour on other domains and tasks is unknown.",["C002","C004"],sources=["SRC-006","SRC-007"],note="reader must know what retrieval and zero-shot mean")
n("N02","SIGNIFICANCE","Training data are costly, so many retrieval systems are deployed zero-shot.",["C001"])
n("N03","KNOWN","Lexical methods (BM25) dominate retrieval history; neural sparse, dense, late-interaction and re-ranking families each try to close the lexical gap.",["C006"],sources=["SRC-003","SRC-004","SRC-009","SRC-016"],note="define lexical gap, bi-encoder, cross-encoder")
n("N04","KNOWN","Earlier benchmarks (MultiReQA, KILT) cover one task or one domain, small corpora or Wikipedia.",["C005"],sources=["SRC-001","SRC-002"])
n("N05","GAP","Among the benchmarks the paper cites, none evaluates retrieval zero-shot across many tasks and domains with large corpora.",["C003","C005"],sources=["SRC-001","SRC-002"])
n("N06","RQ","RQ1: does in-domain performance predict zero-shot performance?",["C056"])
n("N07","RQ","RQ2: which architectures hold up across heterogeneous datasets, and at what computational cost?",["C056"])
n("N08","RQ","RQ3: does existing relevance annotation treat non-lexical systems fairly?",["C056"])
n("N09","OBJECTIVE","Build a heterogeneous zero-shot benchmark and use it to compare ten systems from five families.",["C020","C022"])
n("N10","APPROACH","BEIR: 18 English datasets, 9 tasks, unified format and software; nDCG@10; MS MARCO-trained checkpoints evaluated without adaptation.",["C010","C011","C012","C013","C014","C015","C020","C021","C022"],sources=["SRC-007"])
n("N11","DESIGN","Zero-shot evaluation of ten systems on 18 datasets with nDCG@10, plus MS MARCO in-domain scores.",["C011","C012","C013","C014"])
n("N12","DESIGN","Latency and index-size measurement on 1M DBPedia documents.",["C040"])
n("N13","DESIGN","Manually judge the unjudged top-10 hits ('holes') of every system on TREC-COVID and re-score.",["C017"])
n("N14","DESIGN","Train two identical models differing only in similarity function to test the document-length preference.",["C016"])
n("N15","RESULT","Zero-shot scores: BM25 strong; BM25+CE and ColBERT best on average; docT5query above BM25 on 11 of 18; dense and sparse-learned often below BM25; GenQ helps specialised domains.",["C030","C031","C032","C033","C034","C035","C036","C039","C043"],evidence=["E050","E052","E070","E072","E073","E075","E077","E078","E086"])
n("N16","RESULT","Best zero-shot systems are the slowest; ColBERT needs the largest index.",["C040"],evidence=["E091","E092","E093"])
n("N17","RESULT","Hole@10 differs widely by system; adding judgements barely changes lexical systems but lifts ANCE and ColBERT.",["C041","C042"],evidence=["E102","E104","E105"])
n("N18","RESULT","Cosine versus dot product changes TREC-COVID nDCG@10 by 15.3 points and the length of retrieved documents.",["C037","C038"],evidence=["E080","E082","E083"])
n("N19","INTERPRETATION","In-domain scores do not order systems as zero-shot scores do; cross-attention style scoring and keyword expansion are the authors' candidate explanations.",["C044","C045","C046","C047"])
n("N20","INTERPRETATION","Accuracy of the best systems is bought with latency and index size.",["C049"])
n("N21","INTERPRETATION","Pools built by lexical systems disadvantage non-lexical systems, at least on TREC-COVID.",["C051","C052"])
n("N22","INTERPRETATION","The similarity function is the authors' explanation for TAS-B's preference for short documents.",["C048"])
n("N23","CONTRIBUTION","A heterogeneous zero-shot retrieval benchmark with software, a ten-system comparison in which no system wins everywhere and BM25 remains strong, and evidence of annotation bias against non-lexical systems.",["C020","C021","C043","C052"])
n("N24","LIMITATION","Benchmark scope: English only, short documents, text only, one or two fields, general-purpose models, datasets used as released.",note="limitations: "+", ".join(["L001","L002","L003","L004","L005","L006","L009","L010","L013"]))
n("N25","LIMITATION","No variance across runs and no total compute reported.",note="limitations: "+", ".join(["L007","L008"]))
n("N26","LIMITATION","TREC-COVID pool still favours lexical systems; unbiased datasets are needed.",note="limitations: "+", ".join(["L011","L012"]))
n("N27","LIMITATION","Writer-derived caveats: one-dataset annotation study, single hardware, confounded systems, average row, count discrepancy, few queries, re-implementations, author-made judgements.",note="limitations: "+", ".join(["L101","L102","L103","L104","L105","L106","L107","L108"]))
n("N28","IMPLICATION","Retrieval methods should be evaluated across many datasets; datasets need diverse pooling.",["C053"])
n("N29","FUTURE","Multilingual, long-document, multi-factor, multi-field and task-specific evaluation.",["C054"])
n("N30","BACKGROUND_CONCEPT","nDCG@10, qrels, pooling and holes, bi-encoder versus cross-encoder versus late interaction, lexical gap.",["C011"],note="each defined at first use")
E=[]
def e(a,b,t): E.append({"from":a,"to":b,"type":t})
for a,b,t in [("N01","N06","motivates"),("N02","N06","motivates"),("N01","N07","motivates"),("N01","N08","motivates"),
 ("N03","N05","establishes"),("N04","N05","establishes"),("N06","N05","addresses"),("N07","N05","addresses"),("N08","N05","addresses"),
 ("N09","N06","operationalizes"),("N09","N07","operationalizes"),("N09","N08","operationalizes"),("N10","N09","implements"),
 ("N11","N15","produces"),("N12","N16","produces"),("N13","N17","produces"),("N14","N18","produces"),
 ("N15","N19","supports"),("N16","N20","supports"),("N17","N21","supports"),("N18","N22","supports"),
 ("N19","N06","answers"),("N19","N07","answers"),("N20","N07","answers"),("N21","N08","answers"),("N22","N07","answers"),
 ("N15","N23","grounds"),("N17","N23","grounds"),("N05","N23","grounds"),
 ("N24","N23","limits"),("N25","N15","limits"),("N26","N17","limits"),("N26","N23","limits"),("N27","N16","limits"),("N27","N17","limits"),
 ("N21","N28","implies"),("N24","N29","opens"),("N28","N29","opens"),
 ("N19","N30","requires"),("N11","N30","requires")]:
    e(a,b,t)
chains=[
 {"experiment":"Zero-shot comparison of ten systems on 18 datasets","rq":"N06","hypothesis":"If in-domain scores predicted zero-shot scores, MS MARCO ordering would match BEIR ordering; a mismatch counts against it.","falsifier":"same ordering in-domain and zero-shot","design_rationale":"C010, C011, C012, C013","observations":["E050","E052","E060"],"claims":["C030","C031","C032","C033","C034","C035","C036","C043","C044"],"limitations":["L007","L103"],"next":"Cost: the best systems are slower, so what do latency and index size look like?"},
 {"experiment":"Latency and index size on 1M DBPedia documents","rq":"N07","hypothesis":"Systems that score best zero-shot pay in latency and index size.","falsifier":"best systems are also fast and small","design_rationale":"efficiency matters for real-time use (authors' framing: models compare a query against millions of documents)","observations":["E091","E092","E093"],"claims":["C040","C049"],"limitations":["L008","L102"],"next":"Why do some dense systems fall below BM25 (TREC-COVID)? Look at labels and at document length."},
 {"experiment":"TREC-COVID hole annotation","rq":"N08","hypothesis":"Missing judgements disadvantage non-lexical systems.","falsifier":"scores of dense systems unchanged after annotation","design_rationale":"C017","observations":["E102","E104"],"claims":["C041","C042","C052"],"limitations":["L011","L101","L108"],"next":"A second cause of dense-model differences: retrieved document length."},
 {"experiment":"Cosine versus dot-product model","rq":"N07","hypothesis":"The similarity function determines whether short or long documents are retrieved.","falsifier":"same length distribution under both similarity functions","design_rationale":"C016","observations":["E082","E083"],"claims":["C038","C048"],"limitations":["L012"],"next":"Wrap up: what the benchmark shows and what it cannot."}]
sg={"pattern":"question_led","nodes":N,"edges":E,"experiment_chains":chains}
json.dump(sg,open("story/story_graph.json","w",encoding="utf-8"),indent=1,ensure_ascii=False)
spine="""# Paper spine

1. Problem: Neural retrieval models are usually trained and tested on the same dataset, so how they behave on other domains and tasks (where no training data exist) is unknown, although zero-shot use is common because training data are costly. {C001} {C002} {C004}
2. Gap: The benchmarks the paper cites cover a single task or domain, small corpora or Wikipedia only, so they cannot compare retrieval systems zero-shot across many tasks and domains. {C003} {C005}
3. Question: Does in-domain performance predict zero-shot performance, which architectures hold up across heterogeneous datasets and at what computational cost, and does relevance annotation treat non-lexical systems fairly? {C056}
4. Approach: BEIR collects 18 English datasets from 9 retrieval tasks in one format with software, and evaluates ten systems from five architecture families zero-shot with nDCG@10, plus latency, index size and a manual re-annotation of TREC-COVID. {C020} {C021} {C022}
5. Key finding: No system wins on every dataset and BM25 remains a strong baseline; BM25+CE (16 of 18 datasets above BM25) and ColBERT (9 of 18) are best on average but slowest, while learned sparse and dense systems that beat BM25 in-domain often fall below it zero-shot. {C043} {C032} {C040}
6. Meaning: In-domain scores do not order systems as zero-shot scores do, and part of the dense systems' shortfall on TREC-COVID reflects missing relevance judgements (ANCE 0.654 to 0.735 after annotation). {C044} {C052}
7. Main limit: Results are single runs on English text-only datasets without variance estimates, and the TREC-COVID pool remains lexically biased, so score differences between systems are not backed by intervals. {L007} {L001} {L011}
"""
open("story/spine.md","w",encoding="utf-8").write(spine)
