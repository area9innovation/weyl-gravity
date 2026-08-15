# BT complete-$g^4$ lower-loop bounds

Certificate: `REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_LOWER_LOOP_BOUNDS_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

Lifecycle: `COMPLETE_M4_LEADING_POWER_DECIDED_INTERACTING_H_MINUS_ONE_OPEN`.

## Result

The missing conditioned lower-loop sectors cannot cancel the certified
negative two-loop power coefficient. For every integer $L\ge7$, exact affine
enumeration reduces the zero-loop sector to ten rows and the one-loop sector
to twenty-seven rows after ten further one-loop integrands cancel exactly.

The zero-loop sum is

$$
 M_{4,0}(L)=L^{-4}Z(\omega_p),
$$

where

$$
 Z(w)=\frac{17w^7-170w^6+561w^5-780w^4-840w^3
 +16128w^2-57456w+63936}
 {32w^2(4-w)(3-w)^2}.
$$

Consequently

$$
 \lim_{L\to\infty}M_{4,0}(L)=\frac{111}{32\pi^4}>0.
$$

The full one-loop sector obeys the explicit bound

$$
 |M_{4,1}(L)|\le
 \frac{900315}{4}\pi^2\bigl(1+\log\lfloor L/2\rfloor\bigr).
$$

Thus $M_{4,0}=O(1)$ and $M_{4,1}=O(\log L)$, while
$N\omega_p\asymp L^2$. Both lower-loop sectors are
$o(N\omega_p)$. Together with the two-loop certificate
$c_4+c_7<0$, this proves that the complete perturbative coefficient $M_4$
has a strictly negative leading $N\omega_p$ coefficient.

This is not a theorem about the sign of the resummed interacting moment. It
does not establish uniformity of the perturbation series at the tuned
coupling, a nonperturbative score estimate, or the actual interacting
$H^{-1}$ second moment.

## Affine atlas and corrected volume scope

The exhaustive generator considers every connected monomial, pairing
topology, bulk/rank covariance choice, and signed external orientation. Its
exact statistics are:

- rank zero: 432,256 candidate orientations, 4,120 source-conserving, 3,272
  killed by a zero bulk momentum, and 848 contributions combining to ten
  rows;
- rank one: 110,112 candidates, 1,104 source-conserving, 750 killed by a zero
  bulk momentum, and 354 contributions combining to 37 rows, ten of which
  cancel exactly.

The maximum absolute component source is six in rank zero and five in rank
one. Therefore integer source conservation is equivalent to modular source
conservation for $L\ge7$. The earlier scratch assumption $L\ge5$ was rejected
before certification.

## Exact zero-loop recombination

Put $t=e^{2\pi i/L}$ and $w=2-t-t^{-1}$. The producer reconstructs every
directed-edge block and every $K_3,K_4,K_5$ partition from the ten atlas rows
using rational Laurent polynomials. Cross multiplication gives the displayed
$Z(w)$ exactly. Since $w\to0$ and

$$
 \lim_{w\to0}w^2Z(w)=\frac{111}{2},\qquad
 L^4w^2\longrightarrow16\pi^4,
$$

the finite positive limit follows. For $L\ge7$, $0<w<1$; a deliberately
coarse numerator lower bound is

$$
 63936-57456-840-780-170=4690>0,
$$

so the zero-loop term is positive throughout the certified range.

An earlier binary64 preflight appeared to show decay near $L^{-16}$. That was
catastrophic cancellation among terms individually carrying fourth-order
soft poles. It is not evidence and is superseded by the exact identity.

## One-loop soft allocation

The standard exact vertex bounds are

$$
 |K_3(a,b,c)|\le\frac23\omega(a)\omega(b),\qquad
 |K_4|\le\frac{56}{3}\prod_i\sqrt{\omega_i},\qquad
 |K_5|\le8\prod_i\sqrt{\omega_i}.
$$

Every purely external cubic also satisfies the stronger identity

$$
 K_3(-2p,p,p)=K_3(-p,-p,2p)
 =-\frac23\cos^2(p_1/2)\omega_p^3.
$$

This extra factor is decisive for the four rows that otherwise retain an
inverse external power.

After the verifier chooses two legs in every remaining cubic and combines
equal shifted dispersions, the 27 rows contain respectively four, fifteen,
and eight denominator-weight sums of total exponent one, two, and three.
Every total-three row retains at least one compensating factor $\omega_p$.

## Common five-centre shell bound

All one-loop propagators are centred at one of
$-2p,-p,0,p,2p$. Let $\rho$ be centered max-norm distance. The lattice
dispersion obeys

$$
 \omega(k)\ge\frac{16\rho(k)^2}{L^2},
$$

and the union of the five radius-$m$ shells contains at most $405m^3$
sites. Hence a product of shifted inverse dispersions with total exponent
$B=1,2,3$ has normalized sums bounded respectively by

$$
 \frac{405}{64},\qquad
 \frac{405}{256}(1+\log\lfloor L/2\rfloor),\qquad
 \frac{1215}{8192}L^2.
$$

For $B=3$, use $L^2\omega_p\le4\pi^2$. Summing the independently replayed
row constants gives the displayed common one-loop bound.

## Boundary and next gate

The complete fixed-order leading coefficient is now decided, but the
perturbative series is not known to be uniform on the tuned nonzero-coupling
branch. A growing negative coefficient cannot by itself be promoted to a
negative variance or a divergent physical moment; that would instead signal
loss of fixed-order control.

The next useful gate is nonperturbative: obtain a centered conditional-score,
convexity, or shell estimate for the actual interacting lowest mode, with a
uniform remainder that never expands through the nonuniform $g^4$ series.
No continuum measure, Born rule, Krein reconstruction, or Lorentzian causal
claim is established here.

## Verification

```sh
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_lower_loop_atlas.py --check
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_lower_loop_bounds.py --check
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_lower_loop_bounds_decision.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_lower_loop_bounds.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_lower_loop_bounds
```

Tier 0 and Tier 1 are the applicable commit rails. The upstream two-loop
certificates are unchanged and imported by content hash, so Tier 2 does not
require rebuilding their expensive exact outward cubature. Tier 3 is not run
because this is not a freeze, release, shared-core change, QME promotion, or
Lorentzian lifecycle promotion. A skipped higher tier is not a pass.

## Verification receipt

All Python rails ran under a 500 MB virtual-memory cap; the Science Forge
advisory ran with `GOMEMLIMIT=300MiB`.

- Tier 0: all five Python sources compiled, all changed JSON parsed, the scoped
  diff passed `git diff --check`, and two bounded `pdflatex` passes produced a
  57-page PDF of 660,923 bytes.
- Tier 1: the atlas check passed in 2.65 s at 22,052 KB peak; the lower-loop
  producer in 0.15 s at 16,816 KB; the certificate projection in 0.03 s at
  20,028 KB; and the independent verifier in 0.20 s at 30,412 KB. All ten
  focused reproduction and mutation tests passed in 5.78 s at 31,384 KB. The
  Paper 21 claim map regenerated and its independent boundary verifier passed.
- The append-only Science Forge event was accepted as sequence 22. The
  advisory shadow rail exited zero but is not counted as a scientific pass: it
  reported a pre-existing Forge binary/stdlib hash mismatch causing bridge
  audit error E9118, and a stale July corpus baseline of 976 certificates
  versus 1,717 currently. Diagnostics are preserved at
  `/tmp/sf-shadow.Iqh49M`.
- Tier 2 did not rebuild the unchanged content-addressed two-loop cubature
  chain; its certificate is imported by hash. Tier 3 was not run under the
  criteria above.
