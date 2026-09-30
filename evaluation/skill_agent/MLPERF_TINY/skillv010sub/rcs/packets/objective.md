In the authors' words, this paper is meant to explain why machine-learning inference on
ultra-low-power, microcontroller-class hardware (TinyML) has lacked a fair, standardized way to
compare hardware and software solutions on accuracy, latency, and energy together, and to
present MLPerf Tiny, an open benchmark suite built to close that gap. The paper asks whether one
suite can measure all three metrics on this hardware class while still letting a submitter's
specific hardware or software contribution be shown and directly compared against a shared
reference. It describes what the suite actually is (four reference benchmarks, a fixed
measurement protocol, and a closed/open submission-division structure), and then reports what
happened when real organizations submitted to its first round: five submissions spanning both
divisions and five different hardware and software categories. A reader should come away
understanding what problem this suite solves, how its design resolves the tension between
letting submitters differ and keeping their results comparable, what the first round actually
showed, and which parts of that story rest on strong evidence versus which remain open questions
for later rounds.
