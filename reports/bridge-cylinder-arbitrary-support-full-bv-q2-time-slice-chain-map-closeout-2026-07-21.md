# Cylinder arbitrary-support full-BV time-slice chain-map closeout

Date: 2026-07-21

Science Forge item:
`bridge-cylinder-arbitrary-support-full-bv-q2-time-slice-chain-map`

Disposition: `OBSTRUCTED`

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`,
`LORENTZIAN-CAUSAL`

## Result

The scoped chain map cannot exist with the selected finite residual receiver.
The obstruction occurs at unary order, before the quadratic Bach tensor or
the three anomaly representatives enter.

The imported causal theorem remains intact:

```text
386-row prolonged causal BV complex
    <---- finite-order local graph SDR ---->
30-row all-energy minimal metric BV endpoint.
```

The graph maps preserve compact and spacelike-compact support; the advanced
and retarded homotopies have the declared causal support.  This is not the
failed map.

The proposed next arrow instead targets the selected positive-frequency
matter window

```text
W_selected = W_2 + W_3 + W_4,
dim W_selected = 10 + 40 + 82 = 132,
```

together with the fifteen CE ghosts and fifteen BFV/Koszul momenta.  The
all-energy source cohomology contains the E branch at every integer
`n >= 2`.  At `n=5`, one chirality has dimension

```text
n^2 + 2n - 3 = 32,
```

so the two-chirality `E_5` block has dimension 64.  Residual `D` equivariance
forces a chain projection to send it into the target weight-five block, whose
dimension is zero.  Hence the induced projection is zero on `H_E,5`, whereas
an SDR must induce the identity there:

```text
rank([iota_cl pi_cl]|H_E,5) = 0,
rank(1|H_E,5)               = 64.
```

The minimum SDR defect rank is therefore 64.  No
`SO(4,2)`-equivariant unary SDR—and consequently no full arity-two
local-to-selected-time-slice chain map—exists on the declared arbitrary-
support domain.

## Complete local ansatz

The certificate records the complete six-role minimal BV ansatz from

```text
S_min = S_W[g]
      + integral gstar (L_c g + 2 omega g)
      + integral cstar [c,c]/2
      + integral omegastar L_c omega.
```

With `Q=(S_min,-)_BV` and

```text
Q(epsilon Phi) = epsilon q1(Phi)
               + epsilon^2 q2(Phi,Phi) + O(epsilon^3),
```

the declared `q2=(1/2)D^2Q` contains the Diff ghost, Weyl ghost, metric,
metric-antifield, Diff-ghost-antifield and Weyl-ghost-antifield rows.  It is a
finite-order local bidifferential operator; its metric equation row has order
at most four and obeys the intersection support rule on two compact inputs.

The portable component payload and executable arity-two square are not
promoted because the requested composite SDR already fails on unary
cohomology.  This is a mathematical nonexistence result for the scoped finite
receiver, not an expression-growth shortfall.

## Smallest repair

The receiver must be replaced by a completed all-energy time-slice carrier:

```text
E_n, n>=2;  A_n, n>=3;  L_n, n>=4;
both chiralities and conjugate Cauchy data;
the same 15 CE ghosts and 15 BFV/Koszul momenta.
```

For arbitrary smooth compact sources, the carrier must use a rapid-decay
Fréchet/Sobolev sequence completion (and a distributional dual), not merely
an algebraic direct sum.  Only after constructing its `q1`, `pi_cl`,
`iota_cl`, and `s_cl` maps should the programme serialize `q2`, prove
continuity under harmonic convolution, and evaluate the anomaly images.

## Fail-closed consequences

The images of `omega C^2`, `omega E4`, and `omega CdualC` remain
`NO_CERTIFIED_MAP`.  The raw-`D` Cartan defect likewise remains
`NO_CERTIFIED_MAP`.  No anomaly cohomology, QME, state, particle, positivity,
or unitarity claim follows.

## Evidence

- Certificate:
  `bridge/certificates/CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1.json`
- Independent verifier:
  `bridge/anomaly_restriction/verify_cylinder_arbitrary_support_full_bv_q2_time_slice_obstruction.py`
- Atlas fragment:
  `residual_atlas/cylinder-arbitrary-support-full-bv-q2-time-slice-obstruction-fragment-v1.json`
- Tier receipt:
  `bridge/anomaly_restriction/receipts/CYLINDER_ARBITRARY_SUPPORT_FULL_BV_Q2_TIME_SLICE_CHAIN_MAP_OBSTRUCTION_V1_TIER_RECEIPT.json`

## Verification

The producer/check, independent reconstruction, nine unit tests, Draft
2020-12 schema validation, fail-closed atlas validation, Python compilation,
and scoped whitespace audit pass.  The decisive mutation adds an `n=5`
target block; it removes this rank-64 witness while leaving the certificate's
all-energy repair flag false.  This shows that the obstruction is caused by
the finite receiver rather than being hard-coded as a generic failure.

Tier 3 was not run: this closeout obstructs a bridge and does not promote a
freeze, release, shared core algebra, quantum coefficient, or Lorentzian state
claim.
