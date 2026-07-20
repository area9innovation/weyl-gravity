# Candidate B: exact unimodular three-form obstruction

## Verdict

Candidate B fails on the frozen unit-cylinder theory:

\[
\boxed{\text{CANDIDATE B OBSTRUCTED}}
\]

The Henneaux--Teitelboim term is globally represented as

\[
S_{\rm HT}
=\int_M\lambda_{\rm HT}\bigl(\operatorname{vol}_{\widehat g}-dA_3\bigr).
\]

This is not treated as a scalar multiplier row in isolation.  The certificate
includes the reducible tower

\[
A_3\longleftarrow C_2\longleftarrow C_1\longleftarrow C_0,
\]

its cotangent rows, three nonminimal doublets, Diff completion, real
structure and the unchanged Weyl quartet.

## First obstruction: the frozen cylinder is off shell

Candidate B uses the frozen \(\alpha_R=0\) action with

\[
M_P^2=\frac16,\qquad V_0=\frac14,
\qquad \bar\theta=\text{constant}.
\]

In an orthonormal frame on
\(\mathbb R_t\times S^3\),

\[
\bar g=\operatorname{diag}(-1,1,1,1),
\qquad
\operatorname{Ric}=\operatorname{diag}(0,2,2,2),
\qquad R=6.
\]

Both \(V_0\) and \(\lambda_{\rm HT}\) change only the
metric-proportional Euler row.  The invariant trace-free residual is

\[
E_{\mu\nu}^{\rm TF}
=\frac{M_P^2}{2}
\left(\operatorname{Ric}_{\mu\nu}
-\frac14R\,g_{\mu\nu}\right)
=\operatorname{diag}
\left(\frac18,\frac1{24},\frac1{24},\frac1{24}\right).
\]

It is nonzero and independent of \(\lambda_{\rm HT}\).  Consequently no
multiplier value makes the declared non-Einstein unit cylinder a stationary
point.  A complete retarded/advanced linearized parent cannot be promoted
about an off-shell background.

## Second obstruction: the trace becomes flux history

The topology failure is independent of the preceding background failure and
explains why a local Poincare-lemma calculation would give the wrong answer.
For a dressed pure trace

\[
\delta\widehat g_{\mu\nu}=u\,\bar g_{\mu\nu}
\]

and harmonic spatial three-form component

\[
a(t)=\int_{S^3}\delta A_3,
\]

the quadratic HT density is

\[
L_{\rm HT}^{(2)}
=\lambda_{\rm HT}(2u-\partial_t a).
\]

In the ordered basis \((u,a,\lambda_{\rm HT})\), its formally self-adjoint
Hessian is

\[
H_B(D)=
\begin{pmatrix}
0&0&2\\
0&0&D\\
2&-D&0
\end{pmatrix},
\qquad D^\sharp=-D.
\]

It has rank two over \(\mathbb Q(D)\) and the exact polynomial kernel

\[
H_B(D)
\begin{pmatrix}
D/2\\1\\0
\end{pmatrix}
=0.
\]

Thus

\[
u=\frac12\dot a
\]

with arbitrary flux history \(a\).  Candidate B does not eliminate the
arbitrary dressed trace or put it into a contractible block; it re-encodes it
in a topological carrier with no complete Green inverse.

## Compact topology and the global pair

Kunneth gives

\[
H^\bullet(\mathbb R\times S^3)
=(\mathbb R,0,0,\mathbb R,0),
\]

while compact support gives

\[
H_c^\bullet(\mathbb R\times S^3)
=(0,\mathbb R,0,0,\mathbb R).
\]

The \(H^3\) generator is \(\operatorname{vol}_{S^3}\).  The
\(H_c^4\) generator is detected by integration over spacetime.  Therefore:

* small gauge transformations \(A_3\mapsto A_3+d\epsilon_2\) do not change
  \(a(t)\);
* a compactly supported \(u\) of zero spacetime integral has a compactly
  supported \(a\)-primitive;
* a compactly supported \(u\) with nonzero integral changes the asymptotic
  flux and represents the \(H_c^4\) class;
* \(d\lambda_{\rm HT}=0\) retains a constant cosmological mode until the
  frozen metric equation selects \(\lambda_{\rm HT}=0\).

For a real three-form, the flux is real.  For a compact \(U(1)\) two-gerbe it
is periodic modulo the integral period lattice.  That discrete large-gauge
identification is not present in the local BV contraction and is not silently
used.

The global Lee--Wald form is

\[
\Omega_{\rm top}=\delta a\wedge\delta\lambda_{\rm HT}.
\]

It is nondegenerate on the ambient pair.  Raw \(D=\partial_t\) translates the
background flux, so

\[
\iota_D\Omega_{\rm top}
=V_{S^3}\,\delta\lambda_{\rm HT}
=d\!\left(V_{S^3}\lambda_{\rm HT}\right).
\]

Raw \(D\) becomes null only after imposing a fixed-\(\lambda_{\rm HT}=0\)
superselection tangent.  That is additional global data, not a conclusion of
the local action.

## Berger gate

The imported rational Berger clock remains a solution of its original
metric/clock equations.  Candidate B then forces
\(\bar\lambda_{\rm HT}=0\), while the volume constraint requires

\[
\bar A_3=t\,\operatorname{vol}_{\rm Berger}.
\]

At \(a=1\), \(c^2=9/40\), the normalized spatial volume coefficient is

\[
a^2c=\frac{3\sqrt{10}}{20}.
\]

Hence

\[
\mathcal L_D\bar A_3=\operatorname{vol}_{\rm Berger},
\]

whose class is nonzero in \(H^3(S^3)\).  No global two-form small-gauge
parameter compensates it.  Stationarity would require enlarging
\(K_{\rm Berger}=D-\omega R\) by the global closed-three-form shift and
fixing the conjugate cosmological sector.  The frozen raw-\(D\) sector is
therefore not preserved by Candidate B as stated.

## Seven-gate disposition

1. Action-derived BV/CME: **PASS at the formal local level**.
2. Compact-support \(u\): **FAIL**; it becomes arbitrary flux history.
3. Complete causal parent: **FAIL**; the background is off shell and the
   HT Hessian has a polynomial kernel.
4. Cyclic current: **exact**, but it exposes the global flux/multiplier pair.
5. No uncontrolled topological direction: **FAIL**.
6. Zero-charge raw \(D\): **FAIL without a new superselection restriction**.
7. Frozen Berger clock: **FAIL without a new global symmetry
   reclassification**.

This is a scoped no-go for the declared action, background and small gauge
group.  It does not rule out an active-clock retuning, a theory defined from
the outset in a fixed flux/cosmological superselection sector, or an enlarged
global gauge quotient.  Those are different theories.

## Reproduction

```bash
python3 d_quotient_classical/compensator/candidate_b_unimodular_threeform_obstruction.py --check
python3 d_quotient_classical/compensator/verify_candidate_b_unimodular_threeform_obstruction.py
python3 -m unittest d_quotient_classical.compensator.tests.test_candidate_b_unimodular_threeform_obstruction -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-candidate-b-unimodular-threeform-obstruction-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json
```

No Hadamard, anomaly, QME, particle, scattering or unitarity result is
claimed.

CLOSE-OUT: OBSTRUCTED — Candidate B cannot support the frozen unit cylinder and trades the dressed trace for an uncontrolled three-form flux history with nontrivial compact/global cohomology and raw-\(D\) charge.
