# BT Euclidean pair-block response: connected order-\(\lambda^4\) ledger

**Dependency boundary:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_CONNECTED_LEDGER_V1`

## Result

The complete order-\(\lambda^4\) pair-response problem can be reduced before
any large lattice sum is attempted. There are exactly seven normalized
outer-cumulant terms, and every surviving free-background Wick graph has at
most two freely summed momenta. A three-loop calculation is not part of this
coefficient.

This matters computationally as well as mathematically. The next calculation
should stream a finite list of connected zero-, one-, and two-loop topologies.
It should not form a dense full-volume covariance tensor or enumerate
disconnected vacuum graphs. That is the OOM-safe formulation of the next
gate.

The result does **not** compute the full-Gibbs order-\(\lambda^4\) coefficient.
It classifies and reduces that calculation exactly.

## 1. Action through fourth order

Write the scaled interaction as

\[
 S_\lambda=S_0+\lambda S_1+\lambda^2S_2
 +\lambda^3S_3+\lambda^4S_4+O(\lambda^5).
\]

For the directed edge differences at a site, define

\[
 A=\sum d,\quad B=\sum d^2,\quad C=\sum d^3,
 \quad D=\sum d^4,\quad E=\sum d^5.
\]

Exact expansion of the BT exponential interaction gives

\[
\begin{aligned}
 S_1&={1\over2}\sum AB,\\
 S_2&=\sum\left({B^2\over8}+{AC\over6}\right),\\
 S_3&=\sum\left({BC\over12}+{AD\over24}\right),\\
 S_4&=\sum\left({C^2\over72}+{BD\over48}+{AE\over120}\right).
\end{aligned}
\]

Only sixteen residual sites depend on the chosen nearest-neighbour pair.
Terms independent of both pair variables are removed before conditional
normalization, exactly as in the certified one-loop calculation.

## 2. Conditional normalization is a cumulant

Let \(U_j\) denote the pair-dependent part of \(S_j\), and let
\(\kappa_u\) be the cumulant under the exact free conditional pair Gaussian.
The conditional center has the universal expansion

\[
 m_n=\sum_{\sum_jjk_j=n}
 {(-1)^K\over\prod_j k_j!}\,
 \kappa_u\!\left(u,U_1^{[k_1]},\ldots,U_n^{[k_n]}\right),
 \qquad K=\sum_jk_j.
\]

In particular,

\[
\begin{aligned}
 m_1={}&-\kappa_u(u,U_1),\\
 m_2={}&-\kappa_u(u,U_2)+\tfrac12\kappa_u(u,U_1,U_1),\\
 m_3={}&-\kappa_u(u,U_3)+\kappa_u(u,U_1,U_2)
          -\tfrac16\kappa_u(u,U_1,U_1,U_1),\\
 m_4={}&-\kappa_u(u,U_4)+\kappa_u(u,U_1,U_3)
          +\tfrac12\kappa_u(u,U_2,U_2)\\
       &-\tfrac12\kappa_u(u,U_1,U_1,U_2)
          +\tfrac1{24}\kappa_u(u,U_1,U_1,U_1,U_1).
\end{aligned}
\]

This is the first normalization layer. It prevents a disconnected
conditional partition function from entering as an independently estimated
term.

## 3. The full-Gibbs coefficient has seven connected terms

Let \(D\) be the axial quadratic response derivative and \(\kappa_0\) the
free-background cumulant. The fully normalized fourth-order coefficient is

\[
\begin{aligned}
 T_4={}&\mathbb E_0[Dm_4]-\kappa_0(Dm_3,S_1)
 -\kappa_0(Dm_2,S_2)+\tfrac12\kappa_0(Dm_2,S_1,S_1)\\
 &-\kappa_0(Dm_1,S_3)+\kappa_0(Dm_1,S_1,S_2)
 -\tfrac16\kappa_0(Dm_1,S_1,S_1,S_1).
\end{aligned}
\]

Equivalently, before conversion to joint cumulants,

\[
 T_4=\mathbb E_0[Dm_4]+\mathbb E_0[Dm_3W_1]
 +\mathbb E_0[Dm_2W_2]+\mathbb E_0[Dm_1W_3]-Z_2T_2,
\]

where

\[
 W_1=-S_1,\qquad W_2={S_1^2\over2}-S_2,
 \qquad W_3=-S_3+S_1S_2-{S_1^3\over6},
 \qquad Z_2=\mathbb E_0[W_2].
\]

The cumulant form is the useful one: every Wick component disconnected from
the response insertion has already canceled. Taking absolute values before
this cancellation would recreate the same normalization problem encountered
in the earlier complete-\(g^4\) work.

## 4. Why two loops are enough

Consider a conditional term of coupling order \(i\) containing \(r\)
interaction vertices. Before the response derivative its total field degree
is

\[
 1+i+2r.
\]

The connected conditional cumulant includes the observed pair field as one
vertex. Connecting it to all \(r\) interaction vertices requires at least
\(r\) innovation edges, hence at least \(2r\) innovation legs. After the
response derivative, the resulting composite insertion satisfies

\[
 \deg_{\rm background}(Dm_i)\leq i.
\]

Now take an outer term with \(s\) marginal action vertices whose coupling
orders sum to \(4-i\). Its maximal background degree is

\[
 i+(4-i)+2s=4+2s.
\]

A Wick graph therefore has at most \(E=s+2\) edges. The joint cumulant makes
the graph connected on \(V=s+1\) composite vertices, so

\[
 \beta=E-V+1\leq(s+2)-(s+1)+1=2.
\]

The certificate enumerates all integer partitions in both normalization
layers and checks this count row by row. Momentum conservation or additional
innovation contractions can lower the rank of an individual row; none can
raise it above two.

## 5. Exact zero-background checkpoint

As a local algebra check, set every external field to zero and integrate only
the two internal pair variables with covariance

\[
 C_B=\begin{pmatrix}9/616&1/308\\1/308&9/616\end{pmatrix}.
\]

Direct exact expansion of the normalized bivariate Gaussian ratio gives

\[
\begin{array}{c|cc}
 &\lambda^2&\lambda^4\\ \hline
\text{longitudinal}
&-7349/379456&297291527/329112813568\\
\text{transverse}
&-7979/379456&342682355/329112813568
\end{array}
\]

After the pair-orientation weighting,

\[
 b_{\rm pair,vac}(\lambda)
 =-{15643\over1517824}\lambda^2
 +{41416831\over82278203392}\lambda^4+O(\lambda^6).
\]

The fourth-order local term is positive, but the \(\lambda^2+\lambda^4\)
truncation remains negative at \(\lambda=2/5\). This does not predict the
full-Gibbs sign: the predecessor theorem proved that free-background
annealing reverses the local sign already at one loop. The checkpoint instead
confirms that the background terms are again indispensable at fourth order.

## 6. What is established and what remains

Established:

- the complete conditional-center expansion through order \(\lambda^4\);
- the complete seven-term full-Gibbs connected-normalization ledger;
- cancellation of all disconnected vacuum normalization components before
  estimation;
- a maximum of two freely summed background momenta;
- the exact zero-background \(\lambda^4\) coefficient and its limited scope.

Open:

- the full-Gibbs finite-volume \(\lambda^4\) coefficient and sign;
- its large-volume power or logarithm;
- a volume-uniform remainder or a nonperturbative result at \(\lambda=2/5\);
- the response-to-Witten bridge and the actual interacting \(H^{-1}\) shell
  sum.

No continuum measure, Born rule, Krein reconstruction, new physical
dimension, or Lorentzian-causal result follows from this calculation.

## 7. Next calculation

Generate the seven connected rows directly in Fourier space, retaining both
pair orientations and the conditioned-covariance rank corrections. Start
with an exact rational \(L=4\) evaluation streamed topology by topology. If
the coefficient is nonzero, split its two-loop symbol into hard/hard,
hard/soft, and soft/soft momentum regions and decide the large-volume power
or logarithm. This is the shortest controlled route from the positive
one-loop result toward a volume-uniform response estimate.
