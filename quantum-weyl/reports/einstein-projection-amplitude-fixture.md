# Einstein-projection and helicity parity-pair reference fixture

This N-G5 preparatory rail pins the certified local inclusion of Einstein
solutions into the Bach-flat solution locus.  That theorem supplies the local
helicity-$\pm2$ module, but not a nonlinear projection of conformal-gravity
vertices or an asymptotic scattering-state embedding.

The reference calculation uses the holomorphic complex three-point branch

\[
\tilde\lambda_1=\tilde\lambda_2=\tilde\lambda_3=(1,0),
\quad
\lambda_1=(1,0),\quad \lambda_2=(0,1),\quad
\lambda_3=(-1,-1).
\]

Every momentum $p_i=\lambda_i\tilde\lambda_i$ is null and
$p_1+p_2+p_3=0$.  The exact brackets are

\[
\langle12\rangle=\langle23\rangle=\langle31\rangle=1,
\qquad [12]=[23]=[31]=0.
\]

For helicities $(--+)$, the stripped Einstein reference is therefore

\[
M_3^{--+}=\frac{\langle12\rangle^6}
{\langle23\rangle^2\langle31\rangle^2}=1.
\]

Its little-group factor is $t_1^4t_2^4t_3^{-4}$, and exchange of the two
negative-helicity legs leaves it invariant.  This is the flat-space stripped
factor in Eq. (6.2) of Adamo and Mason,
[*Conformal and Einstein gravity from twistor actions*](https://arxiv.org/abs/1307.5043).

The certificate also evaluates the parity-conjugate anti-holomorphic branch.
With common holomorphic spinors and
$[12]=[23]=[31]=1$, the $(++-)$ factor is

\[
M_3^{++-}=\frac{[12]^6}{[23]^2[31]^2}=1,
\]

with little-group factor $t_1^{-4}t_2^{-4}t_3^4$.  The two exact fixtures
therefore test both helicity orientations without importing a physical
conformal-gravity coefficient.

## Fail-closed input gates

The fixture now requires exact equality of six setting fields: setting,
background, phase space, source theory, target sector, and normalization
identifiers.  Both known
Berger-clock identifiers route to `BERGER_REDUCED_MODE_CARTAN_RAIL`; they are
not admissible inputs to the complexified flat Einstein amplitude rail.  This
prevents a homogeneous compact reduced-mode $q_2$ from being interpreted as a
flat radiative vertex.

The gauge-covariant linearized compensated defect

\[
\Delta_{mn}=G^{(1)}_{mn}(\widehat h)-T_{mn}/c_1
\]

and its same-source condition $Q(T)=0$ are imported from the pinned classical
preflight.  That certificate explicitly does not construct a full BV defect
chain map or prove nonlinear tangency.  The separately pinned projectors
$\Pi_E=1+\Box/M_2$ and $\Pi_M=-\Box/M_2$ are exact only on already-TT fields
for nonzero $M_2$.  They are not used here: no projector on the unreduced
Diff $\times$ Weyl BV complex exists, and their pure-Weyl limit is singular.

The future physical test must instead apply an exported full-BV nonlinear
Einstein-defect chain map to $q_2(\iota_E x,\iota_E y)$ and obtain zero or a
certified $q_1$-exact trivialization.  Until that map lands, tangency remains
uncomputed.

The normalization dictionary is locked at `stripped_einstein_shape_v1`.
Bracket shape, helicities, and little-group weights are included.  Overall
gravitational coupling, phase, momentum delta function, and conformal-gravity
action normalization are excluded.  Shape comparisons are allowed, but an
overall coefficient match is forbidden until every excluded factor is
declared.

The future comparison is deliberately not executed.  It requires a
setting-matched complete support-local BV $q_2$, the verified physical
contraction, the full-BV nonlinear defect map, and the missing normalization
factors.  A nonzero defect is branch leakage, not an Einstein amplitude.

Reproduce with:

```bash
python3 quantum-weyl/transfer/einstein_projection_amplitude_fixture_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_einstein_projection_amplitude_fixture.py
```

## Verification receipt

The current verification receipt is recorded by the deterministic commands
above, strict Draft 2020-12 schema validation, Python compilation, JSON
parsing, content hashes, and scoped diff checks.  Tier 3 is not required
because this hardens a reference interface without changing shared algebra,
executing the nonlinear projection, promoting G5, or claiming a release
theorem.
