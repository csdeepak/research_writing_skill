Intended readers: machine-learning researchers from other subfields (adjacent researchers). They
know general machine learning, deep learning, standard evaluation practice, and statistics, but
not this project's subfield-specific terminology, datasets, or prior work.

They can be assumed to know: supervised classification and its standard metrics (Top-1 accuracy,
AUC-ROC); convolutional neural networks; quantization as a general idea; standard training/test
splits; the general concept of edge or on-device inference at phone- or GPU-class scale; and
standard reporting practice (baselines, ablations, reporting negative or absent results).

They cannot be assumed to know: TinyML-specific terminology (TFLite Micro, device under test,
inferences-per-second, post-training quantization vs. quantization-aware training as
microcontroller-deployment concepts); the resource envelope of microcontroller-class hardware
compared with phone- or GPU-class deployment; the specific datasets used here (Speech Commands,
the Visual Wake Words task, DCASE2020/ToyADMOS/MIMII) and their role in prior TinyML work; prior
embedded/TinyML benchmarks (CoreMark, MLMark) and why they do not already solve this problem; or
MLPerf's own broader inference-benchmark tradition and why its existing suite does not cover this
hardware class.

Binding reader types for this review:
A (specialist in this exact subfield) -- checks precision and full rigor.
B (adjacent researcher, the primary intended reader) -- needs subfield terms defined, the gap
explained, and intuition for each design choice.
E (mixed audience) -- needs each section to open accessibly and then deepen.

Venue type: report (no specific venue was designated; the paper is written to stand alone for the
audience above).
