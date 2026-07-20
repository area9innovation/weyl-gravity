# Observer Berger apparatus reduced-cohomology pairing close-out

The action-derived apparatus parent and the existing 108-row Berger unary
carrier were imported by exact hashes.  The physical reduction cannot yet be
formed: the parent contains an action formula, field/parity lists, pairing
rank and principal symbols, but no row-level combined \(q_1\).

Eight exact interfaces are absent: the combined carrier embedding, sparse
row-level \(q_1\), row-level odd pairing, cohomological degrees, real
structure, \(K_{\rm Berger}\) matrix, detector-smearing-to-Maxwell chain map
and the typed zero-mode/support category.  This is consequential because the
108-row carrier already contains rods, memories and emitters.  Concatenating
the new 56 rows by matching names would double count semantic roles rather
than define a chain complex.

The machine-readable
`BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT` now specifies the
required row table, exact operators, support sectors, identities, cohomology
outputs, contraction data and mutations.  No isolated 56-row reduction is
reported as physical cohomology.

Until that contract is instantiated, the pairing radical/signature, physical
apparatus classes, persistent memory representatives and reduced detector
rank remain `NO_CERTIFIED_MAP`.  The parent action and its leading probe rank
are not retracted.

Verification: `py_compile` passed in 0.05 s and the method-distinct verifier
in 0.09 s.  The first combined test run correctly exposed that the atlas
test reserves IDs containing `crosswalk` for the two cross-background rows;
the new same-background row was renamed `reduced_cohomology_preflight`.
The corrected suite passed 59 tests in 32.39 s, followed by atlas schema
validation and independent replay.  Two `pdflatex` passes completed in
0.53 s and 0.52 s; scoped `git diff --check` passed.  Tier 2 uses exact
dependency hashes because no shared operator changed.  Tier 3 was not run
because no theorem, freeze, tag or release is promoted.

CLOSE-OUT: SHORTFALL — the combined gravity-clock-Maxwell-plus-apparatus row-level q1 crosswalk is missing, so physical cohomology cannot be computed

EVIDENCE: `closed_universe_observers/certificates/BERGER_DYNAMICAL_APPARATUS_REDUCED_COHOMOLOGY_CROSSWALK.json`

MISSING-DEP: BERGER_DYNAMICAL_APPARATUS_COMBINED_Q1_CROSSWALK_CONTRACT
