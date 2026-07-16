# Compact harmonic domain and relative Taub descent

Date: 2026-07-16

## Result

`COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT` closes the domain ambiguity that
preceded the full harmonic obstruction calculation.  It establishes a
`G1_DOMAIN_AND_DESCENT_FREEZE` result with dependency tags
`LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

The declared compact phase space is now precise:

```text
M = R_t x S1_L x S2,
Sigma = S1_L x S2,
P_N -> Sigma a fixed compact U(1) bundle with N=2,
H^0_lin = ker L_Einstein-Maxwell / (linearized Diff x U(1)),
```

with smooth periodic metric perturbations and connection differences.  A
difference of two connections on the same bundle is a global one-form `a`, so
its curvature perturbation is `f=da` and has zero `S2` flux at every
perturbative order.  This domain is before the final residual quotient.

The certificate defines the full smooth harmonic completion on this domain,
but it does not claim to have computed a master-variable basis or the complete
linear cohomology.

## Flux topology changes the earlier interpretation

For

```text
F(epsilon) = (P + epsilon^2 p) vol(S2),
integral vol(S2) = 4 pi/k_2,
```

exact integration gives

```text
N(epsilon) = q_min/(2 pi) integral F
           = 2 q_min (P + epsilon^2 p)/k_2.
```

At the rational fixture `q_min=k_2=P=1`,

```text
N(epsilon)=2+2 epsilon^2 p.
```

The transition winding of a fixed compact `U(1)` bundle is integer and locally
constant in a smooth family.  Therefore `p=0`.  This proves that the magnetic
row which removed the constant-lapse cokernel in the earlier augmented
calculation is not available inside the same fixed-bundle phase space.

There are now three distinct charge domains:

1. On fixed `P_N`, magnetic flux cannot vary and the certified obstruction
   survives.
2. In an enlarged theory of closed real two-forms with continuously variable
   harmonic flux, `p=Q(v)` can remove the constant-lapse component.  The exact
   radion and duality extensions belong here.
3. Electric charge may vary continuously on fixed `P_N`, but at the purely
   magnetic background its first variation does not hit the constant-lapse
   energy row because `(E^2+P^2)/2` has zero derivative in the electric
   direction at `E=0`.

Thus “charge-relaxed extension” must no longer be read as an extension through
connections on the same compact `U(1)` bundle.  It is an extension in an
enlarged continuous-flux family.

## Gauge descent

For the action-derived coupled gauge operator, gauge covariance gives

```text
DE_Phi[R_Phi(epsilon)] = C_epsilon E(Phi).
```

Differentiating at a solution in an on-shell tangent direction `v` gives

```text
D^2 E_bar[v,R_bar(epsilon)]
  = -L ((D R)_bar[v] epsilon).
```

Pairing with the adjoint constant-lapse class kills the right-hand side.
Consequently the imported quadratic form descends through linearized
`Diff x U(1)` on its Einstein--Maxwell domain and through the target gauge
directions in the Weyl--Maxwell complex.  Diffeomorphisms of the monopole
connection are treated with the bundle-covariant lift

```text
delta A = d(lambda+i_xi A)+i_xi F,
```

so this statement is patch-independent.

This is a formal action-Noether descent theorem.  It is not the missing curved
off-shell BV chain map.

## Cauchy-slice independence

The relevant reducibility parameter is time translation,
`K=partial_t`.  On the purely magnetic stationary background its compensated
Maxwell component is zero.  The polarized coupled Noether identity makes the
quadratic current divergence-free for two linearized solutions.  Since
`Sigma` is closed, Stokes' theorem gives

```text
integral_(Sigma_t1) J_K = integral_(Sigma_t2) J_K.
```

The constant-lapse obstruction is therefore a Cauchy-slice-independent Taub
charge.  In separated complex harmonics this adds the time selection rule
`omega_1+omega_2=0` to the spatial rules
`n_1+n_2=0`, `ell_1=ell_2`, and `m_1+m_2=0`.  A real normal mode contains both
frequency signs, so evaluation at `t=0` selects a representative of the same
conserved quadratic charge; it does not define a time-dependent obstruction.

## The promoted interpretation

On the fixed compact bundle, the previously certified fixture matrix

```text
diag(-2,-1/2,-16/3,-12*(6+5*sqrt(3))/5)
```

is now a gauge-descended, slice-independent **relative Taub bilinear** on the
declared subspace of `H^0_lin`.  Each of its four basis fixtures therefore
fails a necessary second-order Weyl--Maxwell extension condition in that
fixed-bundle phase space.

“Relative” is essential: this tests whether Einstein--Maxwell tangents extend
inside Weyl--Maxwell at the common background.  It is not a theorem that the
same tangent is non-integrable in Einstein--Maxwell itself, and it is not yet
an equality with a fully constructed covariant-symplectic moment map.

## Remaining gate

The next calculation is now well posed: compute every surviving
equal-`(abs(n),ell,polarization,branch)` block and classify the other
constraint-adjoint classes on the fixed `P_N` domain.  The complete
`H^0_lin`, full adjoint cokernel, off-shell BV chain map, causal propagation,
and scattering remain open.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | Python compilation, JSON parsing, scoped `git diff --check` | < 0.1 s | PASS |
| 1 | exact generator/byte comparison | 0.38 s | PASS |
| 1 | independent topology, phase-space split, selection, and scope verifier | 0.41 s | PASS |
| 1 | scoped unit suite | 0.38 s | PASS (8 tests) |

Tier 2 is unnecessary because all three imported inputs are unchanged and
content-addressed; this certificate is a new consumer which changes no shared
operator or schema.  Tier 3 criteria are not met because this is a `G1`
domain/descent theorem, not a freeze of the complete harmonic theorem, shared
core algebra, or a release.
