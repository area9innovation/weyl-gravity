# Corrected Berger observer-apparatus interaction import gate

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

## Result

The repaired cyclic $q_2$ imports exactly on the existing 64
gravity-clock-Maxwell rows.  It includes the Maxwell stress vertex
$q_2(A,A)\to\widehat h^+$.  The previously certified detector matrix

\[
M_0=\begin{pmatrix}C_{00}&0\\0&C_{11}\end{pmatrix},
\qquad C_{00},C_{11}>0,
\]

is retained only as an imported **probe-limit baseline**.  It is not yet the
linear transfer theorem of an adjoined rod-memory-Maxwell complex: no extended
unary differential or retarded Green homotopy has been exported.

## Correct action arity

The repository uses

\[
Q(\phi)=q_1(\phi)+\frac1{2!}q_2(\phi,\phi)
+\frac1{3!}q_3(\phi,\phi,\phi)+\cdots,
\]

so $q_n$ has $n$ inputs and is paired with the $(n+1)$-st action derivative.
For the memory readout this gives

| action monomial | action degree | induced operation |
|---|---:|---:|
| $pA$ | 2 | $q_1$ |
| $pA\,\delta R$ | 3 | $q_2$ |
| $pA(\delta R)^2$ | 4 | $q_3$ |

Thus the cubic $pA\delta R$ term does **not** require $q_3$.  The first $q_3$
readout terms come from quadratic dependence of the smearing, composite
polarization, metric pairing, or volume density on fluctuations.  A generic
smooth $\rho(\Theta,R)$ has an unbounded Taylor tower unless a polynomial
truncation or an auxiliary detector-profile model is declared.

## Apparatus interface choice

The interface fixes the ambiguous modeling choices as follows.

- The rods are three dynamical relational scalars and require BV partners.
- Detector polarization is composite,
  $P_a=d\Theta\wedge dR^a$; it is not a separate field family.
- Each memory uses a dynamical pair $(m_a,p_a)$ with BV partners.
- The currents $J_b$ remain external $q$-closed conserved sources at this
  gate.  A dynamical emitter and its recoil are a later interaction input.

The bilinear $pA$ readout is part of the extended $q_1$.  The next nonlinear
certificate must therefore begin with a common rod-memory-Maxwell unary
complex, its cyclic pairing, and an advanced/retarded Green homotopy.  Only
then can this team recompute the source-to-memory transfer in the extended
complex.

## Team and gauge boundary

The nonlinear classical team supplies the action-derived apparatus
$q_1,q_2,q_3$ (and higher operations when the profile requires them), their
cyclicity and $K_{\mathrm{Berger}}$ identities, gravitational backreaction,
and the extended Green homotopy.  The closed-universe team imports those
results and tests whether observer evaluation is a chain-compatible cyclic
morphism.  This follows work package O4 and avoids duplicating the nonlinear
programme.

Raw $D$ remains distinct from $K_{\mathrm{Berger}}=D-\omega R$.  Its scoped
linearized presymplectic nullity cannot replace $K_{\mathrm{Berger}}$
equivariance on the extended apparatus complex.

## Conditional formal rank stability

There is one useful theorem available before the deformation is constructed.
If a gauge-compatible formal observer deformation

\[
M(\kappa)=M_0+\kappa M_1+\kappa^2M_2+\cdots
\]

exists, then the constant term of its determinant is
$C_{00}C_{11}>0$.  Hence $\det M(\kappa)$ is a unit in the formal power-series
ring and the record map remains rank two formally.  This is a conditional
algebraic lemma, not evidence that the interacting deformation exists or
descends through the gauge quotient.

## Verification

```text
python3 closed_universe_observers/generate_berger_observer_interaction_import_gate.py --check
python3 closed_universe_observers/verify_berger_observer_interaction_import_gate.py
python3 -m pytest -q closed_universe_observers/tests/test_berger_observer_interaction_import_gate.py
```

Seven mutations remove the cyclic repair, reintroduce the arity error, promote
rank two without the extended unary/Green data, turn composite polarization
into an undeclared independent field, violate the nonlinear-team handoff,
identify raw $D$ with $K_{\mathrm{Berger}}$, or promote the incomplete
interaction.  All fail closed.
