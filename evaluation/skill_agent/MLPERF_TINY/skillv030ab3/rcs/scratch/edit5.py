p = ".rcs/scratch/build_evidence.py"
s = open(p, encoding="utf-8").read()
marker = "doc = {"
add = '''add("observation", "Related work overall, as stated by the authors: there are a few ML related hardware benchmarks, but none that accurately represent the performance of TinyML workloads on tiny hardware; there is a clear and distinct need for a TinyML benchmark that caters to the unique needs of ML workloads, makes power a first-class citizen and prescribes a methodology that suits TinyML.",
    "lines 30, 33 (section 3)", 'Quote: "none that accurately represent the performance of TinyML workloads on tiny hardware"; "there is a clear and distinct need for a TinyML benchmark"')  # E065

'''
assert marker in s and "E065" not in s
s = s.replace(marker, add + marker, 1)
open(p, "w", encoding="utf-8").write(s)

p = ".rcs/scratch/build_claims.py"
s = open(p, encoding="utf-8").read()
a = '"literature", ["E040", "E041", "E042"]'
assert a in s
s = s.replace(a, '"literature", ["E040", "E041", "E042", "E065"]')
open(p, "w", encoding="utf-8").write(s)

p = ".rcs/drafts/v001/paper.md"
s = open(p, encoding="utf-8").read()
a = "None combines ML workloads small enough for microcontrollers with power measurement {C003}."
assert a in s
s = s.replace(a, "The authors state that none accurately represents the performance of TinyML workloads on tiny hardware {C003}.")
open(p, "w", encoding="utf-8").write(s)
