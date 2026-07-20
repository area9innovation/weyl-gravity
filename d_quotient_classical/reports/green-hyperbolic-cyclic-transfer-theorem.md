# Sharp cyclic Green-homotopy transfer theorem

## Result

Let `(C,q_C)` contract differentially and cyclically onto `(E,q_E)` through
`(i,p,h)`, with all maps preserving the declared support and operator-domain
categories. If `E` carries advanced and retarded Green homotopies, then

```text
Lambda_C,+/- = h + i Lambda_E,+/- p
```

satisfies the full chain-homotopy identity and same-sided causal support.
The local term cancels in the causal difference:

```text
Delta_C = Lambda_C,+ - Lambda_C,-
        = i Delta_E p.
```

Consequently, on compact-to-spacelike-compact support complexes,

```text
[Delta_C] = [i_sc] [Delta_E] [p_c].
```

It is therefore a quasi-isomorphism whenever the endpoint causal map is.
With `i^sharp=p`, the transferred Green pairing is not merely abstractly
isomorphic but satisfies the exact representative identity

```text
<f,Delta_C g>_C = <p f,Delta_E p g>_E.
```

If the endpoint Green pairing agrees with a Cauchy-current pairing, that
identity descends with it. Pairing-derived degreewise sign involutions, rather
than one guessed scalar sign, give the advanced/retarded adjoint reversal.

## Sharpness

Seven exact rational counterexamples identify the load-bearing hypotheses:

- `CHAIN_MAPS_ARE_ESSENTIAL`: dropping `q_C i=i q_E and p q_C=q_E p` leaves `lifted chain homotopy` defective (rank `2`).
- `DEFORMATION_IDENTITY_IS_ESSENTIAL`: dropping `q_C h+h q_C=1-i p` leaves `lifted chain homotopy` defective (rank `2`).
- `RETRACTION_IS_ESSENTIAL_FOR_DESCENT`: dropping `p i=1_E` leaves `descended chain homotopy and derived quasi-isomorphism` defective (rank `2`).
- `SUPPORT_LOCALITY_IS_ESSENTIAL`: dropping `support-local U and U^-1` preserves the algebraic chain identity (rank-zero chain defect) but creates one explicit cross-point support entry.
- `PAIRING_ADJOINTNESS_IS_ESSENTIAL`: dropping `i^sharp=p` leaves `induced Green/current pairing identity` defective (rank `2`).
- `ENDPOINT_ADJOINT_REVERSAL_IS_ESSENTIAL`: dropping `Lambda_E,+^sharp=Sigma_E Lambda_E,- Sigma_E^-1` leaves `advanced/retarded adjoint reversal` defective (rank `2`).
- `SIGN_INTERTWINING_IS_ESSENTIAL_FOR_FIXED_SIGMA`: dropping `U Sigma=Sigma U` leaves `adjoint reversal with the untransported fixed Sigma` defective (rank `2`).

The side conditions `h^2=h i=p h=0` normalize a strong deformation retract
but are not used in the one-step lifted chain identity. Global hyperbolicity,
no timelike boundary, finite rank and filtration nilpotence are likewise
sufficient implementation conditions with the explicit replacements stated
in the certificate; they are not mislabelled as algebraically necessary.

## Independent consumers

The theorem consumes existing content-addressed artifacts without rerunning
their producers.

- On the unit vacuum conformal cylinder, the complete carrier has
  `386=356+30` rows. The cyclic SDR, advanced/retarded homotopies, causal
  quasi-isomorphism and equality of Green and Cauchy-current pairings are all
  imported and hash checked.
- On global unit Nariai, the curved repaired carrier has
  `310=15+140+140+15` rows and a 26-row metric endpoint. Its exact cyclic SDR,
  same-sided support, adjoint reversal and metric descent are imported and
  hash checked; the causal-difference and pairing factorizations are then the
  abstract theorem applied on that same background.

No carrier or mode is identified between these backgrounds.

## Scope

This theorem transfers a Green-hyperbolic-complex structure; it does not
construct the endpoint analytic input. It does not authorize nonlocal shears,
an isolated Bach-operator inverse, an open-background uniform theorem,
Hadamard wavefront control, a complex structure, positivity, particles,
renormalized products, QME restoration or any quantum claim.

## Reproduction

```bash
python3 -m d_quotient_classical.causal_transfer.green_hyperbolic_cyclic_transfer_theorem --check --guards
python3 -m d_quotient_classical.causal_transfer.verify_green_hyperbolic_cyclic_transfer_theorem
python3 -m unittest d_quotient_classical.causal_transfer.tests.test_green_hyperbolic_cyclic_transfer_theorem
```

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: d_quotient_classical/certificates/GREEN_HYPERBOLIC_CYCLIC_TRANSFER_THEOREM_V1.json
