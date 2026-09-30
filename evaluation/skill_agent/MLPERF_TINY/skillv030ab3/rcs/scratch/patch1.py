p = '.rcs/scratch/build_evidence.py'
s = open(p, encoding='utf-8').read()
old = 'Quote: "By establishing a collaborative community,'
new = 'Quote: "The benchmark will standardize the nascent field of TinyML and enable future progress through competition and comparability."; "By establishing a collaborative community,'
assert old in s
s = s.replace(old, new)
old2 = "Impact section, stated by the authors: TinyML has"
assert old2 in s
s = s.replace(old2, "Impact section, stated by the authors: the benchmark will standardize the nascent field of TinyML and enable future progress through competition and comparability; TinyML has")
open(p, 'w', encoding='utf-8').write(s)
