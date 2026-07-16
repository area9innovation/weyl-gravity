# Einstein--Maxwell obstruction bilinear on the compact fixture span

Date: 2026-07-16

## Result

`EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_G1` constructs the first reusable
restriction of

```text
O : H^0_lin x H^0_lin -> coker L_WM.
```

The declared domain is

```text
H_fixture=span_R{R,D,P,G},
```

where `R` is the constant radion, `D` the Maxwell-duality direction, `P` the
certified `l=1` photon mode, and `G` the plus branch of the certified `l=2`
gravitational mode. The codomain is only the constant-lapse component `C_H` of
the full adjoint cokernel.

With the normalized spatial `tt` pairing, polarization gives

```text
             R       D       P                        G
R           -2       0       0                        0
D            0    -1/2       0                        0
P            0       0   -16/3                        0
G            0       0       0   -12 sqrt(3)-72/5.
```

All distinct-`ell` entries vanish because the invariant projection of an
`SO(3)`-equivariant bilinear operator can contain a scalar only when
`ell_1=ell_2` with conjugate `m` values. The only symmetry-allowed mixed
fixture pair is `R,D`; a new full-tensor calculation gives

```text
Q(a_R R+a_D D)=-2 a_R^2-(1/2)a_D^2,
O(R,D)=0.
```

Thus the displayed matrix is computed, not inferred from the previously known
diagonal fixtures.

## Charge fibres

At fixed electric and magnetic charges, the constant-lapse class survives in
the cokernel and `Q(v)=0` is a necessary second-order extension condition.
Allowing only electric charge variation does not change that result at the
purely magnetic background.

If the second-order magnetic coefficient `p` is admitted, the augmented
linear pairing is

```text
<zeta_H,L(Phi2,p)>=-p.
```

Consequently `C_H` is removed from the augmented cokernel and choosing
`p=Q(v)` cancels this component. This reproduces the explicit radion and
duality charge-relaxed extensions. For the photon and gravitational modes it
removes only the certified constant-lapse obstruction; it is not yet a full
extension because other source rows and cokernel directions have not been
classified.

## Taub interpretation

`zeta_H` is the adjoint constraint zero-mode associated with the product
time-translation Killing field. Pairing the quadratic source with it is the
standard Taub/linearization-stability construction. Here it is restricted to
the Einstein--Maxwell tangent subspace inside Weyl--Maxwell and to a declared
global-charge fibre, so the precise classification is a **relative Taub
moment-map component**.

This does not assert that the same tangent is obstructed in Einstein--Maxwell
itself. A full covariant-symplectic identification of the moment map also
remains open.

## General harmonic selection rules

For a constant-lapse projection, equivariance gives necessary rules:

- `k_1+k_2=0` on `S1`;
- `ell_1=ell_2` and `m_1+m_2=0` on `S2`;
- product parity is even;
- surviving equal-quantum-number polarization blocks still require tensor
  calculation.

The certificate is therefore `G1_DECLARED_FIXTURE_SPAN`, not the full harmonic
theorem commissioned by the planning brief. The next promotion computes every
surviving polarization block and the complete adjoint cokernel.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compilation, schema/certificate JSON parsing, scoped `git diff --check` | < 0.1 s | PASS |
| 1 | exact certificate generation including the mixed full-tensor fixture | 5.21 s | PASS |
| 1 | byte-for-byte generator verification | 5.33 s | PASS |
| 1 | independent matrix, polarization, charge-fibre, and provenance verifier | 0.36 s | PASS |
| 1 | scoped unit suite | 5.23 s | PASS (8 tests) |

Tier 2 was not run because the three imported certificates are unchanged,
content-addressed inputs and this theorem adds a direct consumer without
changing their operators or schemas. Tier 3 criteria were not met: this is a
`G1` classification, not a freeze, lifecycle promotion, shared-core change,
or release.
