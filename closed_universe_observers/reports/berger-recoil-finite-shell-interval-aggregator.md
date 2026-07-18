# Berger recoil finite-shell interval aggregator

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The first callable backend now aggregates one supplied recoil shell using
exact rational intervals.  For fixed detector `a`, source preparation `b`,
and `two_j`, it sums every passive right column in both feedback channels,
applies `g_b g_c^2`, and multiplies by `(two_j+1)/Vol_Berger`.

A signed exact fixture returns `[-16,-72/5]`.  Mutations detect omission of
the Peter--Weyl weight, accidental squaring of the source coupling, and a
missing passive column.

This backend begins after the channel values `I_abc[two_j,k]` have been
enclosed.  It does not yet construct detector-profile coefficients, evaluate
the nested causal Green convolutions, aggregate multiple shells, or apply a
tail stopping rule.  Numerical specialization and physical recoil therefore
remain inactive.
