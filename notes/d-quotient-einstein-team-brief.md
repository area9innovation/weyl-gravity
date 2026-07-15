# Einstein team brief: does the closed-cylinder quotient describe gravity with boundaries?

## Commission

Answer one question:

\[
\boxed{
\text{Is }D\text{ genuinely gauge after adding clocks, interactions, quantization, or boundaries?}
}
\]

Your task is **not** to export the closed-cylinder cohomology result to
scattering.  Construct the strongest asymptotic or causal counterexample to the
\(D\)-quotient, in a setting where time translation is expected to carry a
physical charge, and determine exactly which parts of the Weyl-gravity
construction survive.

The compact-cylinder Cartan contraction depends on a boundaryless phase space
and a strict residual action.  Neither property may be assumed at null or
timelike infinity.  The centered residual classes \([W_+^2]\) and
\([W_-^2]\) are deformation/vertex classes, not one-particle gravitons and not
surrogates for radiative scattering states.

Existing flat transverse-traceless reduced-mode and radial indicial results are
bootstrap inputs only.  They do not establish a full Lorentzian off-shell BV
propagator, support-compatible Green complex, null-infinity charge theorem, or
scattering equivalence.

## E-D1a status: generator identification completed

The exact seed certificate
`bridge/certificates/d_quotient_asymptotic_seed.json` corrects a necessary
ambiguity before the charge computation.  Three generators must be kept
separate:

```text
H_ESU = real Einstein-cylinder time translation d_T,
D_M   = real Lorentzian Minkowski dilation t d_t+r d_r,
D_rad = compact radial-quantization grading used in the residual module.
```

Under the real Penrose map, `H_ESU` becomes `(P_0+K_0)/2` in the stated
convention and crosses the null boundary of a fixed Minkowski patch.  It is
not a boundary-preserving generator there.  `D_M` is tangent to null infinity
and restricts to `u d_u`, but it is not `P_0=d_u`.  The compact identification
`D_rad=D_M` uses the radial-quantization Cayley/Wick continuation, not the
real Lorentzian Penrose push-forward.

Consequently “time-translation/`D` charge” must be split into distinct
charge questions.  Nonzero ADM/Bondi `P_0` charge does not compute the charge
of `D_M` or `H_ESU`.  The current asymptotically flat verdict is
`PHASE_SPACE_NOT_CLOSED`, not `D_GAUGE` or `D_CHARGED`; the Einstein verdict
is `EINSTEIN_OPEN`.  See `notes/conformal-d-quotient-asymptotic-seed.md` for
the exact dictionary, reduced shear/news action, and triangular `(h,chi)`
operator seed.

The subsequent flat TT Schwartz-core kill test adds a separate obstruction:
the pure-Weyl current restricts to zero on two Einstein wave tangents, while
the Einstein-Hilbert current has a nonzero Cauchy witness.  Local finite-jet
improvements cannot change this rank mismatch on the declared domain.  Thus
causal closure of `chi=0`, even if proved, is not sufficient for Einstein
scattering; a nondegenerate symplectic and charge comparison is independently
required.  The result is scoped and does not yet classify null-infinity
corners or compensator-generated Einstein-Hilbert terms.

## Work package E-D1: asymptotically flat Lorentzian BV--BFV complex

Construct the retarded/advanced linear BV complex with declared spaces and
falloffs at

\[
\mathscr I^-,\qquad i^0,\qquad \mathscr I^+.
\]

Include fields, ghosts, antifields, constraints, corner matching, soft/memory
data, Coulombic data, and the extra Cauchy data of the fourth-order Bach
operator.  Prove the mapping and support properties of the differential and
Green operators on the chosen weighted, Sobolev, or polyhomogeneous spaces.

Identify the actual asymptotic symmetry algebra from boundary preservation and
finite charge criteria.  Compute the renormalized charge variation, flux, and
algebra for the asymptotic transformation corresponding to cylinder \(D\):

\[
\delta H_D=\Omega_\Sigma(\delta\phi,\mathcal L_D\phi).
\]

Separate proper gauge parameters, whose normalized charges vanish, from BMS or
other asymptotic symmetries.  Include surface counterterms and corner terms.
Do not quotient time translation if it has ADM/Bondi charge or flux.

Then compute:

- radiative BRST/BV cohomology;
- helicity-\(\pm2\) one-particle and wave-packet classes;
- the causal symplectic/Green pairing and its signature;
- the Einstein radiative branch and the generalized fourth-order/Weyl branch;
- the conventional ghost mode and any zero-norm or logarithmic partners.

The strongest counterexample is admissible finite-flux data for which \(D\) is
charged and an unavoidable extra branch has negative physical norm or a new
scattering channel.  If boundary conditions remove it, prove that those
conditions are local, causal, symplectic, and preserved.

## Work package E-D2: causal closure of the Einstein sector

Fourth-order Bach evolution needs more Cauchy data than Einstein evolution.
Define the proposed Einstein submanifold by local initial/boundary constraints
and prove or refute

\[
\text{Einstein data on }\Sigma
\Longrightarrow
\text{Einstein solution for all time}.
\]

At linear order and then at the first nonlinear order:

1. list the complete Bach Cauchy data and the proposed Einstein constraints;
2. prove constraint propagation using the hyperbolic evolution, not only a
   modewise polynomial identity;
3. test retarded and advanced support and compatibility with gauge fixing;
4. test preservation at \(\mathscr I^\pm\), \(i^0\), and any timelike boundary;
5. identify whether extra normal derivatives are fixed locally, elliptically on
   a slice, nonlocally, or by future boundary data;
6. compute the first nonlinear source for the transverse extra branch.

The target theorem is:

> There exists a local, causal set of initial or boundary conditions selecting
> the Einstein branch, and this branch is preserved by evolution.

If the conditions require future data, nonlocal projection, or loss of a
well-posed symplectic phase space, issue a no-go result instead of weakening the
meaning of “causal.”

## Work package E-D3: observables, charges, and scattering

Compare the selected sector with Einstein gravity by constructing explicit
maps of phase spaces and observables.  Determine whether it reproduces:

- Einstein radiative phase space and helicity states;
- Bondi shear and news;
- ADM and Bondi energy-momentum;
- BMS and soft-graviton charges, memory, and flux laws;
- the Einstein covariant symplectic form;
- tree-level three- and four-point helicity amplitudes;
- factorization and unitarity on the selected external states.

For every extra Weyl mode classify it as excluded, pure gauge, non-radiative,
zero norm, negative norm, logarithmic/generalized, or an additional scattering
channel.  Supply the relevant cocycle, norm, charge, or amplitude; do not infer
its status from the closed-cylinder disappearance of one-particle residual
cohomology.

Compute whether the boundary time-translation charge agrees with ADM/Bondi
energy on the selected sector.  A nonzero agreement means \(D\) is a physical
symmetry there, even if its compact-cylinder counterpart was gauged.

## Work package E-D4: Lorentzian dS and AdS

Repeat the causal and symplectic analysis for:

1. Lorentzian dS with past/future conformal boundaries and a declared patch;
2. global Lorentzian AdS with reflecting, transparent, and any admissible mixed
   boundary conditions considered separately.

For each choice identify the generator corresponding to \(D\), calculate its
charge, and determine whether it is proper gauge, a physical Hamiltonian, or
sector-dependent.  Prove real-time preservation of the Einstein selection and
compatibility with the symplectic flux.  Euclidean AdS determinants or EAdS/dS
continuations are cross-checks only; they are not causal certificates.

Track boundary gravitons, normalizable versus non-normalizable modes, alternate
quantizations, zero modes, and possible logarithmic branches.  Do not select a
sector solely by imposing conditions at both temporal ends unless the resulting
problem has an explicit causal interpretation.

## Scalar-clock challenge

Add a conformally coupled scalar clock before Yang--Mills.  Determine whether
total \(D\) remains a constraint on compact slices while boundary time
translation remains charged, and construct relational observables

\[
\mathcal O_A(\tau)=\text{``the value of }A\text{ when }T=\tau\text{.''}
\]

Check clock monotonicity, gauge invariance, boundary falloffs, scalar flux, and
the total symplectic form.  This rail must distinguish “relational evolution
with a zero total constraint” from “evolution generated by a nonzero asymptotic
Hamiltonian.”

## Common background matrix

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | known target; boundaryless scope | known target | proved baseline | zero in stated absolute residual complex | \(I_2\) on centered degree-four classes | proper solution sector |
| Cylinder + scalar clock | open | open | open | open | open | open |
| Cylinder + Yang--Mills | open | open | open | open | open | open |
| Weakly deformed background | open | open | open | open | open | stability open |
| Lorentzian dS/AdS | boundary-dependent; compute | open | open | open | open | selected sector to certify |
| Asymptotically flat | `PHASE_SPACE_NOT_CLOSED`; `H_ESU` crosses fixed \(\mathscr I\), `D_M` charge open | `NOT APPLICABLE` until a boundary-preserving generator and phase space are chosen | formal triangular seed only; causal complex open | `OPEN` | `OPEN` | `EINSTEIN_OPEN`; reduced `chi=0` seed only |

## Priority and stop/go decisions

1. Complete the asymptotically flat linear causal complex and boundary phase
   space.
2. Choose a real boundary-preserving image, then compute its charge separately
   from the ADM/Bondi time-translation charge and radiative pairing.
3. Prove or refute linear causal preservation of the Einstein branch.
4. Classify the extra radiative branch and its norm.
5. Compare Bondi observables and tree amplitudes.
6. Add the scalar clock, then Lorentzian dS/AdS; add Yang--Mills only after the
   scalar rail is understood.

Escalate immediately if the Einstein selection is nonlocal or future-dependent,
if a negative-norm radiative mode is unavoidable, or if the selected sector
fails to reproduce the Einstein symplectic/charge structure.  These are
successful counterexample results.

## Required handoff

Deliver one human-readable report and machine-readable certificates containing:

- exact field/ghost spaces, falloffs, boundary and corner conditions;
- operator domains, support properties, and retarded/advanced Green checks;
- covariant phase-space charge, flux, integrability, and charge-algebra data;
- radiative cohomology representatives and exact/symbolic pairing matrices;
- local causal Einstein-sector constraints and propagation witnesses or no-go
  certificates;
- observable, Bondi, soft, and amplitude comparison maps;
- the strongest attempted counterexample in every setting;
- hashes, provenance, exact commands, elapsed times, and test tiers;
- explicit assumptions, open fields, and fail-closed flags;
- one verdict per setting: `D_GAUGE`, `D_CHARGED`, `SECTOR_DEPENDENT`, or
  `PHASE_SPACE_NOT_CLOSED`, plus `EINSTEIN_CAUSAL`,
  `EINSTEIN_NONCAUSAL`, or `EINSTEIN_OPEN`.

Every material result must carry at least one exact dependency tag:
`LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`, or
`LORENTZIAN-CAUSAL`.  Only an explicit `LORENTZIAN-CAUSAL` certificate may
support causal propagation or scattering claims.

## Cross-team contribution contract

Submit new results through the generator and phase-space registries in
[`d_quotient_programme/`](../d_quotient_programme/README.md).  In particular,
keep `H_ESU`, `D_M`, `D_rad`, and `P_0` in distinct ledger rows unless an
explicit phase-space-preserving intertwiner has been certified.
