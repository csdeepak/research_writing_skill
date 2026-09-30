import json
P = "project/paper.txt"
S = []


def add(first, authors_note, year, title, venue, status, quote, loc, statement, role, why):
    sid = "SRC-%03d" % (len(S) + 1)
    S.append({
        "id": sid, "title": title, "as_cited": title, "title_status": "as_cited",
        "authors": [first] + ([authors_note] if authors_note else []), "year": year, "venue": venue,
        "doi": None, "url": None, "publication_status": status,
        "level": 2, "domain": "TinyML / embedded ML",
        "verification": {"method": "user_supplied_file", "date": "2026-09-29", "verified_by": "agent", "retraction_checked": False},
        "read_depth": "abstract",
        "establishes": [{"statement": statement, "support_quote": quote, "location": loc, "strength": "as characterised by the MLPerf Tiny authors; source not read"}],
        "why_useful": why, "informs_sections": [role],
        "evidence_quality": "low",
        "limitations": "Registered from the project's own reference list and citing sentence only (no web, source not read). Publication status inferred from the citation string; not independently verified. May be used only to say what the MLPerf Tiny paper says the work is or provides.",
        "permitted_use": ["content_citation"],
    })


add("Gal-On", "and M. Levy", 2012, "Exploring coremark a benchmark maximizing simplicity and efficacy", "The Embedded Microprocessor Benchmark Consortium", "TECHNICAL_REPORT",
    "EEMBC's CoreMark benchmark [9] has become the standard benchmark for MCU-class devices due to its ease of implementation and use of real algorithms.", "paper.txt line 31 (section 3)",
    "The MLPerf Tiny authors describe CoreMark as the standard MCU-class benchmark that does not profile full programs or represent ML inference.", "Related work", "Names the general-purpose MCU benchmark against which the gap is set.")
add("Reddi", "et al.", 2019, "Mlperf inference benchmark", None, "PREPRINT",
    "MLPerf, a community-driven benchmarking effort, has recently introduced a benchmarking suite for ML inference [18] and has plans to add power measurements.", "paper.txt line 33 (section 3)",
    "The MLPerf Tiny authors describe the MLPerf inference benchmark as precluding MCUs for lack of small benchmarks and compatible implementations.", "Related work", "Names the closest existing ML inference benchmark. Venue not given in the project reference list.")
add("Banbury", "et al.", 2021, "Micronets: Neural network architectures for deploying tinyml applications on commodity microcontrollers", "Proceedings of Machine Learning and Systems, 3", "PEER-REVIEWED",
    "The benchmarks have already acted as a standard set of tasks for TinyML research [4]", "paper.txt line 195 (section 7); also cited line 12 for energy efficiency",
    "The MLPerf Tiny authors cite this work for the use of the benchmarks as a standard set of tasks for TinyML research.", "Introduction; Discussion", "Cited by the authors for adoption of the benchmark tasks.")
add("Bouguera", "et al.", 2018, "Energy consumption model for sensor nodes based on lora and lorawan", "Sensors, 18(7):2104", "PEER-REVIEWED",
    "avoiding the energy cost associated with wireless communication, which at this scale is far higher than that of compute [5]", "paper.txt line 12 (section 1)",
    "The MLPerf Tiny authors cite this work for wireless communication energy cost being far higher than compute at this scale.", "Introduction", "Supports the authors' motivation for on-device inference.")
add("Chowdhery", "et al.", 2019, "Visual wake words dataset", "CoRR, abs/1906.05721", "PREPRINT",
    "The Visual Wakewords challenge [6] tasked submitters with detecting whether at least one person is in an image.", "paper.txt line 53 (section 4.1)",
    "The MLPerf Tiny authors describe the Visual Wake Words challenge as detecting whether at least one person is in an image.", "Method", "Origin of the visual wake words task.")
add("David", "et al.", 2020, "Tensorflow lite micro: Embedded machine learning on tinyml systems", "arXiv preprint arXiv:2010.08678", "PREPRINT",
    "using TFLite for Microcontrollers (TFLM) [7] on the NUCLEO-L4R5ZI board", "paper.txt line 36 (section 4)",
    "The MLPerf Tiny authors run the reference models with TFLite for Microcontrollers, cited to this work.", "Method", "Names the inference runtime of the reference implementations.")
add("He", "et al.", 2016, "Deep residual learning for image recognition", "IEEE conference on computer vision and pattern recognition, pages 770-778", "PEER-REVIEWED",
    "The Image Classification model is a customized ResNetv1 [10]", "paper.txt line 60 (section 4.2)",
    "The MLPerf Tiny authors base the image classification model on ResNetv1.", "Method", "Origin of the ResNet family used for image classification.")
add("Howard", "et al.", 2017, "Mobilenets: Efficient convolutional neural networks for mobile vision applications", "arXiv preprint arXiv:1704.04861", "PREPRINT",
    "The Visual Wakewords model is a MobilenetV1 [11]", "paper.txt line 55 (section 4.1)",
    "The MLPerf Tiny authors use MobileNetV1 for visual wake words.", "Method", "Origin of the visual wake words model.")
add("Lin", "et al.", 2014, "Microsoft coco: Common objects in context", "European conference on computer vision, pages 740-755", "PEER-REVIEWED",
    "The Visual Wakewords Challenge uses the MSCOCO 2014 dataset [15]", "paper.txt line 54 (section 4.1)",
    "The MLPerf Tiny authors use MSCOCO 2014 as the source of the visual wake words data.", "Method", "Source dataset of visual wake words.")
add("Krizhevsky", "et al.", 2009, "Cifar-10 (canadian institute for advanced research)", None, "TECHNICAL_REPORT",
    "CIFAR-10 [14] is a labeled subset of the 80 Million Tiny Images dataset [20].", "paper.txt line 59 (section 4.2)",
    "The MLPerf Tiny authors use CIFAR-10 for image classification.", "Method", "Source dataset of image classification.")
add("Torralba", "et al.", 2008, "80 million tiny images: A large data set for nonparametric object and scene recognition", "IEEE transactions on pattern analysis and machine intelligence, 30(11):1958-1970", "PEER-REVIEWED",
    "CIFAR-10 [14] is a labeled subset of the 80 Million Tiny Images dataset [20].", "paper.txt line 59 (section 4.2)",
    "The MLPerf Tiny authors describe CIFAR-10 as a labeled subset of the 80 Million Tiny Images dataset.", "Method", "Parent dataset of CIFAR-10.")
add("Warden", None, 2018, "Speech commands: A dataset for limited-vocabulary speech recognition", "arXiv preprint arXiv:1804.03209", "PREPRINT",
    "We used the Speech Commands v2 dataset[21], a collection of 105,829 utterances collected from 2,618 speakers", "paper.txt line 67 (section 4.3)",
    "The MLPerf Tiny authors use Speech Commands v2 for keyword spotting.", "Method", "Source dataset of keyword spotting.")
add("Zhang", "et al.", 2017, "Hello edge: Keyword spotting on microcontrollers", "arXiv preprint arXiv:1711.07128", "PREPRINT",
    "we used the small depthwise-separable CNN described in [22]", "paper.txt line 68 (section 4.3)",
    "The MLPerf Tiny authors use the small depthwise-separable CNN described in this work for keyword spotting.", "Method", "Origin of the keyword spotting model.")
add("Koizumi", "et al.", 2019, "Toyadmos: A dataset of miniaturemachine operating sounds for anomalous sound detection", "2019 IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA), pages 313-317", "PEER-REVIEWED",
    "the DCASE2020 [13] competition, which is itself a combination of two publicly available sources: the ToyADMOS [12], and the MIMII [17] datasets", "paper.txt line 72 (section 4.4)",
    "The MLPerf Tiny authors state that the DCASE2020 data combine ToyADMOS and MIMII.", "Method", "One of the two sources of the anomaly detection data.")
add("Koizumi", "et al.", 2020, "Description and discussion on DCASE2020 challenge task2: Unsupervised anomalous sound detection for machine condition monitoring", "arXiv e-prints: 2006.05822", "PREPRINT",
    "we have selected to use the dataset from the DCASE2020 [13] competition", "paper.txt line 72 (section 4.4)",
    "The MLPerf Tiny authors take the anomaly detection dataset from the DCASE2020 competition.", "Method", "Source competition of the anomaly detection benchmark.")
add("Purohit", "et al.", 2019, "Mimii dataset: Sound dataset for malfunctioning industrial machine investigation and inspection", "arXiv preprint arXiv:1909.09347", "PREPRINT",
    "the ToyADMOS [12], and the MIMII [17] datasets", "paper.txt line 72 (section 4.4)",
    "The MLPerf Tiny authors state that the DCASE2020 data combine ToyADMOS and MIMII.", "Method", "One of the two sources of the anomaly detection data.")
add("Fedorov", "et al.", 2019, "Sparse: Sparse architecture search for cnns on resource-constrained microcontrollers", "Advances in Neural Information Processing Systems 32, pages 4978-4990", "PEER-REVIEWED",
    "A significant amount of prior work in TinyML has used CIFAR-10 as a target dataset [8]", "paper.txt line 59 (section 4.2)",
    "The MLPerf Tiny authors cite this work as an example of prior TinyML work on CIFAR-10.", "Method", "Supports the authors' reason for choosing CIFAR-10.")
add("Asanovic", "and D. A. Patterson", 2014, "Instruction sets should be free: The case for risc-v", "EECS Department, University of California, Berkeley, Tech. Rep. UCB/EECS-2014-146", "TECHNICAL_REPORT",
    "RISC-V is a free, open standard instruction set architecture (ISA) [3].", "paper.txt line 190 (section 6.2)",
    "The MLPerf Tiny authors cite this report for RISC-V as a free, open standard instruction set architecture.", "Results", "Defines RISC-V for the reader.")

json.dump({"sources": S}, open(".rcs/corpus/source_registry.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(len(S))
