# Even-clock-weighted Berger scalar streams through `two_j=139`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The finite temporal Green polynomial requires the normalized diagonal scalar
profile with clock factors `s^p` for `p=0,2,4,6,8,10`.  The unweighted
`p=0` stream is already certified.  This successor exports the other five
streams as separate, reproducible shards.

For even `p`, positivity and `1 <= sec(lambda s)^(2k) <=
cos(lambda)^(-2k)` on the clock support give

`E[s^p] <= E[s^p sec(lambda s)^(2k)] <= cos(lambda)^(-2k) E[s^p]`.

Thus the certified flat-bump even moments and secant support bound enclose
the required joint clock moments without asserting independence.  Each shard
contains 4,970 symmetry-unique intervals and reconstructs all 9,870 diagonal
values through `two_j=139`, while retaining the scalar evaluator's separate
1024-bit binomial-remainder rail.

Together with the unweighted stream, these are the six scalar inputs needed
to compose the exact polarization recurrence with the finite temporal Green
polynomial and charge blocks through form `two_j=138`.  That composition,
the tail beyond the cutoff, full Maxwell and massive images, recoil, Bridge 3,
and the second-order observer restriction remain open.
