# BT global connected finite-time packet column

Certificate:
`REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The apparent soft singularities `q_B=0` do not obstruct the actual connected
order-`lambda^4` BT packet column at fixed finite time. All nine exchange
channel kernels are globally Hilbert--Schmidt on the complete labeled
massless three-body phase-space product. The hard tenth channel is bounded
trivially.

Consequently the common compact regular cutoff used in the predecessor can
be removed. The actual unit-weight connected tree amplitude

\[
 A_{\rm full}=16\lambda^4\sum_{B=0}^{9}K_{B,T}\otimes R_B
\]

obeys the exact sufficient bound

\[
 \boxed{\|A_{\rm full}\|^2\le
 \frac{1539}{400\pi^6}\lambda^8T^2.}
\]

It therefore defines a global positive finite-time click effect
`A_full^* A_full`, with a positive operational complement whenever the
displayed upper bound is at most one.

This closes the momentum-domain gate for the complete *connected* leading
column. Disconnected spectator compositions, the matching forward
coefficient, all-time scattering, and general Eq. (19) remain open.

## Exchange-channel geometry

Write the fixed center-of-momentum vector as

\[
 P=(M,\mathbf0),\qquad M=\frac{16}{5}.
\]

Every one-particle energy in labeled massless three-body phase space lies in
`[0,M/2]`. The ten unordered channels comprise the hard channel `q_0=P` and
nine mixed channels. Each mixed channel can be oriented as

\[
 q_{ia}=P-p_i-k_a,
\]

where `p_i` is one incoming spectator and `k_a` one outgoing spectator.
Writing their energies as `E` and `K`,

\[
 q_{ia}^0=M-E-K\ge0.
\]

Therefore `q_ia=0` is possible precisely when

\[
 E=K=M/2,
 \qquad \widehat{\mathbf k}=-\widehat{\mathbf p}.
\]

This is the simultaneous double-collinear boundary: the other two incoming
particles sum to `k_a`, and the other two outgoing particles sum to `p_i`.

Choose the incoming direction to be `+z` and use the antipodal local chart

\[
 m(s,t)=\frac{(2s,2t,s^2+t^2-1)}{1+s^2+t^2}
\]

for the outgoing direction. At the zero, the derivative of
`(q^0,q^z,q^x,q^y)` with respect to `(E,K,s,t)` is

\[
 \begin{pmatrix}
 -1&-1&0&0\\
 -1& 1&0&0\\
 0&0&-M&0\\
 0&0&0&-M
 \end{pmatrix},
 \qquad
 \det=-2M^2=-\frac{512}{25}.
\]

Thus the spectator map has four transverse directions at the apparent zero.
Since `D=q^0+|q|` dominates the Euclidean four-radius and
`|F_T(delta)|<=T`, the squared kernel behaves at worst as `r^-2` against
`d^4q`. Its local radial behavior is `r dr`, which is integrable.

The exact global calculation below is stronger than this local power count.

## Exact recursive phase measure

The standard invariant three-body phase measure factors as

\[
 d\Phi_3(P)=\frac{ds}{2\pi}
 d\Phi_2(P;p,Q)d\Phi_2(Q;r_1,r_2),
 \qquad s=(P-p)^2=M^2-2ME.
\]

For massless daughters,

\[
 d\Phi_2(P;p,Q)=\frac{M^2-s}{32\pi^2M^2}d\Omega,
 \qquad
 d\Phi_2(Q;r_1,r_2)=\frac{d\Omega_*}{32\pi^2}.
\]

Using `ds=-2M dE` gives

\[
 d\Phi_3(P)=
 \frac{E\,dE\,d\Omega\,d\Omega_*}{512\pi^5}.
\]

After integrating the internal two-body direction,

\[
 d\nu(p)=\frac{E\,dE\,d\Omega}{128\pi^4}.
\]

The total volume is recovered exactly:

\[
 \Phi_3(P)=\frac{M^2}{256\pi^3}
 =\frac{1}{25\pi^3}.
\]

This is the same labeled measure certified previously from the independent
five-dimensional energy--orientation chart.

## Exact exchange integral

Set

\[
 e=E/M,\qquad k=K/M,\qquad
 c=\widehat{\mathbf p}\mathbin\cdot\widehat{\mathbf k}.
\]

Then `0<=e,k<=1/2`, `-1<=c<=1`, and

\[
 \frac{D}{M}=1-e-k+\sqrt{e^2+k^2+2ekc}.
\]

Rotational invariance gives

\[
 \int d\Omega_p\,d\Omega_k\,f(c)
 =8\pi^2\int_{-1}^{1}f(c)\,dc.
\]

Put `r=sqrt(e^2+k^2+2ekc)`. Since `dc=r dr/(ek)`, direct integration yields

\[
 \int_{-1}^{1}\frac{dc}{(D/M)^2}
 =\frac1{ek}\left[
 \log\frac1{1-2\min(e,k)}+(1-e-k)
 -\frac{1-e-k}{1-2\min(e,k)}
 \right].
\]

On the half-domain `e>=k`, integrating first over `e` leaves

\[
 \frac32k^2-\frac34k+left(k-\frac12\right)\log(1-2k).
\]

The polynomial part integrates to `-1/32`. With `x=1-2k`, the logarithmic
part is fixed by

\[
 \int_0^1x\log x\,dx=-\frac14
\]

and contributes `1/16`. Hence the half-domain is `1/32`; exchange symmetry
doubles it to

\[
 \boxed{\frac1{16}}.
\]

Restoring the angular and phase-measure factors gives, for each exchange
channel,

\[
 \int_{\Phi_3\times\Phi_3}\frac{d\Phi_3(x)d\Phi_3(y)}{D_B^2}
 =\frac{M^2}{32768\pi^6}
 =\frac1{3200\pi^6}.
\]

The logarithm in the intermediate angular primitive is integrable. It is not
an infrared divergence.

For the hard channel, `D_0=M`, so

\[
 \int\frac{d\Phi_3(x)d\Phi_3(y)}{D_0^2}
 =\frac{\Phi_3(P)^2}{M^2}
 =\frac1{6400\pi^6}.
\]

## Global ten-channel operator

Define each finite-time kernel on the full phase-space product by

\[
 \beta_{B,T}(y,x)=\frac{F_T(\delta_B(y,x))}{D_B(y,x)},
 \qquad
 F_T(\delta)=\int_0^T e^{i\delta\tau}\,d\tau.
\]

Its value on the measure-zero set `q_B=0` is irrelevant to the resulting
`L2` equivalence class. Since `|F_T|<=T`, the preceding integrals imply

\[
 \sum_{B=0}^{9}\|K_{B,T}\|_{\rm HS}^2
 \le \frac{19T^2}{6400\pi^6}.
\]

For the exact ten-residue interference Gram,

\[
 \lambda_{\max}(H)=\frac{81}{16}.
\]

The tree multiplier is `16 lambda^4`, hence

\[
 \begin{split}
 \|A_{\rm full}\|^2
 &\le\|A_{\rm full}\|_{\rm HS}^2\\
 &\le256\lambda^8\frac{81}{16}
 \frac{19T^2}{6400\pi^6}\\
 &=\frac{1539}{400\pi^6}\lambda^8T^2.
 \end{split}
\]

Thus

\[
 E_{\rm click}=A_{\rm full}^*A_{\rm full},\qquad
 E_{\rm no}=I-E_{\rm click}
\]

are positive and sum to the identity whenever

\[
 \frac{1539}{400\pi^6}\lambda^8T^2\le1.
\]

## Declared scalar source

The hard residue annihilates the declared positive-even scalar species
vector. For a normalized momentum packet `F`,

\[
 q_{\rm click}=16\lambda^8
 \left\|\sum_{B=1}^{9}K_{B,T}F\right\|^2.
\]

Cauchy--Schwarz across the nine exchange channels gives the global bound

\[
 \boxed{q_{\rm click}\le
 \frac{81}{200\pi^6}\lambda^8T^2.}
\]

This is a globally defined connected finite-time physical-scalar packet
coefficient. It is not yet the probability of the complete three-particle
evolution because disconnected spectator terms have not been added.

## What is now closed and what remains

For the connected order-`lambda^4` column, all three codomain questions are
now closed:

- particle number: only `3 -> 3` occurs;
- species: the positive-even source remains in the positive-even four-plane;
- momentum domain: the full fixed-`P` phase space is allowed, including
  `q_B=0` in the Hilbert--Schmidt sense.

The next gate is no longer an infrared regularization problem. It is the
disconnected spectator completion: lower connected blocks tensored with
identity spectators must be assembled on the same finite-time domain. Only
then can the full order-`lambda^4` output column be compared with the
order-`lambda^8` forward cut or an exhaustive normalization identity.

General Eq. (19) remains a different problem. The result does not construct
the standard scalar projector, a fixed-vacuum trace, an all-time operator,
loops/KLN completion, gravity, BV/BRST transfer, or anything
`LORENTZIAN-CAUSAL`.

## Verification receipts

The producer, independent verifier, and mutation suite run sequentially under
`ulimit -v 500000` with Python
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`:

- producer: `25/25`, pass, `0.02 s`, `16216 KB` maximum RSS;
- independent verifier: `25/25`, pass, `0.07 s`, `23316 KB` maximum RSS;
- twelve tests, including eleven decisive mutations: pass, `0.09 s`,
  `24468 KB` maximum RSS.

Papers 5 and 6 compiled twice with `pdflatex -interaction=nonstopmode
-halt-on-error` under the same memory cap. Their final passes took `0.52 s`
and `0.53 s`, at `50752 KB` and `50824 KB` maximum RSS; no new overfull boxes
were introduced. The append-only planning fold imported `1491` nodes with
zero invalid items and zero malformed events in `7.89 s` at `207280 KB`
maximum RSS.

Tier 0 covers Python/JSON parsing, TeX compilation, staged-diff inspection,
and `git diff --check`. Tier 1 is the scoped producer, independent verifier,
and mutation suite. The mathematical inputs are unchanged and content-pinned,
which supplies the affected Tier-2 gate. Tier 3 is not required because this
is a reduced-mode finite-time coefficient theorem, not a freeze, shared-core
change, QME promotion, or Lorentzian theorem.

CLOSE-OUT: DONE — the exact certificate, independent rail, mutation suite,
Papers 5/6, and append-only planning transition establish the global
connected finite-time column; disconnected completion remains the next gate.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_GLOBAL_CONNECTED_FINITE_TIME_PACKET_COLUMN_V1.json`
