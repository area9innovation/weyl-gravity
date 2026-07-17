# Berger observer-apparatus interaction import gate

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Result

The repaired cyclic $q_2$ can be imported without invalidating the already
certified first-order detector coefficient.  Thus

\[
M_{ab}=Q_a[dG_{\mathrm{ret}}J_b]
=\begin{pmatrix}C_{00}&0\\0&C_{11}\end{pmatrix},
\qquad C_{00},C_{11}>0,
\]

remains the linear source-to-memory response, of rank two.

This does **not** yet incorporate the detector apparatus into the interacting
gauge quotient.  The repaired support-local coefficient ledger has exactly 64
gravity-clock-Maxwell rows.  It contains the exact Maxwell stress vertex
$q_2(A,A)\to\widehat h^+$, but it has no rod, detector-polarization, memory,
or emitter rows and hence no BV partners for those variables.  Extended
cyclicity is therefore not a well-typed identity on the currently exported
complex, rather than a tested identity with a nonzero residual.

## First obstruction and required extension

Four apparatus families must be adjoined with their antifields: the three rod
scalars, detector polarization/transport data, each memory pair $(m_a,p_a)$,
and a dynamical emitter-current sector.  Their action-derived unary operators,
Diff cotangent lifts, stress vertices, readout vertices, and $K_{\mathrm{Berger}}$
action must then be exported into one common cyclic ledger.

There is also an arity obstruction.  With fixed external smearing data,
$p_a q_a[F]$ is bilinear in $p_a$ and $A$.  Once localization is genuinely
relational, however,

\[
q_a[F]=\int \rho_a(\Theta,R)\,\langle dA,P_a\rangle_{\widehat g}
\,\mathrm{dvol}_{\widehat g},
\]

so its Taylor expansion includes a $p_a A R$ block.  A $q_2$-only repair is
therefore insufficient; the apparatus extension must include $q_3$ and all
cyclic cotangent partners (and may require higher Taylor terms for a nonlinear
bump profile).

## Gauge boundary

The present $K_{\mathrm{Berger}}=D-\omega R$ results apply through arity three
on the existing gravity-clock sector and through arity two on the 64-row
gravity-clock-Maxwell sector.  Raw $D$ remains a distinct affine generator:
its fixed-coupling linearized presymplectic-null result cannot replace an
action-equivariant $K_{\mathrm{Berger}}$ calculation on the added apparatus.

Accordingly, gravitational backreaction is now *vertex-ready* but not solved:
the Maxwell stress source exists, while no second-order metric/apparatus
solution or backreacted rank-two response has been computed.  The classical
observer algebra remains fail-closed.

## Verification

```text
python3 closed_universe_observers/generate_berger_observer_interaction_import_gate.py --check
python3 closed_universe_observers/verify_berger_observer_interaction_import_gate.py
python3 -m pytest -q closed_universe_observers/tests/test_berger_observer_interaction_import_gate.py
```

The mutation rail removes the cyclic repair, injects a cyclicity defect,
collapses the transfer rank, erases the required $q_3$, identifies raw $D$
with $K_{\mathrm{Berger}}$, and attempts an illegal nonlinear promotion.  All
six mutations fail closed.
