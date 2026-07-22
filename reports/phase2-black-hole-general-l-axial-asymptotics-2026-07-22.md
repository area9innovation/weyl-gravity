# Phase 2: generic-ell axial Schwarzschild asymptotic recurrences

Work item: `sf:program/work/phase2-black-hole-general-l-axial-asymptotics`
Result token: `BH_PHASE2_GENERAL_L_AXIAL_ASYMPTOTIC_RECURRENCES_EXACT`
Dependency tags: `LOCAL-ALGEBRAIC` + `REDUCED-MODE`
Lifecycle: `CLASSIFIED`

## Disposition

The generic-angular-momentum axial asymptotic operator gate closes exactly.
On Schwarzschild mass `M>0`, in ingoing Eddington--Finkelstein coordinates,
with `Lambda=ell(ell+1)`, `ell>=2`, and real `omega!=0`, both the tracefree
Ricci-carrier system and the homogeneous metric system have all-orders formal
large-radius recurrences over `Q(Lambda,omega,M,i)`. Their post-indicial pivots
contain no `Lambda`-dependent denominator. The only exceptions are the imported
degenerate angular representations `ell=0,1` and the colliding-rate frequency
`omega=0`.

This is the operator/recurrence prerequisite for the separately gated literal
Lee--Wald-current calculation. No current or finite-pairing statement is made.

## Exact carrier system

For state `Z=(Pc,Pc',Qc,Qc')`, the exact system `Z'=M_psi Z` is

```text
[ 0, 1, 0, 0 ]
[ (Lambda*r-4*M)/(r^2*(r-2*M)), -2*i*omega*r/(r-2*M),
  -2*i*M*omega/(r*(r-2*M)), 0 ]
[ 0, 0, 0, 1 ]
[ 0, -2/(r-2*M),
  (Lambda*r-4*M-2*i*omega*r^2)/(r^2*(r-2*M)),
  (-2*i*omega*r-2)/(r-2*M) ]
```

Its leading characteristic polynomial is

```text
z^2 (z+2 i omega)^2.
```

The exact formal sectors are

| rate | carrier powers |
|---|---|
| `0` | `0`, `-1` |
| `-2*i*omega` | `-4*i*M*omega`, `-4*i*M*omega-1` |

For the top power in either sector, the recurrence determinant is

```text
-4 n (n-1) omega^2.
```

The `n=1` zero is a genuine integer-spaced resonance, but it is compatible:

- rate `0`: RHS `(Lambda,0)` admits particular coefficient
  `(i*Lambda/(2*omega),0)`;
- rate `-2*i*omega`: RHS
  `(-(Lambda-16*M^2*omega^2)/2, Lambda-16*M^2*omega^2)` admits particular
  coefficient `(i*(Lambda-16*M^2*omega^2)/(4*omega),0)`.

The free resonance coefficient is exactly the independent lower-power
solution. Setting it to zero fixes the top-power representative. No logarithm
is forced. For all integers `n>=2` the top pivot is nonzero. The lower-power
pivot is `-4*n*(n+1)*omega^2`, nonzero for every integer `n>=1`.

## Exact homogeneous metric system

For state `Y=(H0,H1,H1')`, eliminating the `H0` quadrature gives the shared
generic-`Lambda` master equation for `F=H1'`:

```text
(r^2-2*M*r) F''
 + (2*i*omega*r^2+2*r+2*M) F'
 + (6*i*omega*r-Lambda) F = 0.
```

The two formal solutions have

```text
rate 0:            F ~ r^-3 sum(c_k r^-k+3)
rate -2*i*omega:   F ~ exp(-2*i*omega*r) r^(1-4*i*M*omega)
                        sum(d_n r^-n).
```

Their exact recurrence pivots are

```text
-2*i*omega*(k-3),   k>=4,
 2*i*n*omega,       n>=1.
```

Both are nonzero throughout the declared domain. `Lambda` and `M` occur only
in recurrence numerators. The generalized homogeneous mode is also exact:

```text
H1 = constant,
H0 = -i*omega*r + Lambda/2 - 1 + 2*M/r,
```

a degree-one, log-free, unramified mode.

## Exact exceptional set

- `omega=0`: the two exponential rates collide and every displayed
  frequency pivot degenerates. It remains separately classified by
  `BH2_OMEGA_ZERO` and is excluded here.
- `ell=0,1`: the exact generic-harmonic input theorem isolates these as
  degenerate axial representations before this reduction.
- No additional real-frequency or angular exceptional locus exists for
  integer `ell>=2`, because no recurrence pivot contains `Lambda` or `M`.

## Controls and independent rail

- At `Lambda=6`, `M=1`, the metric master, exponents, recurrence, and
  polynomial mode reproduce `BH2C_METRIC_ALL_ORDERS` exactly.
- The carrier powers at `Lambda=6`, `M=1` reproduce
  `BH2C_ASYMPTOTIC_JORDAN`.
- The independent verifier uses the explicit polynomial
  `P3=(5*x^3-3*x)/2`, never symbolic `Lambda`, and the independent VbGeo
  Schouten/Kulkarni--Nomizu curvature engine. It reconstructs the complete
  `ell=3` metric and carrier matrices, then independently recovers the rates
  and powers.
- Mutations replacing `n(n-1)` by `n(n+1)`, inserting a spurious
  `(Lambda-6)` pivot pole, or omitting `omega=0` are rejected.

## Deliverables

- producer and deterministic certificate;
- strict schema;
- explicit-`P3` independent verifier;
- eight-test fast structural/mutation/prospective-tree provenance rail;
- residual-atlas fragment;
- tier receipt.

All deliverables except this report are under
`black_hole_programme/phase2/general_l_axial_asymptotics/`.

## Verification and tier disposition

- Tier 0: Python compile, JSON parse, scoped `git diff --check`, and exact
  changed-path inspection pass.
- Tier 1: deterministic producer replay, independent explicit-`P3` VbGeo
  verifier, eight tests, and residual-atlas validation pass.
- Tier 2: not run because no imported mathematical input, shared engine,
  schema consumer, or existing certificate changed; every prerequisite is
  imported read-only by exact hash.
- Tier 3: not run because this is a scoped `CLASSIFIED` recurrence theorem,
  not a paper freeze, release, or shared-core change.

## Claim boundary and successor handoff

This result does **not** compute the sphere-integrated Lee--Wald `F^v`, prove
finite radial pairing, classify the additional metric lift, treat polar
parity, construct an asymptotic phase space or Hilbert norm, or establish
scattering, QNMs, stability, particles, positivity, or a quantum result.
Those remain separate successors exactly as required by the work item.

CLOSE-OUT: DONE — generic-ell axial Ricci-carrier and homogeneous metric asymptotic systems, all-orders recurrence pivots, compatible resonances and the exact exceptional set are certified, with ell=2 control and an independent explicit-ell=3 recomputation.
EVIDENCE: black_hole_programme/phase2/general_l_axial_asymptotics/receipt.json
