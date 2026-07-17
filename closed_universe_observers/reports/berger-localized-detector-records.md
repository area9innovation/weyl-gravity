# Two localized clock-labelled Berger detector records

## Result

The first localized detector layer now exists as a bridge-only classical
consumer of the authoritative Berger certificates.  In a local apparatus
chart, use the clock and three probe rods

\[
(\Theta,R^1,R^2,R^3),\qquad
d\Theta\wedge dR^1\wedge dR^2\wedge dR^3\ne0.
\]

The declared fixture has exact relational Jacobian `I_4`.  It places two
compact, disjoint detector windows at

\[
(\tau_0,r_0)=(1,(1/4,0,0)),\qquad
(\tau_1,r_1)=(2,(1/2,0,0)),
\]

after the imported emitter clock support `[-1,-1/2]`.  Their field-strength
records are

\[
Q_a[F]=\int \rho_a(\Theta,R)
  \langle F,d\Theta\wedge dR^1\rangle_{\widehat g}
  \operatorname{vol}_{\widehat g},\qquad a=0,1.
\]

Because the relational supports are disjoint, compact probe variations can
be supported independently in the two windows.  Their exact evaluation
matrix is `I_2`.  Thus `Q_0` and `Q_1` are linearly independent and generate
the real classical record algebra

\[
\mathcal A_{\rm record}=\mathbb R[Q_0,Q_1].
\]

The construction is Diff-covariant at probe order, Weyl invariant through
the clock metric `gHat`, and Maxwell-gauge invariant because it uses
`F=dA`.  Four mutation rails independently destroy the rod Jacobian, clock
label separation, support separation, and rank-two record conclusion.

## Source-to-record map and exact obstruction

Importing the compact current and retarded Green theorem defines the map

\[
j=d\kappa\longmapsto F_{\rm ret}=dG_{\rm ret}J
\longmapsto (Q_0[F_{\rm ret}],Q_1[F_{\rm ret}]).
\]

This map is well-defined, but the current imports prove only global
nonvanishing and retarded support.  They do not provide a pointwise Green
kernel or wave-front witness showing that `F_ret` is nonzero in both detector
windows chosen independently of the solution.  Consequently two localized
record functionals are certified, while two nonzero detector clicks are not.

This is the first exact obstruction to promoting the partial Berger observer
map: causal support is weaker than a nonzero, unique, no-wrap source-to-window
incidence theorem.

## Gauge and lifecycle boundary

The rods are healthy standard-sign probe scalar Cauchy data.  Their stress,
backreaction, and apparatus recoil are deliberately excluded, as required by
the staged classical gate.  Because that probe rod sector is not part of the
imported fixed-coupling phase space or interacting `K_Berger` complex, neither
raw-`D` nor `K_Berger` descent is promoted.

Therefore:

- `TWO_LOCALIZED_CLOCK_LABELLED_RECORD_FUNCTIONALS = true`;
- `SOURCE_TO_RETARDED_FIELD_TO_RECORD_MAP_DEFINED = true`;
- `TWO_NONZERO_RETARDED_RECORD_VALUES = false`;
- `D_DESCENT_WITH_RODS_CERTIFIED = false`; and
- `CLASSICAL_OBSERVER_MAP_CERTIFIED = false`.

The next exact gate is
`BERGER_POINTWISE_RETARDED_GREEN_KERNEL_TWO_WINDOW_WITNESS`.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_LOCALIZED_CLOCK_DETECTOR_RECORDS.json`.

## Verification

```bash
python3 closed_universe_observers/generate_berger_detector_records.py --check
python3 closed_universe_observers/verify_berger_detector_records.py
python3 -m pytest -q closed_universe_observers/tests/test_berger_detector_records.py
```

This is a `LOCAL-ALGEBRAIC` and `LORENTZIAN-CAUSAL` bridge consumer.  It is
not a backreacting apparatus theorem, a complete `D`-quotient observer
algebra, a quantum state construction, or a QME result.
