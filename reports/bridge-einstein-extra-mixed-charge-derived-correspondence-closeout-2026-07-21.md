# Mixed-charge derived Einstein/extra correspondence closeout

## Outcome

The failed projection to separately neutral Einstein and extra-Weyl fibres is
replaced by the exact two-jet homotopy pullback

```text
C = (E x X) x^h_(O x O) O_anti,
Delta_anti(c) = (c,-c),
d eta_E = kappa_E-c,
d eta_X = kappa_X+c,
O = span{H,P_x,J1,J2,J3}.
```

The charge-transfer coordinate `c` is essential. It records opposite
component charges while the summed Weyl charge is derived-zero. The strict
presentation is quasi-isomorphic to the minimal five-generator total-charge
Koszul model: `alpha=eta_E+eta_X` obeys
`d alpha=kappa_E+kappa_X`, while `beta=(eta_X-eta_E)/2` and
`c'=c+(kappa_X-kappa_E)/2` form a contractible pair.

## Exact finite-carrier result

On the real `ell=2,m=0,k=0` balanced two-amplitude carrier, the strict tangent
complex has dimensions `7 -> 10`, differential rank five, and cohomology
dimensions `H0=2`, `H1=5`. The exact point has

```text
c_H = 48*(-6+5*sqrt(3))/5,
kappa_E = c,
kappa_X = -c,
kappa_W = 0.
```

Both projected charges are nonzero. Consequently the point belongs to the
mixed correspondence and total Weyl derived zero fibre, but not to either
separate neutral branch. Mutations deleting `c`, replacing the anti-diagonal
by the diagonal, dropping one Koszul half, or asserting separate neutral
projections are rejected.

## Map and form disposition

- The pre-residual ambient inclusion `E -> W` and cofiber projection `W -> X`
  remain certified.
- `C -> Z_W`, `C -> E`, and `C -> X` are honest derived or ambient maps.
- `C -> Z_E x Z_X` is obstructed by the exact balanced witness.
- The diagonal compact stabilizer action is honest: `c` transforms
  coadjointly and the anti-diagonal equations are equivariant.
- `j^*Omega_W` and `p_X^*S_X` are honest pullback forms.
- The lift-invariant Schur form is not a pairing produced by quotienting the
  nonlinear correspondence; no such quotient map exists.
- A raw lifted extra Gram remains lift dependent, and the source Einstein form
  remains a distinct relative comparison form.

## Verification

Tier 0 parsed all Python/JSON, checked the scoped diff, and compiled Paper 13
twice. Tier 1 replayed the producer, ran a method-distinct exact verifier, six
mutation tests, the atlas generator check, and strict atlas validation. Tier 2
was discharged by content-addressed imports plus independent reconstruction of
the tangent differential, charge cancellation, and Schur complement. Tier 3
was not run because this is a scoped two-jet bridge result, not a release or
all-orders freeze.

The result does not establish higher Kuranishi brackets, an all-orders
algebroid quotient, bounded or causal evolution, particle interpretation,
positivity, unitarity, or quantum transfer.

EVIDENCE: `bridge/certificates/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1.json`; `residual_atlas/einstein-weyl-mixed-charge-derived-correspondence-fragment-v1.json`; `bridge/einstein_sector/receipts/EINSTEIN_WEYL_MIXED_CHARGE_DERIVED_CORRESPONDENCE_V1_TIER_RECEIPT.json`
CLOSE-OUT: DONE — the two-jet mixed-charge derived correspondence, balanced witness, tangent cohomology, and complete map/form disposition are certified.
