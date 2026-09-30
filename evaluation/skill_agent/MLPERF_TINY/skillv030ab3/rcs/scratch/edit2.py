p = ".rcs/scratch/build_claims.py"
s = open(p, encoding="utf-8").read()
R = [
 ('["the suite specifies", "the paper describes"], lims=["L004"])', '["the suite specifies", "the paper describes"], lims=["L004"], sources=["SRC-005", "SRC-007", "SRC-008", "SRC-009", "SRC-010", "SRC-011", "SRC-012", "SRC-013", "SRC-014", "SRC-015", "SRC-016"])'),
 ('["the paper describes", "the reference implementation runs"])', '["the paper describes", "the reference implementation runs"], sources=["SRC-006"])'),
 ('["the round included", "Table 2 lists"], lims=["L007", "L008"])', '["the round included", "Table 2 lists"], lims=["L007", "L008"], sources=["SRC-018"])'),
 ('origin=AS, rationale="design_choice")\nC("C033"', 'origin=AS, rationale="design_choice", sources=["SRC-017"])\nC("C033"'),
]
for a, b in R:
    assert a in s, a[:50]
    s = s.replace(a, b, 1)
open(p, "w", encoding="utf-8").write(s)

q = ".rcs/drafts/v001/paper.md"
t = open(q, encoding="utf-8").read()
t = t.replace("This mapping is our reading of the authors' stated reasons", "This mapping is a reading of the authors' stated reasons")
t = t.replace("- Bouguera, T.", "- Asanovic, K., and Patterson, D. A. (2014). Instruction sets should be free: The case for risc-v. EECS Department, University of California, Berkeley, Tech. Rep. UCB/EECS-2014-146.\n- Bouguera, T.")
open(q, "w", encoding="utf-8").write(t)
