# Berger 108-row local rod Hessian PBW overlay

Status: `CERTIFIED_SCALAR_LOCAL_ROD_GAUGE_WAVE_HESSIAN_OVERLAY`.

The six linearly clock-dressed rods now have scalar gauge, cotangent-gauge, wave,
rod--metric, metric--rod and rod-induced metric--metric blocks in the canonical
108-row PBW grammar.  The construction derives the invariant-frame
Levi–Civita coefficients from the Koszul formula; it does not treat the Berger
frame as a coordinate frame.  Exact torsion, metric-compatibility and
contracted scalar-wave audits vanish.

The mixed block is the component expansion of the certified variation of the
scalar wave operator.  A second derivation directly varies the general
nonholonomic-frame Koszul formula: all ten metric-component columns agree with
nonzero metric first jets and PBW-reduced scalar second jets.  Its reciprocal
block is an explicit coefficient-aware formal transpose.  The metric--metric
block is the exact second variation of `-sqrt(-g) g^{-1}(dR,dR)/2`, summed over
all six backgrounds; two hundred direct rational-metric second-variation
fixtures agree exactly.

The generated payload contains six blocks, 256 nonzero matrix positions and
1,530 exact serialized terms.  Its schema pins those counts, the exact block
order, entry counts and row/column supports; the independent verifier rebuilds
the formal transposes and both direct-variation audits.

The dressing scope is now explicit.  This payload uses the certified first
jet of the raw-to-dressed clock canonical map.  It does not contain that
map's second jet or cotangent lift.  Equivalently, it does not yet contain
the radial and temporal clock-source blocks obtained by expressing the
invariant rod action in the linearly dressed carrier.  The complete replay
detects this omission in the Weyl/sigma column, so “clock-dressed” must not be
read as a nonlinear all-jet statement.

Together with the separate shifted `q2_64(Phi2,-)` payload this closes the
listed linear overlay input.  The action-derived second clock jet is the
next repair object; no tangent-cone, Bridge 3, finite-r causal or quantum
claim follows here.
