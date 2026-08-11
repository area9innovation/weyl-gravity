# BT finite-detector pushforward and the soft trace ideal

**Result:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The first zero-mode-completed nonlinear detector sector can be transported on
the semifinite BT carrier at every finite soft cutoff.  The construction uses
the dynamically derived number-lowering kernel, its unique orbit dressing,
the weighted cross-Krein squeeze, and the conditional semifinite trace.  It
produces an exact finite-rank projector coefficient through the order needed
to test idempotence.

The soft-cutoff limit is different.  Its algebraic trace cancels between the
hard and two-daughter blocks, but its positive trace norm diverges.  Thus the
semifinite architecture solves the finite-detector domain problem without
supplying a trace-class continuum limit.  A hard matching cancellation or an
explicitly local non-normal renormalized weight remains necessary.

This is a sector preflight, not the deferred full Eq. (19) pushforward.  The
public map still omits oscillator sectors that could alter the full answer.

## 1. A logarithmic-cell detector

The certified neutral soft normalization assigns the conditional squared
amplitude

\[
 a^2=\frac1{48},\qquad a=\frac{\sqrt3}{12}
\]

to one unordered-pair logarithmic cell.  Take one hard parent vector \(h\) and
\(N\) mutually orthogonal two-daughter detector vectors \(d_i\).  On this
finite carrier define

\[
 Kh=a\sum_{i=1}^N d_i,\qquad Kd_i=-ah.
\]

Then \(K^*=-K\).  For \(P_0=|h\rangle\langle h|\), the transported projection
has the exact expansion

\[
 e^{\lambda K}P_0e^{-\lambda K}
 =P_0+\lambda P_1+\lambda^2P_2+O(\lambda^3),
\]

where the order-\(\lambda\) triangle and idempotence-forced box are

\[
 P_1=a\sum_i\left(
 |d_i\rangle\langle h|+|h\rangle\langle d_i|
 \right),
\]

\[
 P_2=a^2\sum_{i,j}|d_i\rangle\langle d_j|
      -Na^2|h\rangle\langle h|.
\]

Exact \(\mathbb Q(\sqrt3)\) arithmetic verifies

\[
 P_0^2=P_0,
\]

\[
 P_0P_1+P_1P_0=P_1,
\]

\[
 P_0P_2+P_2P_0+P_1^2=P_2.
\]

The last identity is the load-bearing normalization test: the negative hard
coefficient is not fitted.  Projector idempotence forces it.

## 2. Zero-mode completion changes the charge disposition

The two logarithmic contractions have fixed-vacuum generator charges

\[
 (+1,-1),\qquad(-1,+1).
\]

The predecessor's unique covariant orbit powers are respectively

\[
 (-1,+1),\qquad(+1,-1).
\]

Both completed pairs therefore have charge \((0,0)\), and their orbit powers
cancel in the Gram.  The covariantly completed squeeze generator is neutral as
well.  Consequently \(P_0,P_1,P_2\) in this certified sector are neutral.  Its
strictly negative Eq. (19)-type radical is zero.

That statement is deliberately local to the available two-annihilator
kernel.  It does not classify the omitted oscillatory, number-preserving, or
full dynamical-zero-mode terms.  In particular it does not prove that the
radical of the complete pushforward is zero.

## 3. Finite cutoff survives the weighted squeeze

For every finite \(N\), the three coefficient operators above have finite
rank.  The weighted squeeze maps their finitely many defining vectors from the
polynomial core into the paired Gaussian image core.  Similarity therefore
keeps the coefficients finite rank and inside the finite part of the
semifinite paired ideal.

An exact one-pair fixture tests more than rank counting.  With \(z=1/2\), put
\(x=z^2=1/4\).  The positive norm of the squeezed local vacuum is

\[
 N_0=\sum_{n\ge0}x^n=\frac1{1-x}=\frac43.
\]

For a pair-excited detector vector the creation series carries coefficient
\(n+1\), hence

\[
 N_1=\sum_{n\ge0}(n+1)^2x^n
 =\frac{1+x}{(1-x)^3}=\frac{80}{27}.
\]

The one-cell positive trace sizes become

\[
 \|SP_1S^{-1}\|_1^2
 =4a^2N_0N_1=\frac{80}{243},
\]

\[
 \|SP_2S^{-1}\|_1
 =a^2(N_0+N_1)=\frac{29}{324}.
\]

They are finite, as required, and larger than their unsqueezed values.  The
explicit squeeze does not remove the soft carrier.

## 4. The exact continuum obstruction

For \(N\) logarithmic cells,

\[
 \operatorname{Tr}(P_1)=0,
\]

and

\[
 \operatorname{Tr}(P_{2,\mathrm{hard}})=-\frac{N}{48},
 \qquad
 \operatorname{Tr}(P_{2,\mathrm{soft}})=+\frac{N}{48}.
\]

Thus \(\operatorname{Tr}(P_2)=0\) exactly.  But the positive trace ideal sees
absolute size rather than signed cancellation.  The two nonzero singular
values of \(P_1\) are both \(\sqrt{N/48}\), while the nonzero eigenvalues of
\(P_2\) are \(\pm N/48\).  Therefore

\[
 \boxed{\|P_1\|_1^2=\frac{N}{12}},
 \qquad
 \boxed{\|P_2\|_1=\frac{N}{24}}.
\]

Removal of the soft cutoff corresponds to admitting arbitrarily many equal
units of the measured \(dr/r\) logarithm, so \(N\to\infty\).  Neither
coefficient has a uniform \(L^1\) limit.  A zero algebraic trace is therefore
not a trace-class certificate.

This is the first exact obstruction after the finite-detector semifinite
construction.  It is narrower than a no-go for Eq. (19): a missing sector of
the full pushforward could cancel the logarithmic carrier on the same operator
domain.  If no such cancellation exists, the remaining alternative is a
local non-normal renormalized weight that treats the paired hard and soft
operator before the cutoff is removed.

## 5. Claim boundary and next calculation

Established exactly:

- the finite-log-cell triangle and idempotence-forced hard/soft box;
- projector idempotence through order \(\lambda^2\);
- neutrality, and zero strict negative radical, of this zero-mode-completed
  sector;
- finite-cutoff membership in the semifinite paired ideal after the explicit
  weighted squeeze;
- failure of a uniform positive trace-class soft limit in this sector.

Not established:

- the omitted order-\(\lambda\) oscillator sectors or the full nonlinear
  \(R_tP_2R_t^\dagger\);
- a cancellation of the neutral logarithmic carrier by hard matching;
- a positive local non-normal thermodynamic weight;
- Eq. (19), the physical \(1/48\), or a complete NLO probability;
- a gravitational/BRST lift or anything `LORENTZIAN-CAUSAL`.

The next decisive calculation is to place the paired operator
\(P_{2,\mathrm{soft}}+P_{2,\mathrm{hard}}\) in a candidate local renormalized
weight and test positivity and cutoff independence.  Before that construction
is promoted, the missing oscillator sectors should be derived far enough to
exclude or exhibit an operator-level cancellation of \(P_1\).

## 6. Verification receipt

All scientific commands run sequentially under a 500,000 KB virtual-memory
cap.

- Python parse/compile: PASS in 0.08 s (16,296 KB peak RSS).
- Exact producer replay: PASS 25/25 in 0.25 s (20,664 KB peak RSS).
- Independent strict-schema, \(\mathbb Q(\sqrt3)\) matrix, charge-import,
  squeeze-sum, trace-spectrum, provenance, event-hash, and claim verifier:
  PASS 15/15 in 0.31 s (30,236 KB peak RSS).
- Producer, verifier, and eight decisive mutations: PASS 10/10 in 2.54 s
  (30,448 KB peak RSS).  The mutations changed the per-cell coefficient,
  projector box, trace norm, completed charge, squeeze norm, soft-limit
  disposition, Eq. (19) status, and physical coefficient; every mutation was
  rejected.
- Papers V and VI: PASS, two `pdflatex` passes each.  Paper V took 0.89 s per
  pass (50,276 and 50,536 KB); Paper VI took 1.01 and 0.98 s (50,492 and
  50,272 KB).
- Higher tiers are not required because no shared algebra, freeze, release, or
  theorem lifecycle promotion changes; the affected reduced-mode certificate
  chain is checked by pinned hashes and the scoped independent rail.

The Science Forge close-out uses the manual append-only `event-v0` fallback.
The external coordinator compiler remains unavailable at its previously
recorded Forge source error, so no successful coordinator run is claimed.
