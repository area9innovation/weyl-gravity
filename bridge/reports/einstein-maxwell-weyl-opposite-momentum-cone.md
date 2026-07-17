# Paired opposite-momentum moment-map cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The single-travelling-block no-go does not extend to a pair of opposite
compact momenta.  For fixed generic `ell` and nonzero allowed `|k|`, the
complete common stabilizer-zero locus is the inverse image of five linear
charge equations inside six positive-semidefinite rank strata: the three
current-sign branches at `+k` and at `-k`.

In particular, equal branch densities at opposite momenta cancel `P_x`.
Choosing rank-one `m=0` densities cancels all rotations, and

```text
a_minus = (omega_plus^2 a_plus + omega_extra^2 a_extra)/omega_minus^2
```

cancels `H`.  Thus every generic `(ell,|k|)` block has a nonzero
two-parameter standing-wave Taub-zero face.

This does not yet prove a second-order extension.  Relative phases are
invisible to the density moment maps but enter the quadratic source.  The
next detector must retain those phases.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_cone --verify bridge/certificates/einstein_maxwell_weyl_opposite_momentum_cone.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_opposite_momentum_cone.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_opposite_momentum_cone
```
