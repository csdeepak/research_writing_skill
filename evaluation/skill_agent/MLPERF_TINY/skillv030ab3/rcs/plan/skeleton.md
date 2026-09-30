# Skeleton (one topic sentence per paragraph slot)

**A.1** Comparing machine-learning inference on microcontroller-class devices is hard; MLPerf Tiny is an open-source suite of four benchmarks that measures accuracy, latency and energy, whose reference models clear their targets and whose first round the authors read as showing a modular design that fits diverse submitters, within stated limits {C001} {C003} {C012} {C015} {C018} {C023} {L002} {L003}.
**I.1** TinyML promises always-on, private, energy-frugal inference, but the diversity of stacks makes systems hard to compare, which is why the authors say a fair, reliable comparison method is needed {C001} {C024}.
**I.2** As the authors describe them, CoreMark, MLMark and the MLPerf inference benchmark each miss part of what TinyML needs {C003}.
**I.3** The paper's aim can be read as three questions: which tasks and targets (RQ1), which rules and measurement (RQ2), and what the first submission round showed (RQ3) {C023} {C025} {C028}.
**I.4** The authors answer with four tasks, open-source reference implementations, two divisions and a measurement framework, built with more than 50 organizations {C023} {C005}.
**I.5** Contributions are numbered and each points to where its evidence sits, followed by a map of the sections {C004} {C006} {C008} {C012} {C015}.
**S2.1** The authors name five challenges: power, memory, hardware heterogeneity, software heterogeneity and the cross-product of stack options {C002}.
**R.1** Along two dimensions, workload realism and power measurement, the three earlier benchmarks leave a gap in the authors' account {C003}.
**M.1** Each benchmark fixes a dataset, a small model and a quality target, summarized in Table 1 {C004}.
**M.2** Keyword spotting and anomaly detection carry choices (feature extraction excluded; toy-car only; AUC) that the authors justify {C030} {C031}.
**M.3** Quality targets sit slightly below reference accuracy so that correct quantized implementations pass {C029}.
**M.4** A closed division fixes models, data and targets; an open division lets submitters change them; the modular reference implementation lets one component be swapped {C006} {C007} {C027} {C028}.
**M.5** Latency and energy are medians of five runs and accuracy is a single pass, run by a host-and-device framework {C008} {C009} {C025} {C026} {C034}.
**R.2** Every reference result sits above its target, by 0.01 AUC up to about 6 accuracy points, on single numbers without spread {C010} {C011} {C012} {C013} {C035}.
**R.3** The authors state the four references meet the minimum accuracy and span a wide range of latency and energy, but the values are not in the available materials {C014}.
**R.4** The June 2021 round had five entries across MCU, RISC-V, single-board computer, accelerator and FPGA hardware, closed and open, none changing the training data {C015} {C016} {C017} {C018}.
**D.1** RQ1-RQ3 are answered at the authors' strength: targets and rules are specified, and the round is read as consistent with the design {C018} {C029} {C027} {C028}.
**D.2** The authors expect standardization and name misuse and e-waste risks; adoption statements are theirs {C020} {C021} {C019}.
**L.1** The authors concede limits on streaming, pre-processing, stability and model coverage {L001} {L002} {L003} {L004}.
**L.2** Additional caveats: missing figure values, no spread, one round, no submission measurements, and README scope {L005} {L006} {L007} {L008} {L009}.
**K.1** MLPerf Tiny specifies how to compare TinyML systems on four tasks; whether it does so fairly across rounds remains to be shown, and the authors plan to extend it {C023} {C022}.
