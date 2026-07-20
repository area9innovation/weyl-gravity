# Candidate A: exact auxiliary-scalaron obstruction

## Verdict

Candidate A fails the common physical-sign gate on the frozen unit-cylinder
action:

\[
\boxed{\text{CANDIDATE A OBSTRUCTED}}
\]

The failure is not inferred from the Einstein scalaron formula and is not a
metric-only trace calculation.  Introducing the mandatory auxiliary scalar
exposes the complete mixed metric rows and gives a consistent sector that
satisfies both the metric and auxiliary equations.

## Auxiliary action and the missing mixed rows

For

\[
\beta=-\frac1{144},\qquad M_P^2=\frac16,\qquad V_0=\frac14,
\]

write

\[
\beta R^2=\chi R-\frac{\chi^2}{4\beta}.
\]

The cylinder background has

\[
R_0=6,\qquad \chi_0=2\beta R_0=-\frac1{12}.
\]

With \(\psi=\chi+1/12\), the complete scalar-tensor density is

\[
\psi(R-6)+36\psi^2.
\]

Its quadratic Hessian is

\[
\begin{pmatrix}
B_{C^2} & L\\
\delta R & 72
\end{pmatrix},
\qquad
(L\psi)_{\mu\nu}
=\nabla_\mu\nabla_\nu\psi
-g_{\mu\nu}\Box\psi
-R_{\mu\nu}\psi.
\]

Because the cylinder is not Einstein, \(L\psi\) is not generally pure trace.
This is the row omitted by the earlier direct-sum promotion.  The new
certificate therefore supersedes the claim that the strict complement was
unchanged.  It retains the earlier double-root tuning, trace Schur complement
and reduced iterated-Green identity.

## Consistent full-Hessian scalar sector

Set

\[
h_{\mu\nu}=u(t)\bar g_{\mu\nu},\qquad \psi=\psi(t),
\qquad P_2=\Box+2.
\]

The Weyl-squared Bach Hessian annihilates a pure trace exactly.  The full mixed
metric rows and auxiliary row reduce to

\[
P_2\psi=0,\qquad P_2u=24\psi.
\]

Thus

\[
P_2^2u=0,
\]

but the second-order auxiliary parent is

\[
H_A(P_2)=
\begin{pmatrix}
0&-3P_2\\
-3P_2&72
\end{pmatrix}.
\]

Its reduced advanced/retarded inverse is

\[
(H_A^\pm)^{-1}=
\begin{pmatrix}
-8G_2^\pm G_2^\pm&-\frac13G_2^\pm\\
-\frac13G_2^\pm&0
\end{pmatrix}.
\]

So the scalar Schur-complement calculation was algebraically correct.  What it
did not determine was the physical current and sign.

## Lee--Wald sign and raw \(D\)

After integrating over \(S^3\), the homogeneous quadratic density is

\[
L_{\rm hom}
=-3\dot\psi\dot u-6\psi u+36\psi^2.
\]

Its velocity Hessian is

\[
\begin{pmatrix}0&-3\\-3&0\end{pmatrix},
\]

with exact inertia \((1,1)\).  The reduced Lee--Wald form is nondegenerate,
but split.

In the state basis \((u,\dot u,\psi,\dot\psi)\), raw cylinder time translation
has characteristic and minimal polynomial

\[
(\lambda^2-2)^2.
\]

It therefore has real roots \(\lambda=\pm\sqrt2\) and size-two Jordan blocks.
The action-derived Hamiltonian is

\[
H_D=-3\dot u\dot\psi+6\psi u-36\psi^2.
\]

It takes both signs.  Moreover,

\[
\iota_D\Omega=dH_D
\]

with \(dH_D\ne0\), so raw \(D\) is not a presymplectic degeneracy on the new
scalar sector.  The zero-charge set is only the proper quadratic cone
\(H_D=0\).

For every scalar harmonic,

\[
\Omega_\ell^2=\ell(\ell+2)-2.
\]

The \(\ell=0\) modes grow or decay as \(e^{\pm\sqrt2t}\) and have Jordan
partners.  Every \(\psi\ne0\) mode is Diff-nontrivial because
\(\delta R=-72\psi\), whereas
\(\delta R(\mathcal L_\xi\bar g)=\mathcal L_\xi\bar R=0\).

The Einstein control gives

\[
m_0^2=\frac{M_P^2}{12\beta}=-2,
\]

in agreement with, but not used in place of, the full cylinder result.

## Berger gate

The frozen positive Berger clock belongs to a different action.  At its
rational fixture \(q=9/40\), the Candidate-A action difference has

\[
R_B=\frac{151}{80},
\qquad
\Delta F=\frac{93839}{921600},
\qquad
\Delta F'=\frac{809}{5760}.
\]

The four orthonormal metric Euler residuals are

\[
\left(
\frac{93839}{1843200},
\frac{135917}{1843200},
\frac{135917}{1843200},
-\frac{12943}{368640}
\right),
\]

so the frozen Berger solution is not preserved.  This does not obstruct a
separately retuned Berger family for the changed action.

## Seven-gate disposition

1. Action-derived BV/CME: **PASS**.
2. Arbitrary compact-support \(u\): **replaced by a physical scalar sector**.
3. Complete causal parent: **not promoted after the terminal sign failure**;
   the reduced scalar Green block is exact.
4. Reduced cyclic current: **exact and nondegenerate, but split**.
5. No negative/uncontrolled direction: **FAIL**.
6. Zero-charge \(D\)-gauge sector preserved: **FAIL**.
7. Frozen healthy Berger clock compatible: **FAIL**.

Candidate A enters the later A/B comparison as a failed candidate.  Candidate
B is the next classical work item.

## Reproduction

```bash
python3 d_quotient_classical/compensator/candidate_a_r2_auxiliary_scalar_obstruction.py --check
python3 d_quotient_classical/compensator/verify_candidate_a_r2_auxiliary_scalar_obstruction.py
python3 -m unittest d_quotient_classical.compensator.tests.test_candidate_a_r2_auxiliary_scalar_obstruction
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-candidate-a-r2-auxiliary-scalar-obstruction-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1.json
```

No Hadamard, anomaly, QME, particle, scattering or unitarity result is claimed.

CLOSE-OUT: OBSTRUCTED — Candidate A has an exact physical-sign, raw-\(D\), and frozen-Berger obstruction; retain the reduced scalar Green block and proceed to Candidate B.
