# Axial extra detector and quadratic Taub theorem

## Result

Three exact `LOCAL-ALGEBRAIC` / `REDUCED-MODE` rails are now separated.

First, `EINSTEIN_MAXWELL_WEYL_AXIAL_REDUCED_ACTION_HESSIAN` reconstructs the
reduced quadratic Fourier action

```text
S2_red=(1/2) integral Phi(-omega,-k)^T K(omega,k) Phi(omega,k)
```

from the certified formally self-adjoint target operator. Its mixed Hessian
is exactly `K`, the same operator generates the certified local Green current,
and that current equals the directly varied integrated four-dimensional
Lee--Wald current. This closes the reduced normalization triangle. It is not
a literal second expansion of the four-dimensional action density; that
stronger independent audit remains open.

Second, `EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR` turns the nondegenerate
extra Lee--Wald block into an exact coefficient observable. If `e_a` are the
two certified extra representatives and

```text
G_X,ab=Omega_WM(conjugate(e_a),e_b)/(-I*omega*N_(ell,m)),
```

then

```text
O_X^a(Phi)=(G_X^(-1))^ab
             Omega_WM(conjugate(e_b),Phi)/(-I*omega*N_(ell,m)).
```

Exact shell reduction proves

```text
O_X^a(e_b)=delta^a_b,
O_X^a(iota Phi_E)=0.
```

Thus `O_X` distinguishes both extra coordinates from the entire certified
generic axial Einstein image. It is a conserved observable on the declared
linear reduced-mode block before the final `SO(4,2)` quotient. Relational,
causal, asymptotic, and quantum descent remain open.

Third, `EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_ELL2_TAUB` gives the first nonlinear
self-extension verdict for the extra block. At

```text
lambda=6, k=0, omega^2=16/3,
e_1=(-6,0,6,0),
e_2=(0,-2/3,0,6),
Phi1=(a_1 e_1+a_2 e_2) cos(4t/sqrt(3)),
```

the real mode is the Hermitian mode-plus-conjugate polarization. Hence the
quadratic source contains the zero-frequency, zero-momentum singlet visible to
the compact constant-lapse adjoint class. Direct fourth-order tensor
expansion gives, at `t=0`,

```text
< [epsilon^2](3 B_tt-T_tt) >_(S2)
  =-64*(243*a_1^2+13*a_2^2)/45.
```

The exact Taub matrix is therefore

```text
T_X=diag(-1728/5,-832/45).
```

Its first principal minor is negative and its determinant is
`159744/25>0`, so `T_X` is negative definite. The off-diagonal entry
vanishes exactly, not numerically.

On the fixed principal bundle, the second variation of the Chern number forces
the second-order magnetic coefficient `p` to vanish. The imported
constant-lapse adjoint identity gives

```text
<L_WM Phi2>_tt=-p=0
```

after compact spatial total derivatives are integrated. Every nonzero real
combination `(a_1,a_2)` therefore has a nonzero adjoint-cokernel pairing and
admits no smooth periodic second-order correction at fixed electric and
magnetic charges.

## Interpretation

The two extra directions are genuine, nonradical solutions of the linearized
Weyl--Maxwell equations, and the detector measures them exactly. Nevertheless,
at the declared compact `ell=2,k=0` fixed-charge point, neither direction nor
any nonzero real combination is tangent to a smooth one-parameter family of
exact solutions through second order. They are linearization-unstable there.

This does not erase the generic linear extra module and does not prove that
all extra Weyl solutions are absent. The obstruction may depend on harmonic,
momentum, charge fibre, boundary conditions, or background. In particular,
the result does not classify nonzero `k`, `ell>2`, varying magnetic topology,
Lorentzian asymptotic data, or the final residual quotient.

The `EE`, `EX`, and `XX` labels must also retain output parity. The present
`XX` axial-by-axial source is even and is detected by the scalar constant-lapse
class. An axial extra-mode source detector at quadratic order requires an
axial output channel, for example an axial--polar input pair. The linear
symplectic detector must not be contracted blindly with a source of the wrong
parity.

## Claim boundary

The theorem is scoped to the two-dimensional real `ell=2,k=0` axial extra
span on the compact fixed-`P_N` product, before final residual quotient. It is
not a generic-`ell`, generic-momentum, causal, scattering, particle, ghost, or
quantum theorem. The direct four-dimensional action-density Hessian expansion
also remains a separate normalization audit.

## Verification

Fast deterministic rails:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_reduced_action_hessian \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_reduced_action_hessian.json
PASS; elapsed 0.48 s

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_detector \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_detector.json
PASS; elapsed 1.22 s

python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_ell2_taub \
  --verify bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json
PASS; elapsed 0.29 s

python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_reduced_action_hessian \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_detector \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_ell2_taub
PASS; 10 tests; elapsed 1.85 s
```

Exhaustive tensor rail:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_ell2_taub \
  --verify-exhaustive bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json
PASS; elapsed 137.31 s
```

Tier 0 Python compilation, JSON parsing, and scoped `git diff --check` passed.
The exhaustive tensor replay is the affected Tier 2 chain for the new
quadratic source. Tier 3 was not run because no shared core algebra, freeze,
lifecycle promotion, release, or causal/quantum theorem changed.
