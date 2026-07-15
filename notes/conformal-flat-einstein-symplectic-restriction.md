# Flat Einstein symplectic-restriction theorem

## Verdict

On the flat transverse-traceless Schwartz Cauchy core,

```text
REDUCED_FLAT_EINSTEIN_SYMPLECTIC_EMBEDDING_REFUTED.
```

The machine certificate is
`bridge/certificates/flat_einstein_symplectic_restriction.json`.  Its tags
are `REDUCED-MODE` and `LORENTZIAN-CAUSAL`; the latter applies only to the
declared real-time Minkowski Cauchy domain.  This is a symplectic no-go, not
a solution no-go: Einstein waves remain exact Bach solutions.

## Pointwise current calculation

For either flat TT helicity, the quadratic pure-Weyl density is, up to a
nonzero overall constant and a divergence,

```text
L_W=(1/2)(Box h)^2,   chi=Box h.
```

Direct variation gives

```text
theta_W^mu(delta h)
  =chi partial^mu(delta h)-partial^mu(chi) delta h,

omega_W^mu(h1,h2)
  =chi1 partial^mu h2-partial^mu chi1 h2
   -chi2 partial^mu h1+partial^mu chi2 h1.
```

Both tangents to the Einstein wave subspace obey `chi_i=0`, so

```text
omega_W^mu(E1,E2)=0
```

pointwise.  The Einstein-Hilbert TT current is instead, up to a nonzero
normalization,

```text
omega_EH^mu(E1,E2)=h1 partial^mu h2-h2 partial^mu h1.
```

Choose a smooth TT Schwartz tensor `q_ij` and wave Cauchy data

```text
E_q: (h,d_t h)=(q,0),
E_p: (h,d_t h)=(0,q).
```

Then

```text
Omega_W(E_q,E_p)=0,
Omega_EH(E_q,E_p)=int_R3 q_ij q^ij>0.
```

In Cauchy coordinates `(q,p)`, the respective matrices have ranks zero and
two.  No nonzero rescaling can identify them.

## Exact wave-packet domain

Choose `q_hat` smooth and compactly supported in a contractible momentum
cone whose closure avoids `k=0`.  A smooth helicity tensor exists on that
cone.  Multiplication and inverse Fourier transformation give a Schwartz,
trace-free, transverse Cauchy tensor.  The displayed data generate global
real-time solutions of `Box h=0`.

This domain is smaller than a completed Bondi phase space, but it already
refutes a nondegenerate Einstein-Hilbert symplectic embedding: an embedding
must work on this ordinary wave-packet core.

## Why local improvements cannot repair it

For `theta -> theta+dY+delta B`, the `delta B` contribution drops from the
antisymmetrized current and `Y` changes it by a spatial divergence.  Every
local finite-jet polynomial in Schwartz fields is Schwartz, hence

```text
lim_(R->infinity) int_(S_R) delta Y=0.
```

The restricted Cauchy pairing remains zero.  This does not classify nonlocal
boundary functionals, finite null-infinity corner degrees of freedom,
soft/distributional endpoint data, or a different dynamical conformal frame.

## Time translation

Flat time translation preserves `ker(Box)`.  On the restricted Einstein core,

```text
delta H_P0=Omega_W(delta h,L_P0 h)=0.
```

With `H_P0[0]=0`, the restricted pure-Weyl charge is zero throughout the
connected core.  Positive-energy Einstein-Hilbert wave packets have nonzero
Hamiltonian.  The full Weyl phase space remains nondegenerate only by pairing
Einstein roots with generalized fourth-order partners.

## Cylinder compatibility

The cylinder calculation uses global `S^3` modes, compact `D` energy, and the
radial/cylinder adjoint.  Those modes do not map into the flat Schwartz
domain on one Minkowski patch.  The certified compact `E/A/L` pairing is
therefore unchanged.  Compact radial evolution and real flat `P_0` evolution
are different phase-space problems.

## Interpretation

The relation is now separated into three levels:

```text
Einstein solutions inside Bach solutions:        exact,
causal closure of chi=0:                          partially established,
flat Einstein-Hilbert symplectic subtheory in CG: refuted on the TT Schwartz core.
```

Even a future causal-closure proof would not by itself recover Einstein
gravity.  A compensator, matter condensate, or symmetry-breaking phase that
generates an `M_P^2 R` term could change the current and restore a nonzero
Einstein pairing.  That would be a new phase or effective sector, not pure
Weyl gravity obtained only through boundary selection.

Maldacena's equivalence concerns asymptotically dS and Euclidean AdS
semiclassical data, not this flat Cauchy theorem
([arXiv:1105.5632](https://arxiv.org/abs/1105.5632)).  Action-level
Einstein/conformal comparisons with Neumann data are likewise boundary- and
curvature-dependent ([arXiv:1608.07826](https://arxiv.org/abs/1608.07826)).

## Next gate

The programme now forks cleanly:

1. complete the full tensor/null-infinity calculation and test whether a
   justified corner extension changes the flat result; or
2. The compensator test is now complete at local/background and flat TT
   quadratic order: `notes/conformal-compensator-einstein-phase.md` proves
   that `c1=zeta v^2` repairs the Einstein-root pairing but leaves an
   opposite-residue massive spin-2 branch.  The next test is causal removal
   of that branch, not another scale-generation calculation.

The first route tests pure Weyl gravity.  The second tests a broken or
matter-completed conformal theory.

## Verification

```bash
python3 -m bridge.einstein_sector.flat_einstein_symplectic_restriction --verify bridge/certificates/flat_einstein_symplectic_restriction.json
python3 -m unittest bridge.einstein_sector.tests.test_flat_einstein_symplectic_restriction
```
