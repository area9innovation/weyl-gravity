# Transverse Nariai first-order Schur solve

The complete local first-order ansatz

\[
\dot Q=Q_0+Q^a\nabla_a:H_1\longrightarrow H_1^\vee
\]

has 45 unknown coefficients per output row.  Its exact coefficient map into
the differentiated gauge equation has shape
`60 x 45`
and rank `45`.  Every one of the
nine augmented systems has the same rank and no free parameter.

The unique correction contains
`59` nonzero PBW
coefficients and gives a zero corrected gauge residual.

This closes the local gauge-repair existence question.  It does **not** yet
identify the correction with the transverse variation of the action-derived
Bach Hessian, and it does not promote cyclicity through the authoritative
action/Hom-bundle adjoint.  Those are the next gate; the complete rank-310 SDR
and causal transfer remain open.
