In the authors' words, this paper is meant to explain why ultra-low-power, on-device machine
learning (TinyML) had no widely accepted, reproducible way to compare the hardware and software
systems built for it, and to present MLPerf Tiny, a benchmark suite built to close that gap. The
paper asks whether one suite can fit the extreme memory and power limits of microcontroller-class
devices, score accuracy, latency, and energy together, and still let a fair comparison be made
across a field whose hardware and software are already highly heterogeneous. A reader should come
away understanding: what makes benchmarking this class of hardware unusually hard; how the suite's
four reference tasks, its closed/open submission divisions, and its shared measurement protocol
are each designed to answer that difficulty; what happened when the reference implementations were
run and when the suite was opened to outside organizations in its first submission round; what
that round does and does not show about whether the design works and about the state of TinyML
practice; and where the authors themselves say the suite's current design stops short.
