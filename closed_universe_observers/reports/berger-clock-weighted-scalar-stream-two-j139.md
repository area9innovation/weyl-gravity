# Even-clock-weighted Berger scalar streams through `two_j=139`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The finite temporal Green polynomial requires the normalized diagonal scalar
profile with the external polarization factor `a(t)=cos(lambda s)` and clock
factors `s^p` for `p=0,2,4,6,8,10`.  This successor exports all six temporal
powers as separate, reproducible shards with the external factor included.

For even `p`, the required joint factor is `s^p sec(lambda s)^(2k-1)`.
Positivity and the certified lower bound on `cos(lambda s)` give

`cos(lambda)E[s^p] <= E[s^p cos(lambda s)] <= E[s^p]` for `k=0`, and

`E[s^p] <= E[s^p sec(lambda s)^(2k-1)] <=
cos(lambda)^(-(2k-1)) E[s^p]` for `k>=1`.

Thus the certified flat-bump even moments and secant support bound enclose
the required joint clock moments without asserting independence.  Each shard
contains 4,970 symmetry-unique intervals and reconstructs all 9,870 diagonal
values through `two_j=139`, while retaining the scalar evaluator's separate
1024-bit binomial-remainder rail.

These are the six scalar inputs needed to compose the exact polarization
recurrence with the finite temporal Green polynomial and charge blocks
through form `two_j=138`.  That composition,
the tail beyond the cutoff, full Maxwell and massive images, recoil, Bridge 3,
and the second-order observer restriction remain open.
