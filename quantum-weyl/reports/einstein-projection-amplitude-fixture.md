# Einstein-projection and MHV reference fixture

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

The future comparison is deliberately not executed.  It requires the complete
support-local BV $q_2$, the verified physical contraction, a nonlinear
Einstein tangency projector or theorem, and a normalization dictionary.  The
adapter must also project the source onto every extra-Weyl complement: a
nonzero component is branch leakage, not an Einstein amplitude.

Reproduce with:

```bash
python3 quantum-weyl/transfer/einstein_projection_amplitude_fixture_certificate.py --check
python3 -m unittest quantum-weyl/transfer/tests/test_einstein_projection_amplitude_fixture.py
```

## Verification receipt

On 2026-07-16 the pinned Einstein-sector theorem reproduced in 0.04 s, the
fixture certificate passed in 0.45 s, the fixture and nonlinear-ledger modules
ran eight tests in 0.74 s, and strict AJV Draft 2020-12 validation passed in
1.27 s.  Tier 0 additionally covers Python compilation, JSON parsing, source
hashes, and scoped diff checks.  Tier 3 was not run because this adds a
reference fixture and a fail-closed interface without changing shared algebra,
executing the nonlinear projection, promoting G5, or claiming a release
theorem.
