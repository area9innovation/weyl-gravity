# External review of Paper 17

This repository invites technically specific attempts to reproduce, narrow,
or falsify its strongest current black-hole result:

> In the axial \(\ell=2\) sector of pure Weyl gravity on Schwarzschild, the
> repeated Regge–Wheeler factor is a non-split self-extension. At one
> certified simple Schwarzschild quasinormal frequency, its connection has
> Smith type \((0,0,2)\), and the meromorphic continuation of the
> mode-reduced retarded compact-source/compact-observation transfer has a
> nonzero rank-one second-order pole.

The manuscript is
[Paper 17](paper/17-pure-weyl-schwarzschild-extension-structure.pdf). A
shorter technical map is in the
[Paper 17 review brief](docs/external-review/paper17-review-brief.md).

## Why this review is unusual

The project is also an experiment in AI-orchestrated research. Asger Alstrup
Palm is a computer scientist, not a professional physicist. AI systems
performed much of the proposal generation, derivation, programming,
adversarial review, and drafting. The purpose of opening the work is not to
ask experts to trust AI output. It is to ask whether a non-expert using AI
can produce research artifacts precise enough for experts to falsify and,
if they survive, useful enough to build on.

We are seeking criticism, not endorsement. A demonstrated error is a
successful outcome of the experiment.

## What is and is not claimed

The result combines `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, and a scoped
`LORENTZIAN-CAUSAL` statement. It does not establish:

- a full off-shell metric or BV retarded propagator;
- an inverse-Laplace contour deformation or complete late-time QNM
  expansion;
- standard asymptotic falloff for the constant generalized mode;
- excitation by a specified real astrophysical source or detector
  sensitivity;
- the polar-sector analogue or all-multipole Bach nonsplitting;
- quantum positivity, unitarity, or physical viability of pure Weyl gravity.

## Useful ways to participate

### A short check

Spend about 15 minutes on one displayed identity, assumption, certificate
field, or claim boundary. Open an issue if it is wrong, ambiguous, or
stronger than its evidence.

### A focused audit

Spend two to four hours on one review track:

1. **Massive-system crosswalk:** Does the complete coupled axial
   Einstein–Weyl first jet really reduce to the stated Bach tangent, including
   the factor of three and endpoint-normalized Jost classes?
2. **Exceptional-resonance classification:** Do the analytic-germ Smith
   argument, nonzero selector, and spin-one local unit establish
   \((0,0,2)\)?
3. **Causal resonance bridge:** Does the retarded parent response continue
   to the certified radial double pole with exactly the stated limitations?
4. **Validated computation:** Are the interval enclosures, contour winding,
   tail bounds, branch choices, and mutation tests independently adequate?
5. **Reconstruction and observability:** Which radial conclusions survive
   metric/Bondi reconstruction, and what remains outside the standard
   asymptotically flat phase space?

### A bounded student reproduction

A student or postdoc could independently reconstruct one link without
auditing the entire programme. Good projects include:

- derive the complete massive axial first jet from the standard coupled
  variables;
- reproduce the selector with a different ODE representation or interval
  backend;
- verify the analytic Smith reduction from the certified connection cell;
- rebuild the exterior-complex-scaled Fredholm reduction;
- derive the outgoing trace and Bondi reconstruction independently.

## Reproduce the consolidated checks

From the repository root:

```bash
bash ci/review-paper17.sh
```

This replays the scoped certificate verifiers and adversarial Paper 17 claim
map tests. It is reproduction of the committed evidence, not an independent
derivation.

## How to report a finding

Use the issue forms for a
[reproduction report](https://github.com/area9innovation/weyl-gravity/issues/new?template=reproduction.yml),
[mathematical objection](https://github.com/area9innovation/weyl-gravity/issues/new?template=mathematical-objection.yml),
or
[claim-boundary question](https://github.com/area9innovation/weyl-gravity/issues/new?template=claim-boundary.yml).
Please identify the commit, theorem or claim identifier, and the first point
where your calculation diverges.

Private initial feedback is also welcome. It will not be quoted or attributed
publicly without permission. Actionable findings should ultimately acquire a
public issue or a project-authored public summary so that the scientific
record is auditable.

Issues are resolved with an explicit disposition such as `CONFIRMED_ERROR`,
`CLAIM_NARROWED`, `CERTIFICATE_REPAIRED`, `PAPER_REVISED`,
`NEEDS_HYPOTHESIS`, or `NOT_REPRODUCED`. A serious challenge to a
load-bearing claim pauses promotion of that claim until the challenge is
resolved.

Acknowledgement does not imply endorsement. Substantial theorem-level,
derivational, or verification contributions will be discussed transparently
with the contributor before any authorship or contributor credit is assigned.
