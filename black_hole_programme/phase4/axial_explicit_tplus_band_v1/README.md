# Explicit \(T_+\) band v1 — correlated continuation

This Phase-4 package resumes the last certified common-moving outgoing
partial-jet checkpoint at \(r=979/32\). It advances the joint \(R/S\) base and
intrinsic tangent with one correlated dual-number panel. The direct
sixteen-state expansion is used only as an independent boundary gate.

This is an append-only checkpoint in the explicit-\(T_+\) experiment. Until
the common outgoing frame reaches \(r=4\) and is joined to the typed horizon
frame, it does not establish \(T_+\), reflection amplitudes, a Stokes
identity, or scattering.

## Interaction-picture restart

The successor `interaction_certificate.json` proves, in exact rational
arithmetic and with an independent verifier, the partial-jet
interaction-picture identities

```text
J'    = P^{-1} E P
K'    = P^{-1} D R
dotK' = P^{-1} C R - J P^{-1} D R
```

and the reconstruction

```text
diag(P,P,R) [[I,J,JK+dotK],[0,I,K],[0,0,I]]
 = [[P,dotP,dotQ],[0,P,Q],[0,0,R]].
```

The same record checks reciprocal Riccati chart changes, logarithmic
amplitudes and their intrinsic tangents, plus the scalar Wronskian law.  A
physical center fixture forces reciprocal switches in both the spin-two and
spin-one blocks and agrees with an independently integrated direct jet.

The pinned Forge rail also takes one validated correlated micro-step from
\(r=487/16\) to \(r=3895/128\), preserving generator 7315 and the direct
sixteen-state coefficient/containment gates.  That micro-step is the
interval claim.  The projective/log center calculation is a numerical
consistency fixture, not an interval enclosure.

Run:

```bash
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce --reproduce
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_checkpoint
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.produce_interaction --reproduce
python3 -m black_hole_programme.phase4.axial_explicit_tplus_band_v1.verify_interaction
python3 -m unittest -v black_hole_programme.phase4.axial_explicit_tplus_band_v1.test_interaction_picture
```
