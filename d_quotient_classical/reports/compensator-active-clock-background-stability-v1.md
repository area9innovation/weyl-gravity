# Quadratic active-clock background stability

## Result

The independently frozen quadratic \(P(X)\) active-clock no-go is not a
single-fixture accident.  It persists on the exact rational open
neighbourhood

\[
\mathcal N=
\left\{
\frac{15}{16}<\kappa<\frac{17}{16},\quad
\frac15<q<\frac14,\quad
\frac23<\nu<\frac56
\right\},
\]

where

\[
\kappa=r_{\rm cyl}^{-2},\qquad q=c_{\rm Berger}^{2}
\quad(a_{\rm Berger}=1),\qquad
\theta=\nu t.
\]

Equivalently, the cylinder radius lies in

\[
\frac4{\sqrt{17}}<r_{\rm cyl}<\frac4{\sqrt{15}}.
\]

For every parameter point in \(\mathcal N\), the common stationary
cylinder/Berger action-space locus has rank five and is a single exact ray.
Every nonzero point on that ray fails the physical-sign gate and the raw
\(D\)-charge gate.  Thus

\[
\boxed{
\mathcal L_{\rm good}(\kappa,q,\nu)=\varnothing
\quad\hbox{for every }(\kappa,q,\nu)\in\mathcal N.
}
\]

This is a theorem about a parameterized family of action-space rays.  The
couplings vary with the backgrounds.  It is not a claim that one fixed action
supports every background in \(\mathcal N\).

## Frozen input

The computation imports the method-distinct freeze audit by exact hash:

```text
result_id:
  COMPENSATOR_ACTIVE_CLOCK_PX2_INDEPENDENT_FREEZE_AUDIT_V1
sha256:
  9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533
science_commit:
  f64be4a5793764ebf8871d5f1a83bd736aed7fc1
lifecycle_commit:
  0b21bfe86eb97a0e0723d85d8c3a336fd1d5ac20
```

The imported theorem fixes the complete declared coefficient basis

\[
(\alpha_B,\alpha_R,M_P^2,p_0,p_1,p_2)
\]

and the audited base point

\[
(\kappa,q,\nu)=\left(1,\frac9{40},\frac34\right).
\]

No unaudited candidate action is used.

## Parameterized stationary evaluation

The cylinder rows are

\[
\begin{pmatrix}
0&36\kappa^2&3\kappa&1&0&0\\
0&12\kappa^2&-\kappa&-1&0&0
\end{pmatrix}.
\]

At Berger horizontal scale \(a=1\),

\[
\operatorname{Ric}_{\hat a\hat b}
=\operatorname{diag}\left(
0,\frac{2-q}{2},\frac{2-q}{2},\frac q2
\right),
\qquad
R=\frac{4-q}{2},
\]

\[
B_{\hat a\hat b}
=\operatorname{diag}\left(
\frac{(1-q)^2}{6},
\frac{(1-q)(1-3q)}{6},
\frac{(1-q)(1-3q)}{6},
\frac{(1-q)(5q-1)}{6}
\right).
\]

With \(X=-\nu^2\), the three independent matter columns are

\[
(1,\nu^2,-3\nu^4)
\]

in the time row and

\[
(-1,\nu^2,-\nu^4)
\]

in both spatial rows.  These give a \(5\times6\) polynomial stationary
matrix.

Define

\[
A=4q-1,\quad
F=q+12\kappa-4,\quad
J=16q\kappa-q-4\kappa,\quad
H=32q\kappa-3q-8\kappa.
\]

The exact kernel generator is

\[
K(\kappa,q,\nu)=
\begin{pmatrix}
8\nu^4F\\[1mm]
-\frac43\nu^4A\\
32\kappa\nu^4A\\
-48\kappa^2\nu^4A\\
-8\kappa\nu^2AF\\
-FJ
\end{pmatrix}.
\]

Hence every rank-five stationary action is

\[
(\alpha_B,\alpha_R,M_P^2,p_0,p_1,p_2)
=\lambda K(\kappa,q,\nu).
\]

Direct substitution gives \(M_{\rm stat}K=0\).  The six signed maximal
cofactors are

\[
\kappa\nu^2(q-1)K_i.
\]

At the frozen point, normalizing the last component to one gives

\[
\left(
\frac{81}{20},\frac{27}{3290},-\frac{324}{1645},
\frac{486}{1645},\frac{18}{25},1
\right),
\]

exactly reproducing the independently frozen ray.

## Rank-change and principal strata

The stationary rank drops precisely on

\[
\{\kappa=0\}\cup\{\nu=0\}\cup\{q=1\}
\cup\{4q-1=0,\ q+12\kappa-4=0\}.
\]

The last component \(p_2=-\lambda FJ\) may vanish at \(J=0\), but \(J=0\)
alone does not lower stationary rank.

This rank variety must not be confused with the nearer principal
discriminant

\[
\lambda\kappa\nu(4q-1)(q+12\kappa-4)=0.
\]

The entire box \(\mathcal N\) avoids both varieties.

## Coupled scalar operator and velocity inertia

On the nonzero auxiliary stratum, the homogeneous quadratic density is

\[
L_{\rm hom}
=-3D\psi\,Du-6\kappa\psi u
+\frac{6}{M_P^2}\psi^2-p_1(Dv)^2.
\]

Its Euler Hessian is

\[
\begin{pmatrix}
0&3(D^2-2\kappa)&0\\
3(D^2-2\kappa)&12/M_P^2&0\\
0&0&2p_1D^2
\end{pmatrix},
\]

with determinant

\[
-18p_1D^2(D^2-2\kappa)^2.
\]

The exact congruence

\[
C=
\begin{pmatrix}
1&1&0\\
1&-1&0\\
0&0&1
\end{pmatrix}
\]

takes the velocity Hessian to

\[
C^TH_{\rm vel}C=\operatorname{diag}(-6,6,-2p_1).
\]

Therefore the gravity--auxiliary pair is split for every nonzero stationary
action throughout \(\mathcal N\), independently of the clock sign.

The six-dimensional first-order evolution has

\[
\chi(\zeta)=m(\zeta)
=\zeta^2(\zeta^2-2\kappa)^2
\]

on the declared box.  The only root-collision surface in this parameterized
homogeneous evolution is \(\kappa=0\), outside \(\mathcal N\).

The raw-\(D\) Hamiltonian is

\[
H_D=-3DuD\psi+6\kappa\psi u
-\frac{6}{M_P^2}\psi^2-p_1(Dv)^2.
\]

The two field configurations

\[
(u,Du,\psi,D\psi,v,Dv)=(0,1,0,-1,0,0)
\]

and

\[
(u,Du,\psi,D\psi,v,Dv)=(0,1,0,1,0,0)
\]

give \(+3\) and \(-3\), respectively.  These witnesses are independent of
\((\kappa,q,\nu,\lambda)\).

## Sound cone, charge and relational clock

On the stationary ray,

\[
p_1=-8\lambda\kappa\nu^2AF,
\]

\[
P_X=-2\lambda q\nu^2F,
\]

\[
P_X+2XP_{XX}=2\lambda\nu^2FH,
\]

and

\[
c_s^2=-\frac qH.
\]

The charge densities are

\[
Q_R=4\lambda\nu^3qF,
\]

\[
\rho_D
=-\lambda\nu^4
\left(
16\kappa q^2-104\kappa q+16\kappa-3q^2+12q
\right),
\]

\[
\rho_K=-P.
\]

The exact generator identities retain the scoped form

\[
K_{\rm Berger}=D-\nu R,\qquad
\iota_D\Omega_{\rm total}=\nu\,\delta Q_R,\qquad
\iota_{K_{\rm Berger}}\Omega_{\rm total}=0.
\]

On \(\mathcal N\),

\[
A<0,\qquad F>\frac{149}{20}>0,\qquad
J<-\frac15<0,\qquad H<-\frac35<0.
\]

Moreover,

\[
-H-q=\kappa(8-32q)+2q>0,
\]

so \(0<c_s^2<1\).  Exact monotonicity bounds also give positive \(P/\lambda\)
and positive \(\rho_D/\lambda\).

Consequently:

* \(\lambda>0\): the Berger clock is timelike, monotone, charged,
  positive-energy, standard-sign, hyperbolic and subluminal, but the cylinder
  clock has the wrong sign;
* \(\lambda<0\): the cylinder clock has the standard sign, but the Berger
  clock has the wrong standard sign and reversed energy/charge orientation;
* \(\lambda=0\): the action is zero and has no principal operator or pairing.

The clock-health intersection is empty throughout \(\mathcal N\).  This is
independent of the already decisive split gravity--auxiliary inertia.

## First explicit bifurcation

Along

\[
\kappa=1,\qquad \nu=\frac34,\qquad \lambda=1,
\]

the first boundary of the declared box is

\[
\boxed{q=\frac14}.
\]

At that surface,

\[
\alpha_R=M_P^2=p_0=p_1=0,
\]

so the cylinder clock and the \(R^2\) auxiliary presentation degenerate.
The stationary matrix nevertheless still has rank five at \(\kappa=1\).

The exact below-surface witness \(q=9/40\) gives

\[
(p_1,P_X,P_X+2XP_{XX})
=\left(
\frac{2961}{800},
-\frac{26649}{12800},
-\frac{174699}{12800}
\right).
\]

The exact above-surface witness \(q=21/80\) gives

\[
(p_1,P_X,P_X+2XP_{XX})
=\left(
-\frac{5949}{3200},
-\frac{124929}{51200},
-\frac{184419}{51200}
\right).
\]

Thus crossing \(q=1/4\) repairs the two-background clock-sign conflict for
\(\lambda>0\).  It does not repair the split gravity--auxiliary velocity pair
or the raw-\(D\) both-sign witnesses, so the full seven-gate good locus remains
empty on both sides.  Stationary rank changes on this surface only at the
separate intersection \(\kappa=5/16\).

## Seven-gate disposition

| Gate | Exact neighbourhood status |
| --- | --- |
| 1. action-derived classical data | action-level pass |
| 2. dressed-trace disposition | physical auxiliary replacement for \(\lambda\ne0\) |
| 3. complete support-local causal parent | not reached after gate 5 |
| 4. reduced current/pairing | nondegenerate but split |
| 5. physical sign | structurally stable fail |
| 6. raw \(D\) | structurally stable fail |
| 7. Berger clock | stationary and monotone; healthy only for \(\lambda>0\) |

No `Candidate C_active` is selected.

## Claim boundary

This result is exact and uses no sampled scan or implicit-function argument.
It is scoped to the displayed cylinder/Berger algebraic family and the frozen
quadratic shift-symmetric \(P(X)\) action class.  It does not cover a fixed
action across the neighbourhood, general backgrounds, higher \(P(X)\), higher
derivatives, fixed-charge quotients, new fields or enlarged gauge groups.

It constructs no complete support-local causal parent and establishes no
Hadamard, anomaly/QME, particle, scattering, positivity or unitarity result.

## Reproduction

```bash
python3 d_quotient_classical/compensator/active_clock_background_stability.py --check
python3 d_quotient_classical/compensator/verify_active_clock_background_stability.py
python3 -m unittest \
  d_quotient_classical.compensator.tests.test_active_clock_background_stability -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-active-clock-background-stability-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json
```

CLOSE-OUT: DONE — the independently frozen quadratic active-clock action-space
no-go persists on an exact open cylinder/Berger neighbourhood, and the first
clock/principal bifurcation has exact witnesses on both sides.

EVIDENCE: `d_quotient_classical/receipts/COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1_TIER_RECEIPT.json`
