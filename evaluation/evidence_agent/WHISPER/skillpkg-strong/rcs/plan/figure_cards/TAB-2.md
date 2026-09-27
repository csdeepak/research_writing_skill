id: TAB-2
purpose: "show the headline robustness comparison"
rq: N05
takeaway: "Matched on LibriSpeech, zero-shot Whisper Large V2 has less than half the average WER of a supervised wav2vec 2.0 Large model on 12 other datasets."
claims: [C002, C003]
evidence: [E013, E014, E015]
type: table
non_conclusions: "single run, no variance; does not show per-dataset detail beyond LibriSpeech and the average"
placement: "Results, English ASR robustness subsection"
caption: "Average WER (%) on LibriSpeech test-clean and across 12 other datasets. wav2vec 2.0 Large (fine-tuned on LibriSpeech) vs zero-shot Whisper Large V2, after the Whisper text normalizer (source: paper Table 2; RER computed by the authors)."
