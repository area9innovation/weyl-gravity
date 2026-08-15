# Strict 386-row source q3 common assembly v1

**Result:** `STRICT_386_SOURCE_Q3_COMMON_ASSEMBLY_V1`

**Dependencies:** `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Outcome

The authoritative source `q3` is now assembled on the same 386-row snapshot
as the accepted `q2`.  It combines the arbitrary-input minimal Bach natural
operator with **5952** exact
auxiliary coefficients.  The family census is exhaustive at arity three:
minimal `h,h,h` and shifted-mass `h,h,f_hat,f_hat` are the only two fourth
Taylor families in shifted coordinates.

The arity-three identity is partitioned by source symmetry.  The minimal rail
replays 72 typed channels and
212 paths.  Auxiliary Diff channels
follow from pullback naturality of the weight-one mass density, Weyl channels
pass 605
exact Ward checks, and boost channels vanish because `f_hat` is invariant.
The split and graph identity defects are both **0**.

Quartic cyclicity checks include 40000
pointwise auxiliary equalities plus the minimal integrated-functional theorem
modulo horizontal boundary.  Graph transport has
**40** possible block quadruples and is kept as
an exact compositional DAG.

## Honest boundary

This closes the source-q3 blocker, not Gate A.  Six other top-level freeze
hashes and the final common cyclic contraction remain independent blockers.
No causal Green compatibility, Hadamard, renormalization, or QME claim follows.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_source_q3_common_assembly.py --check
python3 quantum-weyl/classical_import/check_strict_386_source_q3_common_assembly.py
python3 quantum-weyl/classical_import/verify_strict_386_source_q3_common_assembly.py
python3 -m unittest quantum-weyl.classical_import.tests.test_strict_386_source_q3_common_assembly
```
