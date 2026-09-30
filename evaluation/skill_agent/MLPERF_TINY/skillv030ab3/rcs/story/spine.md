# Paper Spine

1. **Problem.** TinyML systems (machine-learning inference on microcontroller-class devices) vary widely in hardware and software, so their accuracy, latency and energy cannot be compared fairly or reproducibly, and the effect of an individual optimization is hard to isolate {C001} {C002}.
2. **Gap.** The authors characterize the existing benchmarks they discuss (CoreMark, MLMark, the MLPerf inference benchmark) as not meeting TinyML needs: not ML workloads, models too large for microcontrollers, or no power measurement {C003}.
3. **Question.** How can one build an open benchmark that measures accuracy, latency and energy across heterogeneous TinyML stacks, compares fairly, and still lets different kinds of contribution be shown {C023} {C025} {C028}?
4. **Approach.** Four benchmark tasks with reference models and open-source reference implementations, quality targets, closed and open divisions, and a standardized measurement framework, developed with more than 50 organizations {C004} {C006} {C008} {C023}.
5. **Key finding.** The reference models clear their quality targets (for example 91.6% against a 90% requirement for keyword spotting), and the June 2021 round produced five diverse submissions in a Table 2 the authors read as showing the modular design accommodating different goals {C012} {C015} {C018}.
6. **Meaning.** In the authors' reading, a modular, two-division benchmark can serve hardware vendors, software vendors and researchers at once {C018} {C027} {C028}.
7. **Main limit.** Streaming inputs and pre-processing are not captured, the closed division covers mainly FC and CNN models, the suite must stay stable while evolving, and the paper gives no submission measurements {L002} {L003} {L004} {L001} {L008}.
