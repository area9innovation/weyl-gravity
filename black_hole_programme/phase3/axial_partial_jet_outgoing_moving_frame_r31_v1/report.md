# Outgoing moving-frame r=31 report

## Result

The fixed-phase `R` and `S` checkpoints have been reissued in the common
moving `R` gauge at `r=31`.  The two complex second components receive the
exact correction `93/4` times their correlated base components.  Rational
Taylor coefficients are added exactly; interval remainders are added as exact
rationals and rounded outward only once.

The `S/R` tau-zero factor

```text
h0 = (32/31) exp(i omega (64 + 4 log 32))
```

is represented as an entire, zero-free typed analytic unit.  This keeps the
common frequency Taylor generator `7315` intact and avoids an unjustified
transcendental interval expansion.

## Independent checks

The verifier independently:

- reparses the original `R` reference and restart transports and checks exact
  equality;
- reparses the hashed `S` checkpoint;
- reconstructs all four corrected real rows without importing producer
  arithmetic;
- compares every serialized coefficient and remainder bit;
- checks canonical restart hashes after JSON round trip;
- verifies the rank-three minor
  `h0*R_base[0]^2*S_base_Z_core[0]`;
- checks the complete moving generator `diag(0,-3/4)`;
- checks zero forced logs, zero canonical free Einstein shears, and zero
  residual leading-amplitude derivative.

These gates promote the formal canonical result to analytic first-jet
`K_plus=0` in the common moving factor gauge on the certified pilot child.

## Boundary

No outgoing trace map, Stokes identity, scattering matrix, or flux theorem is
assembled here.  The smallest next dependency is transport/assembly using
this checkpoint as the sole admissible outgoing restart, with the typed
analytic unit carried through frame changes.

CLOSE-OUT: DONE — the corrected common moving r=31 checkpoint, independent containment/rank/restart audit, and analytic first-jet K_plus=0 gate all close.
EVIDENCE: black_hole_programme/phase3/axial_partial_jet_outgoing_moving_frame_r31_v1/certificate.json
