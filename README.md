# Weyl Gravity: an AI-Orchestrated Research Programme

This repository is both a mathematical-physics programme and an experiment in
how scientific research might be conducted with AI.

The scientific subject is fourth-order gravity, especially pure Weyl gravity:
its extra solutions, gauge structure, causal propagation, nonlinear
obstructions, black-hole resonances, and possible quantum completion. The
methodological question is deliberately unusual:

> Can a person who is not a domain expert in physics, but who knows how to
> direct and critically use AI systems, orchestrate research that becomes
> precise, falsifiable, reproducible, and useful to experts?

The programme is orchestrated by **Asger Alstrup Palm**, a computer scientist
and Honorary Professor at DTU Compute. Palm is not a professional physicist.
AI systems have performed much of the mathematical proposal generation,
symbolic derivation, programming, verification design, literature mapping,
adversarial review, and manuscript drafting.

This is not presented as proof that AI can replace scientific expertise.
It is an open experiment whose outputs must earn credibility through explicit
claims, exact calculations, independent checks, reproducible artifacts, and
external expert criticism. The DTU affiliation describes Palm's academic role
and does not imply institutional endorsement.

## Release status

This is a **pre-release research archive**.

- The manuscripts have varying levels of maturity and have not all undergone
  independent peer review.
- Many results are computer-assisted. Their authority is the stated argument,
  certificate, verifier, and scope—not the identity of the human or AI author.
- The repository does not establish that pure Weyl gravity is a viable theory
  of nature, that its quantum theory is unitary, or that its extra modes are
  observable particles.
- The repository is licensed: manuscripts, certificates, data, and
  documentation under CC BY 4.0, and code under MIT. See [LICENSE](LICENSE).
  A license is permission to use and redistribute, not an endorsement of any
  claim the licensed file makes.
- The programme publishes here, as an open repository. There is no arXiv or
  journal submission, and no release tag or archival DOI. This follows from
  the authorship: the manuscripts name a model as principal author and
  Asger Alstrup Palm as non-technical orchestrator, which is what actually
  happened, and which the major venues do not accept. The attribution is
  not restated to fit them. Cite a commit hash to fix a version.

The most useful external contribution at this stage is a technically specific
critique: identify a claim, assumption, equation, certificate, or verifier and
show where it fails or what additional hypothesis it needs.

## The experiment in AI-assisted research

The project tests a workflow, not merely whether an AI can produce plausible
scientific prose.

1. **The human sets direction.** Palm chooses the broad questions, allocates
   effort, asks for competing approaches, and decides what enters the public
   programme.
2. **AI agents propose and derive.** Models formulate conjectures, develop
   proofs, write symbolic and numerical code, search the literature, and draft
   papers.
3. **Claims are narrowed.** Each result must say which theory, background,
   function space, boundary condition, parameter domain, and lifecycle stage
   it concerns.
4. **Calculations leave receipts.** Exact results use rational or algebraic
   arithmetic where possible. Validated numerical results retain interval
   enclosures, tail bounds, and machine-readable certificates.
5. **Checks are separated from production.** Re-running the same derivation is
   reproduction, not independent verification. Important claims seek a
   different representation, implementation, arithmetic backend, or
   derivation.
6. **Failures remain part of the record.** Negative results, failed mutations,
   blocked promotions, and superseded claims are retained instead of being
   rewritten as success.
7. **Papers expose their boundaries.** A reduced-mode calculation is not
   promoted silently to a Lorentzian causal theorem; a classical sign is not
   called a quantum probability.

This workflow is coordinated by [Science Forge](planning/README.md), an
append-only research ledger with fail-closed gates. Its five governing rules
are:

- missing or failed evidence never counts as a pass;
- history is repaired by new records, not rewritten;
- producer reruns are distinguished from independent verification;
- non-results and limitations are not promoted into claims;
- exact and numerical evidence remain distinct types.

Whether this process has produced genuinely new and correct physics is for
expert review to decide. The repository is designed to make that decision
easier than reviewing an unaudited AI-generated manuscript.

## The scientific question

Pure Weyl gravity is a four-dimensional, locally conformal theory with
fourth-order metric equations. Relative to Einstein gravity it contains
additional solutions, often associated with indefinite signs or “ghosts.”
The programme does not assume that a pole sign alone decides the physical
question. It separates four levels:

1. **Local solutions:** what the differential equations propagate.
2. **Reduced classical directions:** what survives gauge, constraints,
   charges, boundary conditions, and the symplectic radical.
3. **Nonlinear directions:** what can be continued consistently when
   interactions and global balance laws are included.
4. **Quantum states:** what survives anomaly cancellation, state
   construction, positivity, and the full gauge complex.

Different model backgrounds isolate different parts of this problem:
conformal and Berger cylinders, compact product spacetimes, Nariai,
Schwarzschild exteriors, and Euclidean backgrounds. A result on one
background is not silently transferred to another.

## Current scientific position

The programme has produced a large set of exact, computer-assisted, and
validated numerical results, but not a completed physical theory.

| Area | Current position | Primary entry |
| --- | --- | --- |
| Foundational fourth-order systems | Positive and Krein completions, vacuum representations, the degenerate Jordan limit, and selected interaction obstructions are classified in several declared settings. | [Papers 01–05](paper/) |
| Covariant pure-Weyl complex | Residual cohomology and its causal BV–BFV transport are constructed on the conformal cylinder, with explicit scope restrictions. | [Papers 07–08](paper/) |
| Clocks and compact backgrounds | Exact clock, phase-space, causal-transfer, and nonlinear obstruction calculations exist on selected compact laboratories. No single healthy final theory has been selected. | [Papers 09–13](paper/) |
| Schwarzschild black holes | The axial programme contains exact factorization and endpoint results, a validated defective \(\ell=2\) resonance, an endpoint-analytic nonzero complete massive-spin-two QNM velocity, and a fixed-domain global complex-scaled radial Fredholm double pole. Compactly cut-off matrix elements are the meromorphic continuation of an actual retarded mode-reduced transfer. Full metric/Bondi reconstruction, inverse-Laplace contour control, global waveform completeness, and the polar problem remain open. | [Papers 14, 16–18](paper/) |
| Quantum programme | Local algebraic, Euclidean-spectral, and reduced-mode results exist. A Lorentzian full-BV quantum theory, physical Hilbert space, scattering theory, and unitarity theorem do not. | [Paper 12](paper/12-pure-weyl-one-loop-bv-anomaly.pdf), [quantum ledger](quantum-weyl/README.md) |
| Phase-1 synthesis | The completed first phase is a classification with constructive results and obstructions—not a rescue of Weyl gravity and not a universal no-go theorem. | [Paper 15](paper/15-four-level-ghost-classification-phase1-synthesis.pdf) |

For the most detailed live claims table, assumptions, and non-claims, start
with the [physicist executive summary](paper/98-physicist-executive-summary.md).

## Start here

- **General introduction (Paper 99):** [Are Weyl Gravity's Ghosts Real?
  Building Model Universes to Find
  Out](paper/99-how-to-build-a-universe.md)
- **Programme introduction (Paper 00):** [Ghosts, Geometry, and
  Reality](paper/00-ghosts-geometry-reality.pdf)
- **Physicist introduction (Paper 98):** [Pure-Weyl gravity programme:
  executive summary for physicists](paper/98-physicist-executive-summary.md)
- **External reviewers:** [Review Paper 17 and its evidence
  chain](REVIEWING.md)
- **Stable Phase-1 synthesis:** [What Survives the Ghost
  Test?](paper/15-four-level-ghost-classification-phase1-synthesis.pdf)
- **Black-hole endpoint theorem:** [Future-Horizon Regularity and One-Sided
  Radiative Traces Do Not Select the Einstein Subsector](paper/16-lorentzian-endpoint-nonselection-pure-weyl.pdf)
- **Defective Schwarzschild resonance:** [An Axial \(\ell=2\) Non-Split
  Regge–Wheeler Self-Extension and a Defective Schwarzschild
  Resonance](paper/17-pure-weyl-schwarzschild-extension-structure.pdf)
- **Research dependency maps:** [public construction
  map](certificate_graph/universe-building-dag.svg) and [technical certificate
  graph](certificate_graph/certificate-dag.svg)
- **Forward programme:** [universe-building
  roadmap](notes/universe-building-roadmap.md)

## Manuscript series

All items should be treated as research manuscripts unless a separate release
record says otherwise. PDF artifacts are committed beside their LaTeX
sources.

| Paper | Subject |
| --- | --- |
| [00](paper/00-ghosts-geometry-reality.pdf) | Expository introduction to ghosts, geometry, real forms, interactions, cohomology, clocks, and black holes |
| [01](paper/01-symplectic-diagonalization.pdf) | Canonical positive symplectic diagonalization of the Pais–Uhlenbeck oscillator |
| [02](paper/02-variational-fock.pdf) | Minimum distortion and the fourth-order field representation problem |
| [03](paper/03-fourth-order-vacuum.pdf) | Vacuum covariance, Fock sectors, and the Krein/Jordan boundary |
| [04](paper/04-fourth-order-gravity.pdf) | Gauge reduction and free Einstein–Weyl completions |
| [05](paper/05-interaction-obstructions.pdf) | Interaction obstructions and resonant PT breaking |
| [06](paper/06-einstein-weyl-interaction-obstructions.pdf) | Cubic protection and second-order obstruction in Einstein–Weyl gravity |
| [07](paper/07-conformal-residual-cohomology-krein.pdf) | Residual cohomology and Krein completion on the conformal cylinder |
| [08](paper/08-conformal-covariant-causal-transport.pdf) | Covariant BV–BFV causal transport of the residual result |
| [09](paper/09-relational-clocks-berger-d-cartan.pdf) | A backreacting phase clock on a Berger cylinder |
| [10](paper/10-compact-einstein-maxwell-weyl-phase-space.pdf) | Einstein–Maxwell waves inside Weyl–Maxwell gravity |
| [11](paper/11-gravity-light-cyclic-causal-ell3.pdf) | Retained mixed gravity–Maxwell bracket under cyclic causal reduction |
| [12](paper/12-pure-weyl-one-loop-bv-anomaly.pdf) | A scoped one-loop Euclidean BV obstruction and compensator analysis |
| [13](paper/13-compact-weyl-maxwell-second-order-tangent-cone.pdf) | Finite-harmonic formal second-order tangent cone |
| [14](paper/14-pure-weyl-black-hole-radiation.pdf) | Fourth-order perturbations of pure-Weyl black holes |
| [15](paper/15-four-level-ghost-classification-phase1-synthesis.pdf) | Phase-1 four-level ghost classification |
| [16](paper/16-lorentzian-endpoint-nonselection-pure-weyl.pdf) | Lorentzian endpoint conditions and non-selection of the Einstein subsector |
| [17](paper/17-pure-weyl-schwarzschild-extension-structure.pdf) | Non-split Regge–Wheeler self-extension and defective Schwarzschild resonance |
| [18](paper/18-static-bach-flat-black-hole-thermodynamics.pdf) | Residual-basic charges and simultaneous horizon first laws on the Mannheim–Kazanas family |

Computational supplements accompany Papers 07–09, 12, and 16. The `paper/90`,
`91`, and `92` documents are technical bridge notes rather than numbered
headline papers.

## Evidence and claim boundaries

Every quantum result is assigned at least one dependency class:

```text
LOCAL-ALGEBRAIC
EUCLIDEAN-SPECTRAL
REDUCED-MODE
LORENTZIAN-CAUSAL
```

These labels are not interchangeable. In particular, this repository does
not currently contain:

- a complete Lorentzian off-shell BV propagator;
- a BRST-compatible Hadamard state for the full metric BV complex;
- renormalized Lorentzian time-ordered products;
- a causal perturbative AQFT construction;
- a Lorentzian quantum-master-equation theorem;
- a global proof that an isolated black-hole resonance term governs the full
  late-time retarded waveform.

The evidence chain for a strong computer-assisted claim is intended to be:

```text
mathematical statement
  → producer
  → machine-readable certificate
  → independent verifier
  → mutation test
  → paper claim with explicit non-claims
```

Not every historical result has reached every stage. The
[Science Forge shadow audit](ci/science-forge-shadow.sh) is advisory by
default and reports drift rather than silently certifying the entire corpus.

## Repository layout

| Path | Purpose |
| --- | --- |
| `paper/` | Manuscripts, supplements, public introductions, and PDFs |
| `symbolic/`, `numeric/`, `lean/` | Exact algebra, validated/numerical checks, and Lean formalization |
| `black_hole_programme/` | Schwarzschild operators, endpoint analysis, QNMs, thermodynamics, and certificates |
| `covariant_completion/`, `analytic_completion/` | Causal and functional-analytic completion work |
| `d_quotient_classical/`, `d_quotient_programme/` | Compact reduction, clocks, charges, and cross-programme imports |
| `closed_universe_observers/` | Relational observables and observer models |
| `bridge/`, `field_bv_identification/`, `nonlinear/` | Cross-background maps, BV identifications, and nonlinear tests |
| `quantum-weyl/` | Local BV, Euclidean, reduced-mode, Lorentzian, and transfer ledgers |
| `certificate_graph/`, `residual_atlas/` | Evidence dependencies and branch passports |
| `planning/`, `reports/`, `notes/` | Append-only work coordination, receipts, audits, and roadmap |

## Clone and reproduce

```bash
git clone https://github.com/area9innovation/weyl-gravity.git
cd weyl-gravity
git lfs pull
```

The repository is heterogeneous: individual certificate families declare
their own Python, SymPy, FLINT, interval, Forge, or Lean requirements. Prefer
the command printed by the relevant paper supplement or certificate rather
than assuming that one successful script verifies the whole programme.

Representative entry points are:

```bash
# Papers 07–08: required publication rail
python3 symbolic/verify_conformal_paper_free.py --required

# Paper 06: quick exact/symbolic rail
python3 symbolic/verify_gravity_paper6.py --quick

# Advisory corpus audit; findings are not a pass
bash ci/science-forge-shadow.sh

# Lean formalization
( cd lean && lake exe cache get && lake build )
```

The exhaustive suite is intentionally not a per-commit test. Changes to a
claim or certificate should run the smallest falsifying scoped test first,
then the affected certificate chain, and finally the full release suite only
for a freeze.

## Authorship and responsibility

The manuscript series uses an experimental authorship convention:

- **GPT-5.6.sol** is listed as principal programme author.
- **Asger Alstrup Palm** is the programme orchestrator, corresponding human
  contact, and editorially accountable human participant.
- **Claude Fable 5** is credited as a computational coauthor on Paper 00,
  where it contributed.

AI model names describe substantive production roles in this experiment.
They do not remove the need for accountable human release decisions, and
journals or archives may require a different formal authorship declaration.
The detailed contribution statement in each paper controls that paper.

Contact: **Asger Alstrup Palm** — `asger@area9.dk`

## What would count as success?

The project succeeds methodologically if expert reviewers can efficiently
separate correct new results from errors because the assumptions, derivations,
code, evidence, and failures are exposed. A decisive refutation with a
reproducible counterexample would be scientific progress too.

The stronger claim—that a non-expert AI orchestrator can repeatedly originate
reliable research of independent value—cannot be established by the
repository declaring itself successful. It requires external technical review,
reproduction, correction, and eventual use by domain experts.
