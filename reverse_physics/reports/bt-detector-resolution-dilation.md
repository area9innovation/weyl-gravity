# BT detector-resolution dilation

**Result:** `COEFFICIENT_COMPUTED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

The endpoint fibre in the logarithmic-shell calculation is no longer an
unaffiliated abstract copy.  It is the normalized cutoff-difference fibre of
an explicit asymptotic momentum-resolution detector algebra.  This gives the
physical leading-log response a regulator-profile-independent meaning on the
declared final-pair cylinder.  It does not construct a time Møller operator or
a spacetime-local detector algebra.

## Detector algebra and trace

Use the oriented daughter-mass ratio (r>0) and

\[
 y=-\log r.
\]

On the three unordered final-pair channels take the commutative semifinite
detector algebra

\[
 \mathcal D=L^\infty(\mathbb R,dy)\mathbin{\bar\otimes}\mathbb C^3,
 \qquad
 \tau(f)=\sum_i\int_{\mathbb R}f_i(y)\,dy
\]

on its positive trace-finite ideal.  Let (q) be a nonincreasing resolution
profile with endpoint values (q(-\infty)=1), (q(+\infty)=0), and put

\[
 q_R(y)=q(y-R),\qquad
 d_{R,a}=q_{R+a}-q_R,\qquad a>0.
\]

Then (d_{R,a}\geq0), and translation invariance gives the exact identity

\[
 \tau(d_{R,a})=
 \int_{\mathbb R}\bigl(q(y-R-a)-q(y-R)\bigr)dy=a.
\]

Equivalently, integrate (-q') over a translation interval of length (a):
only the unit endpoint jump remains.  The result depends neither on (R) nor
on the transition shape.

Two exact fixtures make this non-formal.  The sharp profile has
(d_{0,1}=1_{(0,1]}) and trace one.  For the (C^1) cubic smoothstep

\[
 q(z)=
 \begin{cases}
 1,&z\leq0,\\
 1-3z^2+2z^3,&0\leq z\leq1,\\
 0,&z\geq1,
 \end{cases}
\]

the unit-shift density is

\[
 d_{0,1}(y)=
 \begin{cases}
 y^2(3-2y),&0\leq y\leq1,\\
 (2-y)^2(2y-1),&1\leq y\leq2,\\
 0,&\text{otherwise}.
 \end{cases}
\]

Both pieces are positive and each integrates to (1/2).  Thus the smooth
trace is again one.  The producer and independent verifier use exact rational
polynomial integration.

## The shell is a dilation cocycle

The normalized cutoff shell is

\[
 u_{R,a}=\sqrt{d_{R,a}/a},\qquad \|u_{R,a}\|_2=1.
\]

For the unitary translations ((T_bf)(y)=f(y-b)),

\[
 d_{R+b,a}=T_bd_{R,a},\qquad
 u_{R+b,a}=T_bu_{R,a}.
\]

Therefore the embeddings used in the preceding shell theorem are derived as

\[
 J_{R,a}e_i=u_{R,a}\ \text{in channel }i,
 \qquad J_{R,a}h=h,
\]

and obey

\[
 J_{R+b,a}=(1_h\oplus T_b\otimes1_3)J_{R,a}.
\]

This is the physical affiliation that is available from the computed
observable: detector-scale dilation of the daughter-mass resolution.  It is
not time evolution.  In particular, it does not undo the certified failure of
an ordinary strong Møller limit.

## Physical leading-log response

The exact five-point generalized-Born calculation supplies constant density
(1/48) per unordered pair per unit (y).  Hence a resolution increment
(a=\log c) gives, after Born normalization,

\[
 \Delta_{\rm real}=3\frac{a}{48}=\frac{a}{16}.
\]

On the regulated physical hard-plus-collinear quotient, pseudo-unitarity
forces

\[
 2\operatorname{Re}B_{hh}=-\|Ah\|^2=-\frac1{16}.
\]

The hard survival response is consequently (-a/16), and

\[
 \Delta_{\rm inclusive}^{\rm LL}
 =\Delta_{\rm real}+\Delta_{\rm hard}=0.
\]

Multiplying by the Born coefficient (3/32), the two absolute coefficients
are (+3/512) and (-3/512) in common units
(lambda^6\log(c)/(\pi^4s)).  The cancellation holds for the sharp and
cubic profiles explicitly, and for every admissible monotone profile by the
trace theorem.  It is a physical NLO leading-log **resolution response** on
the declared final-pair cylinder, not a computed regulator-independent finite
NLO constant.

## Boundary

This result establishes an asymptotic momentum-detector algebra, its positive
semifinite cutoff trace, the dilation cocycle underlying the endpoint fibre,
and the profile-independent leading-log cancellation.  It does not establish
a BT soft-collinear time-asymptotic Hamiltonian, complete incoming degenerate
sectors, a spacetime-local LSZ/AQFT algebra, a full continuum S-matrix domain,
the finite NLO probability, beyond-tree positivity, all-order Eq. (19), a
gravity/BRST lift, or anything `LORENTZIAN-CAUSAL`.

The next dynamical test is sharp: a BT asymptotic Hamiltonian must implement
this same detector-dilation automorphism on complete in/out sectors.  The
separate Eq. (19) route still needs the all-order pushforward/range theorem.

Primary source: [Bateman--Turok, arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096),
Eq. (6), Eq. (17), and Appendix B.  The detector trace and dilation theorem
are repository results; no literature-priority claim is made.

Verification commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_detector_resolution_dilation.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_detector_resolution_dilation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_detector_resolution_dilation
```

Final scoped receipt, 2026-08-11; every Python and TeX command ran
sequentially under `ulimit -v 500000`:

| Tier | Command | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0 | `py_compile` producer, verifier, and test | PASS | 0.03 s | 15,932 KB |
| 0 | parse event, work item, certificate, and schema | PASS | 0.14 s | 14,984 KB |
| 1 producer | exact profile/response producer | PASS, 24/24 | 0.04 s | 20,080 KB |
| 1 independent | independent schema, polynomial, source, and response verifier | PASS, 15/15 | 0.10 s | 30,116 KB |
| 1 mutations | nine tests, including seven decisive scientific mutations | PASS | 0.90 s | 30,384 KB |
| papers | Paper V, final second pass | PASS | 0.40 s | 50,748 KB |
| papers | Paper VI, final second pass | PASS | 0.47 s | 51,012 KB |

PDF text extraction independently found the detector-dilation theorem,
sharp/smooth equality, physical response, and non-transfer boundary.  The new
Paper V passage introduces no overfull box; that paper retains four unrelated
pre-existing boxes and its pre-existing PDF-string warnings.  Paper VI's
final build has no overfull box or warning.  The prose advisory is explicitly
non-certifying: Paper V retains its existing emphasis, dash, parenthetical,
and long-abstract findings; Paper VI retains its existing parenthetical and
long-abstract findings.

Tier 2 was not run because every imported mathematical input is unchanged and
content-addressed and no shared operator or schema consumer changed.  Tier 3
was not run because this is not a freeze, release, shared-core change, or
promotion to a full S-matrix, finite NLO probability, Eq. (19), or
`LORENTZIAN-CAUSAL` theorem.  These unrun tiers are not passes.

The Science Forge coordinator successfully appended terminal event
`01a29d0c7b6a2b6c`; no manual event fallback is claimed for this package.
