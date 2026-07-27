# Paper 17 external-review brief

## The experiment

This programme asks whether a non-domain-expert who is skilled at directing
AI systems can orchestrate research that becomes precise, falsifiable,
reproducible, and useful to specialists. The human orchestrator is Asger
Alstrup Palm, a computer scientist and Honorary Professor at DTU Compute.
AI systems performed much of the mathematical proposal generation, symbolic
work, code, verification design, literature mapping, adversarial review, and
drafting.

The experiment succeeds neither because a manuscript exists nor because a
computer check passes. Its meaningful test is whether independent experts can
trace a claim to its assumptions and evidence, find errors efficiently, and
decide whether any surviving result is scientifically useful.

## The result under review

[Paper 17](../../paper/17-pure-weyl-schwarzschild-extension-structure.pdf)
studies axial \(\ell=2\) Schwarzschild perturbations in four-dimensional pure
Weyl gravity, using the \(e^{+i\omega t}\) convention and \(M=1\).

Its central chain is:

```text
exact axial field reduction
  -> repeated spin-two Regge-Wheeler self-extension
  -> exact nonsplitting and projective cocycle
  -> certified simple scalar QNM plus nonzero extension selector
  -> analytic-germ Smith type (0,0,2)
  -> length-two generalized resonant state
  -> nonzero rank-one second-order radial Green pole
  -> meromorphic continuation of a scoped retarded mode-reduced transfer
```

The certified frequency disk contains the negative-real-frequency
representative of the fundamental Schwarzschild \(\ell=2\) mode, near
\[
\omega_n=-0.3736716844+0.0889623157\,i.
\]

The generalized member is not a second independent Einstein mode. It has a
nonzero projection to the Ricci-carrier quotient. The complete coupled
massive axial first jet identifies it with the tangent of the massive
spin-two QNM branch, modulo the ordinary Einstein mode. In the current
normalization,
\[
\omega_n'(0)=\frac{2i}{3\omega_n}\,\kappa_n\ne0,
\]
where \(m=\mu^2\) is the signed squared-mass parameter and \(\kappa_n\) is
the certified projective selector.

## Five load-bearing questions

### 1. Massive axial crosswalk

Does the full coupled axial massive system—not merely its graded scalar
quotient—have the claimed first-jet factorization and endpoint-normalized
identity
\[
b_{\rm B}(\omega_n)
=\frac{3i\omega_n}{2}\,
  \partial_m a_{\rm phys}(\omega_n,0)?
\]

Primary evidence:

- [`axial_complete_massive_jet_crosswalk_v1`](../../black_hole_programme/phase4/axial_complete_massive_jet_crosswalk_v1/)
- [`axial_massive_jost_crosswalk_v1`](../../black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/)

### 2. Defective resonance

Do the simple scalar divisor, nonzero selector, spin-one unit, and analytic
triangular connection imply Smith valuations \((0,0,2)\) over the discrete
valuation ring of analytic germs at \(\omega_n\)?

Primary evidence:

- [`local_selector_v1`](../../black_hole_programme/phase3/axial_qnm_projective_evans_contour_completion/local_selector_v1/)
- [`axial_qnm_spin_one_local_unit_v1`](../../black_hole_programme/phase3/axial_qnm_spin_one_local_unit_v1/)

### 3. Radial Fredholm and causal bridge

Does the fixed-domain exterior-complex-scaled pencil give the claimed
rank-one double pole, and is the compactly cut-off transfer its unique
meromorphic continuation from the initial retarded Laplace half-plane?

Primary evidence:

- [`axial_qnm_ecs_fredholm_v1`](../../black_hole_programme/phase4/axial_qnm_ecs_fredholm_v1/)
- [`axial_qnm_causal_laplace_bridge_v1`](../../black_hole_programme/phase4/axial_qnm_causal_laplace_bridge_v1/)

### 4. Validated numerics

Are the projective charts, interval enclosures, Jost tails, contour
orientation, zero-free boundary bounds, and winding calculation sufficient
to prove the selector is nonzero on the enclosed QNM cell?

The machine-readable dependency ledger is the
[Paper 17 claim map](../../paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json).

### 5. Reconstruction and observability

Does the outgoing Einstein root have nonzero radiative trace at future null
infinity? Which parts of the generalized constant component obey standard
asymptotic-flatness conditions, and which require a differentiated or
augmented endpoint domain?

Primary evidence:

- [`axial_qnm_null_infinity_reconstruction_v1`](../../black_hole_programme/phase4/axial_qnm_null_infinity_reconstruction_v1/)
- [`axial_qnm_conserved_source_overlap_v1`](../../black_hole_programme/phase4/axial_qnm_conserved_source_overlap_v1/)

## Exact claim boundary

The paper does not prove:

- a full off-shell metric/BV retarded propagator;
- an inverse-Laplace contour deformation, complete QNM expansion, or global
  late-time waveform;
- standard radiative falloff for the generalized constant component;
- a nonzero overlap for a specified real causal astrophysical source;
- detector sensitivity;
- the polar analogue, all-multipole Bach nonsplitting, or a Kerr result;
- quantum positivity, unitarity, or viability of pure Weyl gravity.

The local isolated-resonance contour has the Jordan polynomial
\(e^{i\omega_n t}(V_1+itV_0)\). This is not promoted to a theorem about the
complete retarded waveform.

## One-command reproduction

```bash
bash ci/review-paper17.sh
```

The script verifies committed certificate families and runs the adversarial
claim-map tests. It checks internal consistency and deterministic
reproducibility. It does not constitute an independent derivation.

## What would change the scientific conclusion?

Any of the following would be decisive:

- a missing coupled massive term that changes the first-jet divisor;
- a valid endpoint-normalization objection that permits an opposite Jost
  admixture;
- an interval or branch error that allows the selector to contain zero;
- a failure of the analytic-germ Smith reduction;
- a domain error invalidating the fixed-domain Fredholm realization;
- a mismatch between the retarded Laplace transfer and its asserted
  meromorphic continuation.

Please report the smallest reproducible objection rather than reviewing the
entire programme. A confirmed failure will be recorded as a scientific result
of the AI-research experiment.
