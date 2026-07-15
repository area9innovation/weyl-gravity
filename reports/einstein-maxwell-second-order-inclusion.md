# Einstein--Maxwell second-order inclusion test

Date: 2026-07-15

## Result

The `LOCAL-ALGEBRAIC`, `REDUCED-MODE` certificate
`EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST` finds that second-order
extension is both tangent-dependent and charge-sector-dependent.

It establishes three separate results:

1. The certified constant radion has no smooth periodic second-order
   correction on the compact `S1 x S2` quotient at fixed magnetic flux.
   This is proved by an adjoint-cokernel pairing, not merely by finding a
   nonzero source.
2. A Maxwell duality tangent has the same fixed-magnetic-flux obstruction,
   but extends exactly when magnetic flux may rotate with electric flux.
3. A null radiative tangent on the universal cover has nonzero
   `C_Ch^(2)`, yet an explicit metric correction cancels its complete
   quadratic Weyl--Maxwell source.

Thus a nonzero Chevreton coefficient is not itself a no-go, while the compact
fixed-charge sector already has explicit second-order obstructions.

## Convention

For

```text
Phi(epsilon)=Phibar+epsilon Phi1+epsilon^2 Phi2+O(epsilon^3),
```

the affine quadratic source is

```text
S2=(1/2) D^2 E[Phi1,Phi1],
```

and the extension equation is `L Phi2=-S2`. The Chevreton trace is evaluated
from

```text
H_ab = nabla_c F_ad nabla^c F_b^d
       -(1/4) g_ab nabla_c F_de nabla^c F^de,
```

with `C_Ch^(2)=2 H^(2)` in the certified `kappa=1` fixture conventions.

## Constant radion: fixed-flux obstruction

For

```text
h1=2 t^2 (-dt^2+dx^2)+2 dOmega_2^2,   f1=0,
```

the first Maxwell jet remains parallel, so

```text
C_Ch^(2)=0.
```

The complete affine quadratic Weyl--Maxwell source is

```text
S2 = diag(-2, 34, -18, -18 sin(theta)^2).
```

This nonzero source alone would not prove an obstruction. The decisive fact
is the averaged linearized `tt` row. Average any hypothetical correction over
the compact spatial symmetry group `S1 x SO(3)` and fix invariant
Diff x Weyl gauge. Writing the surviving metric variable as `D=A-R` and the
second-order magnetic-flux coefficient as `p`, one obtains

```text
(L Phi2)_tt = (1/2) partial_x^2 box(D) - p.
```

At fixed magnetic flux `p=0`. Pairing with the constant lapse and integrating
over the periodic `S1` kills the total derivative, whereas

```text
integral_S1 S2_tt dx = -2 L != 0.
```

This is the required adjoint-cokernel witness. It applies to arbitrary smooth
periodic corrections, not only to the invariant ansatz, because averaging
commutes with the linearized operator.

If magnetic flux may change, the obstruction is removable. The explicit
correction

```text
h2=(8/3)t^4(-dt^2+dx^2),
f2=-2 sin(theta) dtheta wedge dphi
```

sets every second-order Weyl--Maxwell residual component to zero.

## Maxwell duality tangent

For `h1=0` and `f1=*Fbar=dt wedge dx`, the parallel first Maxwell jet again
gives `C_Ch^(2)=0`. Holding magnetic flux fixed produces

```text
S2 = diag(-1/2, 1/2, -1/2, -(1/2)sin(theta)^2),
```

whose constant-lapse pairing is `-L/2`. Hence no periodic fixed-magnetic-flux
correction exists. If flux may rotate, however,

```text
F(epsilon)=cos(epsilon) Fbar+sin(epsilon)(*Fbar)
```

is an exact all-order solution because its Maxwell stress is unchanged. Its
second-order correction is `f2=-(1/2)Fbar`.

## Nonzero-Chevreton null radiative extension

On the universal cover, let

```text
u=t-x,  v=t+x,
phi1=u,
psi1=u^2 v/4,
f1=0.
```

These satisfy the complete reduced linearized Einstein--Maxwell equations
`box(phi1)=0`, `Hessian(phi1)=0`, and
`box(psi1)+2 phi1=0`. The metric variation makes the Maxwell jet
nonparallel, giving the pure-null coefficient

```text
C_Ch^(2)=4 (dt-dx) tensor (dt-dx) != 0.
```

Nevertheless it is removable. With

```text
D = u^3 v (5uv-24)/24,
h2=D(-dt^2+dx^2),
f2=0,
```

the exact tensor calculation gives `L Phi2+S2=0` componentwise. This fixture
is polynomial on `R^(1,1) x S2` and is not periodic on the compact `S1`
quotient; it is therefore a local/universal-cover extension theorem, not a
compact radiative-state theorem.

## Interpretation and boundary

The second-order failure is not universal. The compact obstructions found
here are fixed-charge integrability conditions for a constant radion and a
global duality direction. They do not remove the linear helicity-two or
photon classes. Conversely, the removable null fixture proves only that one
nonzero Chevreton source lies in the image of the Weyl linearization; it does
not establish general nonlinear Einstein-sector closure.

The next discriminating calculation is the fixed-electric-and-magnetic-charge
test for periodic nonzero-frequency graviton and photon harmonics.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on generator, verifier, and tests | < 0.1 s | PASS |
| 0 | JSON parsing and scoped `git diff --check` | < 0.1 s | PASS |
| 1 | exact tensor certificate generation | 34.09 s | PASS |
| 1 | independent reduced-equation and adjoint verifier | 0.50 s | PASS |
| 1 | scoped unit suite | 35.89 s | PASS (8 tests) |

Tier 2 was not run because the imported background and linear certificates
are unchanged content-addressed inputs. Tier 3 criteria were not met.

Concurrent quantum-team local-BV and Berger-transfer edits were preserved and
are not part of this result.
