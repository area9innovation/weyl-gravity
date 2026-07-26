# Paper 17 referee major revision

Date: 2026-07-26  
Work item: `sf:program/work/phase4-black-hole-paper17-referee-major-revision`  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

Paper 17 has been revised against the external major-revision report.  The
central result remains intact:

1. the axial \(\ell=2\) Bach spin-two block is a non-split
   Regge--Wheeler self-extension;
2. the certified Schwarzschild QNM has full Smith type \((0,0,2)\);
3. the generalized root has nonzero Ricci-carrier quotient;
4. the compact-source, compact-observation exterior radial Green operator
   has a nonzero rank-one pole of order two;
5. the leading coefficient survives an outgoing Bondi-shear trace and is
   not annihilated by the complexified conserved, traceless odd source
   space.

The revised title and abstract now state the axial \(\ell=2\) scope before
introducing the differential-module mechanism.

## Decisive scientific correction

The previous draft compressed the relationship between the scalar
mass-deformed Regge--Wheeler equation and the full coupled massive axial
system too aggressively.  The authority certificate
`einstein_weyl_critical_mass_jet_v1/certificate.json` explicitly records

- `physical_mass_jet_equals_intrinsic_radial_tau: false`;
- `physical_b_equals_minus_mass_derivative_of_jost: false`;
- `physical_massive_qnm_slope_certified: false`.

The manuscript and claim map now agree with those gates.  The exact statement
is:

\[
  [\mathcal I_{\rm Bach}]
  =\frac{i\omega}{2}[\mathcal I_{\rm mass}^{\rm gr}],
  \qquad
  [\mathcal I_{\rm mass}^{\rm gr}]=[f],
\]

where \(L_m^{\rm gr}=D^2+\omega^2-V_2-mf\) is the spin-two graded
mass-squared tangent.  The relation \(m=(i\omega/2)\tau\) is a
fixed-frequency tangent-cocycle normalization, not a global
reparameterization of operator families.

The differentiated Coulomb and plane-wave asymptotics remain an exact formal
calculation.  They are no longer used to claim equality of physical Jost
derivatives: an opposite-Jost admixture must still be excluded by a displayed
full-system map and a Volterra or equivalent uniqueness theorem.

## Referee issues closed in the manuscript

### Massive-system scope

- \(m\) is defined as a signed squared-mass coefficient.
- The scalar equation is identified as a graded projection.
- The complete coupled massive axial system and physical massive-QNM slope
  are explicit non-results.
- The relation to the massive-spin-two literature is stated directly.

### Certificate self-containment

- The nonsplitting proof now displays the exhaustive rational ansatz, the
  complete \(6\times3\) coefficient matrix, the right-hand side, and fixed
  coefficient and augmented minors.
- The manuscript records the trust boundary, versions, commands, and
  outward-rounded interval convention.
- An immutable DOI-bearing archive is an explicit submission gate; a Git
  commit alone is not described as archival preservation.

### Selector and validated numerics

- The projective Evans coefficient \(\delta\), its derivatives
  \(\delta_\omega,\delta_\tau\), and
  \(\kappa_n=\delta_\tau/\delta_\omega\) are defined.
- The contour, orientation, root disk, arithmetic backend, precision,
  Taylor order, and transport-step counts are stated.
- A certified enclosure is displayed:
  \[
    \operatorname{Re}\kappa_n\in[-0.047,0.022],
    \qquad
    \operatorname{Im}\kappa_n\in[0.064,0.138].
  \]
  Its imaginary interval excludes zero.

### Endpoint and observation bridges

- The endpoint mass comparison is labeled formal and its exact missing
  uniqueness step is named.
- A new outgoing-trace proposition proves coefficientwise that an analytic
  null-infinity observation map preserves the principal Laurent coefficient.
- The large carrier reconstruction gauge and weakened constant-component
  falloff are stated without a finite-Bondi-flux promotion.

### Source scope

- The nonannihilation theorem is explicitly a theorem about complexified
  frequency-domain conserved, traceless sources.
- It does not claim a real, causal, temporally compact source, a specified
  material trajectory, or an energy-condition-satisfying matter model.

### Literature and editorial corrections

- The bibliography now includes the foundational Schwarzschild/QNM papers,
  massive spin-two and Einstein--Weyl QNM work, Keldysh and analytic-pencil
  references, Evans-function computation, and modern cut-off-resolvent QNM
  constructions.
- Smith valuations are defined over the local ring of analytic germs.
- The \(3\times3\) connection size is explained by one admissible endpoint
  line per second-order factor.
- The parent-action normalization is displayed before the mass-derivative
  inverse identity.
- The malformed simple-pole formula and all PDF layout warnings are fixed.

## Claim-map changes

The machine-readable claim map now fails closed on the same distinctions as
the manuscript.  It records:

- exact graded mass-squared direction: `true`;
- complete coupled massive axial crosswalk: `false`;
- endpoint-compatible physical mass jet: `false`;
- physical massive-QNM slope: `false`;
- outgoing-trace bridge: `true`;
- complexified conserved-source overlap: `true`;
- real causal source overlap: `false`.

The mutation suite contains explicit attempts to promote each false claim and
rejects them.

## Verification

Passed:

- Python parse checks for the claim-map producer, verifier, and tests;
- generated claim-map freshness and SHA-256 provenance;
- 15 claim-map regression and mutation tests;
- the projective-cocycle, full-contour winding, local-selector, spin-one
  local-unit, finite-interval/exterior Green, null-infinity, conserved-source,
  and critical-parent verifiers;
- 41 authority-package unit tests;
- two-pass `pdflatex` build with no warnings, overfull boxes, underfull boxes,
  or undefined citations/references;
- visual inspection of the title/abstract, nonsplitting proof,
  reproducibility table, claim boundary, conclusion, and bibliography;
- scoped `git diff --check`.

The projective-cocycle test suite exceeded the initial 30-second output
sampling window.  The partial run was not counted as a pass.  It was rerun to
completion and passed all eight tests in 63.006 seconds.

Tier 3 was not run.  This revision changes paper text, bibliography, and
claim binding, but no source operator, authority certificate, certificate
schema, shared algebra, release, freeze, or lifecycle state.  The revision
narrows the physical mass claim and replays the full affected authority
chain; it does not promote a new scientific lifecycle result.

## Artifact hashes

- manuscript:
  `656ff615f7e590b527acf3ceb5b9487d06959f10b200ced9d541dea9f0639127`
- PDF:
  `2b309c293585f5cc8885fd43d39b652acf9cbe4807817bc3ad02212104bb3247`
- claim map:
  `d1524f126245f20c085f9e06c2e7dc53f63001f98793a488070c54e369682756`
- claim-map producer:
  `5fa3ca15bf3251dc7f04b72a34d0303c2ae3acb24ae4805a6ce65e2e63627f0c`
- independent verifier:
  `a2b36a7c2ceb584c13b435b49ea18ce9bc4db081550d4f8cff5f07f6751a19e1`
- mutation suite:
  `4898b8a44eaac70f70a863d9e7c1e80e89e16824f39af433fec9ab3fbfdfea6f`

These hashes precede only the addition of this report and its tier receipt;
the six publication artifacts themselves are final.

## Remaining submission gates

1. Deposit an immutable DOI-bearing archive containing the manuscript claim
   map, authority certificates, source systems, verifier code, and environment
   lockfile.
2. If the physical massive-QNM interpretation is retained beyond the graded
   statement, construct and certify the complete massive axial/Jost
   crosswalk.
3. Keep the global causal resolvent, real-source construction, and retarded
   contour theorem outside the present result until independently certified.

CLOSE-OUT: DONE — the referee’s mathematical boundary
objections are resolved without weakening the certified self-extension,
defective-resonance, or exterior Green-pole theorems.

EVIDENCE: `reports/PAPER17_REFEREE_MAJOR_REVISION_TIER_RECEIPT.json`;
`paper/17-pure-weyl-schwarzschild-extension-structure-claim-map.json`.
