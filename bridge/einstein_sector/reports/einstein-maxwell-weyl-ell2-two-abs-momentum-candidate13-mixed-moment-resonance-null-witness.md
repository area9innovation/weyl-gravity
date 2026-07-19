# Candidate-13 mixed moment/resonance-null witness

## Result

On the candidate-13 compact Plebański–Hacyan circumference, there is a
nonzero real axial `ell=2,m=0` Einstein-minus/extra tangent for which all five
stabilizer moment maps and the complete candidate-13 cross-fibre resonance
block vanish.  This is an exact independence witness, not a second-order
extension.

Put

```text
rho=(-250+461*sqrt(10))/2132,
a=6-2*sqrt(3),
b=16/3,
q1=sqrt(rho+a), q2=sqrt(4*rho+a), p1=sqrt(rho+b).
```

Use unit-current axial directions, with current signs `+1` on the extra
`p` branch and `-1` on the Einstein-minus `q` branch.  Set the extra
occupations at signed momenta `(1,-2)` to `(1,0)` and the Einstein-minus
occupations to

```text
y1=p1*(2*p1+q2)/(q1*(2*q1+q2)),
y2=p1*(p1-q1)/(q2*(2*q1+q2)).
```

Both occupations are positive: `rho` lies exactly in `(1/2,3/5)`, and
`p1^2-q1^2=b-a=2*sqrt(3)-2/3>0`.  Direct rational simplification gives

```text
q1^2*y1+q2^2*y2=p1^2,
q1*y1-2*q2*y2=p1.
```

These are precisely the normalized `H` and `P_x` moment equations with the
declared momentum and current signs.  Support only at `m=0` makes the `J_3`
expectation zero, while the `T_1,T_2` selection rules connect only to absent
`m=+/-1` coefficients, so `J_1=J_2=0` as well.

Every candidate-13 cross-fibre equation is bilinear in the extra amplitudes
on the two momentum fibres.  The extra occupation on `n=-2` is zero, so the
witness lies on the independently certified second-fibre-zero sheet.  The
isolated-candidate certificate proves that the 21 admissible cross-fibre
circumferences are pairwise distinct, so no other listed cross-fibre
collision is silently imported at this `rho`.

## Interpretation and boundary

The negative-definite pure-extra Taub theorem does not extend to the mixed
Einstein–extra carrier.  The Einstein-minus branch supplies the opposite
current sign and permits an exact nonzero moment-map null tangent.  Moreover,
candidate 13's cross-fibre resonance does not remove this tangent.

The remaining load-bearing gate is therefore the same-fibre quadratic source
ledger evaluated on this three-occupation witness.  Until that calculation is
done, bounded and smooth-secular second-order extension are `OPEN`; causal
extension is `NO_CERTIFIED_MAP`.  No complete mixed cone, residual observable
or quantum claim is made.

## Verification

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness --check
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_moment_resonance_null_witness
```
