# Local BV bootstrap

Dependency tag: `LOCAL-ALGEBRAIC`.

This directory is the first exact substrate for Branch A of the quantum
programme.  It implements a four-dimensional supercommutative coordinate-jet
algebra over rational coefficients, metadata for the minimal fields
`g`, `xi`, and `omega`, deterministic canonical serialization/hashing, and
the three minimal Diff x Weyl BRST rows stated in the brief.  The checked-in
certificate verifies nilpotency on every independent minimal generator,
commutation with coordinate total derivatives, and the odd graded Leibniz
rule.

The second scoped layer is an exact abstract-index tensor quotient.  It
implements signed Riemann and epsilon slot symmetries, graded factor order,
dummy-index renaming without erasing free-index order, exact rational relation
reduction, algebraic Bianchi identities, covariant total derivatives,
integration by parts, and an explicit spacetime-parity involution.  Exhaustive
generation of all 105 pairings of two Riemann tensors produces four canonical
symmetry orbits; the generated Bianchi relation has rank one, leaving a
three-dimensional parity-even quadratic curvature quotient.  The conventional
`Riemann_squared`, `Ricci_squared`, and `scalar_curvature_squared`
representatives independently span it.

The third scoped layer generates all 945 complete contractions of two
once-differentiated Riemann tensors.  Intrinsic symmetries leave 12 canonical
monomials.  Generated algebraic and differential Bianchi relations have
combined exact rank eight, leaving a four-dimensional finite quotient.  A
separate declared-sign constructor verifies covariant derivative commutators
on scalar, covector, and rank-two tensor witnesses.  Exact two-form Hodge
algebra verifies `star^2=+1` in Euclidean signature, `star^2=-1` in Lorentzian
signature, the corresponding real/complex chiral projectors, and their
exchange under parity.

Before cubic generation, the scaling layer adds collision-safe tensor
products with explicit index maps, contraction-aware commutator relations,
and signed orbit-first enumeration.  The full 10,395 raw `Riemann^3`
pairings partition exactly into 33 signed symmetry orbits: 20 vanish by
intrinsic symmetry and 13 are nonzero before algebraic Bianchi reduction.
Only the 33 orbit representatives require the general monomial canonicalizer.
Detailed certificate schemas are now executable contracts rather than
unvalidated documentation.

The first mixed order-six layer is now complete in the dimension-independent,
parity-even curvature sector.  The 13 nonzero cubic symmetry orbits reduce by
five generated algebraic-Bianchi relations to eight cubic classes.  A
generated 14-monomial `Riemann nabla^2 Riemann` bridge, the 12-monomial
`(nabla Riemann)^2` sector, exact total divergences, and contracted
commutators give a 39-column, rank-29 integrated quotient of dimension ten.
Eight cubic directions survive, while two derivative directions lie outside
their span.  The omitted degree-one total divergence restores the standard
17-element local order-six normal form before quotienting total derivatives.

The specialization foundation keeps this universal quotient immutable while
adding named relation families in exact stages.  Every stage emits its
projection matrix, kernel witnesses, parity-block dimensions, provenance,
and deterministic named-representative coordinates.  A dimension-checked
occurrence antisymmetrizer supplies the five-index Schouten primitive; Weyl
is a distinct tracefree tensor specification; and paired epsilon tensors
reduce through a signature-aware 24-term generalized-delta expansion.

The four-dimensional layer now applies that primitive exhaustively.  Across
all three order-six sectors, 3,328 endpoint selections generate 72 unique
nonzero Schouten rows of ambient rank 11.  Their induced rank on the universal
integrated quotient is two, giving an exact specialization from dimension ten
to dimension eight.  Both killed directions come from the cubic sector,
whose rank drops from eight to six; the derivative sectors acquire no further
dimension-dependent loss.  The surjective specialization map and its two
kernel witnesses are stored exactly.

The Weyl-decomposition hardening layer now makes the next specialization
safe to attempt.  Metric, Schouten, and Cotton tensors have exact declared
symmetries and the convention
`A_abc = nabla_b P_ca - nabla_c P_ba`.  The six-term Ricci decomposition,
its covariant derivative, and the cyclic Weyl--Cotton differential identity
are stored as exact tensor relations; expanding Cotton back to `nabla P`
reproduces the differentiated decomposition term for term.  The older
algebraic `Riemann -> Weyl` restriction now rejects every differentiated
Riemann factor, preventing it from silently dropping Schouten/Cotton terms.
Full-Weyl Hodge dualization flips the explicit parity block, with exact
`star^2=+1` in Euclidean and `star^2=-1` in Lorentzian signature on a complete
Weyl contraction.

The first derivative-safe Weyl image is now computed.  Expanding every
Riemann factor as `Weyl + metric wedge Schouten` and then setting Schouten and
all of its covariant derivatives to zero induces an exact surjection from the
eight-dimensional four-dimensional quotient onto a one-dimensional target,
with a seven-dimensional stored kernel.  The target begins with 17 nonzero
Weyl monomials; 106 mapped relations have rank 16.  The cubic,
`(nabla Weyl)^2`, and `Weyl nabla^2 Weyl` sectors each reach that same class.
An explicit odd Hodge companion is constructed.  Because this restriction
also sets Cotton to zero, it is a Schouten-flat image theorem rather than the
unrestricted Weyl-jet quotient or a complete parity-odd enumeration.

The dimension-four one-loop curvature sector is now generated separately
from that order-six image.  The 105 quadratic Riemann pairings reduce to the
three-dimensional `Riemann^2`, `Ricci^2`, `R^2` ansatz.  Exact Weyl variation
modulo the contracted Bianchi total derivative has rank one, and its
two-dimensional kernel is verified to be spanned by `C^2` and `E4`.
Independently generated target-native quadratic Weyl quotients have dimension
one in both the even and compressed dual-Weyl odd sectors.  `Box R` has an
explicit divergence witness, while `omega Box R` has the integrated
trivialization `-(1/12) s(R^2)`.  These are candidate catalogues; full
Diff--Weyl descent, antifield completion, and cohomology remain open.

The first descent layer is now exact.  A horizontal exterior algebra over the
coordinate jets verifies `d_h^2=0`, the density Lie-derivative BRST row,
nilpotency, and commutation of `Q` with `d_h`.  Repeated contraction with the
odd diffeomorphism ghost generates the full form-degree `4 -> 0` tower for a
strict Weyl density and its Weyl-ghost lift.  Exact row solving derives the
coefficients `1,-1,1/2,-1/6,1/24`.  This computes the nonzero Diff descents of
`C^2`, `C dual C`, `omega C^2`, and `omega C dual C`; it does not compute the
separate Euler Weyl-current descent or establish cohomological nontriviality.

This is not Gate A or Gate B.  In particular, the classical commit is
`NOT_FROZEN`; antifield and nonminimal rows have not been imported; and
general covariant curvature reduction remains incomplete.  The
once-differentiated standalone quotient does not apply integration by parts or commute
derivatives, because those operations mix `(nabla Riemann)^2` with cubic
curvature.  The tracefree-Weyl specialization, parity-odd sector, descent, and both
`H^{0,4}(s|d)` and `H^{1,4}(s|d)` remain unavailable.  These curvature
certificates may not be cited as a complete covariant jet normal form or
cohomology calculation.

Run the exact tests and reproduce the receipt from the repository root:

```bash
PYTHONPATH=quantum-weyl python -m unittest discover -s quantum-weyl/local_bv/tests -v
PYTHONPATH=quantum-weyl python -m local_bv.certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.curvature_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.differential_hodge_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.scaling_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.six_derivative_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.specialization_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.four_dimensional_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.weyl_decomposition_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.weyl_image_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.dimension_four_candidate_certificate --check
PYTHONPATH=quantum-weyl python -m local_bv.strict_descent_certificate --check
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_CURVATURE_CANONICALIZATION.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_SPECIALIZATION_FOUNDATIONS.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/COUNTERTERM_CANDIDATES_DIMENSION_FOUR.json
python3 quantum-weyl/schema/validate_result.py quantum-weyl/certificates/ANOMALY_CANDIDATES_DIMENSION_FOUR.json
```

The certificate is
[`certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json`](certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json).
Its repository-wide result-schema envelope is
[`../../quantum-weyl/certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json`](../certificates/LOCAL_BV_MINIMAL_BOOTSTRAP.json).
Running `python -m local_bv.certificate` without `--check` prints the
canonical regenerated JSON for review; it does not overwrite the receipt.

The detailed curvature receipt is
[`certificates/LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json`](certificates/LOCAL_CURVATURE_CANONICALIZATION_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_CURVATURE_CANONICALIZATION.json`](../certificates/LOCAL_CURVATURE_CANONICALIZATION.json).

The differential-curvature/Hodge receipt is
[`certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE.json`](certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION.json`](../certificates/LOCAL_DIFFERENTIAL_HODGE_CANONICALIZATION.json).

The scaling-foundations receipt is
[`certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS_CERTIFICATE.json`](certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS.json`](../certificates/LOCAL_ALGEBRA_SCALING_FOUNDATIONS.json).

The mixed order-six receipt is
[`certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT_CERTIFICATE.json`](certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT.json`](../certificates/LOCAL_SIX_DERIVATIVE_CURVATURE_QUOTIENT.json).

The specialization-foundation receipt is
[`certificates/LOCAL_SPECIALIZATION_FOUNDATIONS_CERTIFICATE.json`](certificates/LOCAL_SPECIALIZATION_FOUNDATIONS_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_SPECIALIZATION_FOUNDATIONS.json`](../certificates/LOCAL_SPECIALIZATION_FOUNDATIONS.json).

The four-dimensional Schouten receipt is
[`certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json`](certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT.json`](../certificates/LOCAL_FOUR_DIMENSIONAL_SCHOUTEN_QUOTIENT.json).

The Weyl--Schouten--Cotton hardening receipt is
[`certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE.json`](certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS.json`](../certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS.json).

The Schouten-zero Weyl-image receipt is
[`certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json`](certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE_CERTIFICATE.json),
with its common result envelope at
[`../certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE.json`](../certificates/LOCAL_SCHOUTEN_ZERO_WEYL_IMAGE.json).

The generated dimension-four candidate receipt is
[`certificates/LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json`](certificates/LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json),
with catalogues under [`../counterterms/`](../counterterms/) and
[`../anomalies/`](../anomalies/) and separate ghost-number-zero and
ghost-number-one common result envelopes under [`../certificates/`](../certificates/).

The strict-density descent receipt is
[`certificates/LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE.json`](certificates/LOCAL_STRICT_DENSITY_DESCENT_CERTIFICATE.json),
with the partial database at
[`descent/DESCENT_DATABASE_DIMENSION_FOUR_STRICT.json`](descent/DESCENT_DATABASE_DIMENSION_FOUR_STRICT.json).

Next admissible local steps are the Euler Weyl-current descent and the
unrestricted higher-derivative Weyl--Cotton jet quotient.  The antifield and
relative-cohomology layers still wait for the frozen classical schema.
