# BT six-point positive-distribution completion no-go

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_DISTRIBUTION_COMPLETION_NO_GO_V1`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle: `CLASSIFIED`.

## Result

The exact positive six-point factorization pole cannot itself be completed as
a locally finite positive exclusive probability distribution. This closes the
most direct regulator route, but it does not rule out a finite wave-packet or
inclusive probability in which an on-shell sequential history is counted as a
separate outcome.

Near the exact transverse physical channel found in the predecessor
certificate, the leading density is

\[
  \frac{9}{8s^2}.
\]

If a positive extension existed, it would be a locally finite Radon measure.
But on the punctured compact interval \(\epsilon<|s|<L\), agreement away from
the pole forces the exact mass

\[
  2\int_\epsilon^L\frac{9\,ds}{8s^2}
  =\frac94\left(\frac1\epsilon-\frac1L\right),
\]

which diverges as \(\epsilon\downarrow0\). Delta-supported counterterms cannot
alter this punctured mass. Therefore no locally finite positive extension
exists.

Linear distributional extensions do exist. If scaling degree is kept at two,
two extensions may differ by \(c_0\delta+c_1\delta'\). Reflection symmetry of
the leading pole removes the odd \(\delta'\) freedom but leaves \(c_0\delta\).
Every resulting finite-part prescription loses positivity. For example, the
symmetric Feynman-modulus preflight gives

\[
 \frac{9}{8(s^2+\epsilon^2)}
 =\frac{9\pi}{8\epsilon}\,\delta(s)+\text{finite part}+o(1)
\]

in distributional form. On the constant test function over \([-L,L]\), the
finite remainder is \(-9/(4L)\). The divergent delta term is therefore not a
positive exclusive event that can simply be subtracted; physically it signals
an on-shell sequential four-point history.

## Audit of existing completion candidates

The available five-point NLO response is order \(\lambda^6\) and lives on an
external daughter-collinear boundary. The new object is the order
\(\lambda^8\) density of a six-point tree amplitude on an internal massless
\(3|3\) factorization hypersurface. These are different orders and different
singular supports, so the former cannot presently cancel the latter.

The certified zero from \(R_t P R_t^\dagger\) is a projector pushforward, not a
physical S-matrix summand. The finite Møller certificate supplies one
isometric hard/vacuum input column. Its two-sided completion theorem leaves an
infinite-dimensional defect partial unitary unselected and does not construct
BT asymptotic-Hamiltonian affiliation. None of these objects supplies the
missing sequential-history subtraction or survival term.

## Physical next gate

Construct the on-shell factorization subspace in the incoming defect continuum
and derive from BT dynamics the action of a two-sided finite-time, wave-packet,
or stochastic Møller operator on it. The construction must count the
sequential four-point history separately, control the regulated square of the
on-shell delta, and use one detector normalization for the sequential and
connected outcomes. In the language of the defect theorem, this is the first
physical restriction of the previously arbitrary infinite-dimensional
partial unitary \(W\).

This result does not prove or disprove a finite inclusive probability, choose
a finite-part constant, construct a complete Møller/LSZ/S operator, establish
Eq. (19), compute matching loops, lift to metric BV--BRST gravity, or establish
anything `LORENTZIAN-CAUSAL`.

## Verification receipt

The producer recomputes the exact punctured mass and regulated limit. The
method-distinct verifier independently integrates both kernels, validates all
five imported content hashes and the schema, and tests the object-type and
claim boundaries. The scoped unit suite includes falsifying mutations for a
false positive extension, an unjustified physical promotion, and singular-
support conflation. Processes are memory-capped at 500 MB.

- Producer: `ulimit -v 500000; python3 reverse_physics/bt_six_point_positive_distribution_completion.py --write --check` -- PASS, 15/15 checks, 0.79 s, 67,480 KB maximum RSS.
- Independent verifier: `ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_positive_distribution_completion.py` -- PASS, 15/15 checks, 1.15 s, 74,188 KB maximum RSS.
- Scoped unit tests: `ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_positive_distribution_completion` -- PASS, 5 tests, 1.37 s, 75,420 KB maximum RSS.
- A final affected-chain replay passed the full-phase-space producer/verifier (16/16 and 14/14), pole producer/verifier (12/12 and 12/12), distribution producer/verifier (15/15 and 15/15), and all 17 scoped tests under the same 500 MB cap.
- Papers V and VI each passed two capped `pdflatex -interaction=nonstopmode -halt-on-error` runs; the second passes took 0.56 s with 50,556 KB and 0.56 s with 50,796 KB maximum RSS, respectively.
- Science Forge conformance reports the new event and work item as `OK`. The repository-wide planning scan still refuses on ten pre-existing nonconformances outside this work item; that global refusal is not recorded as a pass or repaired here.
- The prose advisory is non-certifying. Paper V remained within the emphasis and dash budgets but retained pre-existing parenthetical/abstract findings; Paper VI remained within emphasis, dash, parenthetical and novelty budgets but retained its pre-existing abstract finding.
- Tier 0 parse, schema, TeX and diff checks are recorded in the coherent commit verification. Tier 2 reruns the content-addressed six-point positivity-to-pole chain because the shared note and predecessor hashes change. Tier 3 is not run because this is a scalar classification result, not a freeze, theorem lifecycle promotion, shared-core algebra change, or release.

CLOSE-OUT: DONE -- no locally finite positive exclusive distribution extends the six-point double pole; a BT-derived sequential-history Møller action is the minimal physical input.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_POSITIVE_DISTRIBUTION_COMPLETION_NO_GO_V1.json`
