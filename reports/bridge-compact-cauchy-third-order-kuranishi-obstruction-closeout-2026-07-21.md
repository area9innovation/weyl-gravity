# Compact-Cauchy third-order Kuranishi gate closeout

## Outcome

The formal cubic Kuranishi class and its correction-choice quotient are
certified, and the smallest complete resonance carrier of the balanced
Einstein-minus/extra fixture is enumerated exactly. The class cannot be
evaluated from the current action payload because its first required cubic
constraint tensor is absent.

With

```text
Phi = Phi_bar + epsilon*u + epsilon^2*v + epsilon^3*w + O(epsilon^4),
```

the exact equations are

```text
L v = -(1/2)D2E[u,u],
L w = -D2E[u,v] - (1/6)D3E[u,u,u],
K3(u;v) = P_O(D2C[u,v] + (1/6)D3C[u,u,u]).
```

For another correction `v+z`, `Lz=0`, the representative changes by
`l2(u,z)`. Hence the correction-independent candidate is
`[K3] in O/im(l2(u,-))`. On the declared balanced real two-amplitude slice,
`rank l2(u,-)=1`, so the formal obstruction quotient has dimension four.
Nonlinear gauge-representative independence remains unproved without the
second jet of the bundle-covariant algebroid action and the arity-three
Noether identity.

## Resonance closure

The second-order correction occupies polar `ell=0,2,4` channels at zero,
double, sum and difference frequencies. Multiplication by the first-order
axial `ell=2` fixture gives the complete axial third-order angular carrier
`ell=2,4,6` and sixteen signed frequency lattice points
`n_minus*omega_minus+n_extra*omega_extra` of odd word length at most three.

Exact algebraic shell comparison finds only the original `ell=2` resonances:

```text
(n_minus,n_extra) = (+/-1,0)  q_minus,
(n_minus,n_extra) = (0,+/-1)  p_extra.
```

No new shell type appears kinematically. Whether the original-shell cubic
coefficients vanish is not decidable from the imported data.

## First absent input

The content-addressed quadratic certificate supplies the complete chosen
second-order correction and the bilinear source on two first-order axial
inputs. It does not supply:

- the action-normalized `D3C_barPhi` tensor on the balanced first-order carrier;
- mixed `D2C_barPhi[u,v]` for every stored `ell=0,2,4` correction channel;
- their five stabilizer and resonant `ell=2` adjoint-shell projections;
- a same-convention field-component crosswalk for all stored reduced
  correction coefficients;
- the second action jet and arity-three Noether identity required for gauge
  independence.

The next export must contain those tensors with exact row ordering,
harmonic/frequency labels, action normalization, representative choice, source
action hash, and an independent verifier. A new competing nonlinear action or
the assertion that quadratic charge balance integrates to all orders is not an
admissible substitute.

## Verification

The producer and method-distinct verifier independently enumerate the sixteen
frequency points, prove the four and only four shell coincidences, reconstruct
the balanced `l2(u,-)` rank, and audit the imported payload for the absent
cubic/mixed tensors. Seven replay and mutation tests reject false D3 presence,
false balanced evaluation, hidden correction ambiguity, an omitted resonance,
false gauge independence, and false third-order sufficiency. The fail-closed
atlas row marks the nonlinear gate `OBSTRUCTED` and every causal,
observational, particle and quantum map outside scope.

EVIDENCE: `bridge/certificates/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1.json`; `residual_atlas/einstein-weyl-compact-cauchy-third-order-kuranishi-obstruction-fragment-v1.json`; `bridge/einstein_sector/receipts/EINSTEIN_WEYL_COMPACT_CAUCHY_THIRD_ORDER_KURANISHI_INPUT_OBSTRUCTION_V1_TIER_RECEIPT.json`
CLOSE-OUT: OBSTRUCTED — the cubic class formula and resonance closure are exact, but its value is undefined until the action-normalized D3C, mixed D2C[u,v], and arity-three gauge/Noether tensors are exported.
