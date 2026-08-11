# BT eight-point Krein charge localization

**Certificate:**
`REVERSE_PHYSICS_BT_EIGHT_POINT_KREIN_CHARGE_LOCALIZATION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The minimal Krein lift of the eight-point profile obstruction cannot be the
purely negatively charged, trace-null \(Q\) remainder in Bateman--Turok
Eq. (19).  Its nonzero norm is produced entirely by interference between the
positive- and negative-charge lines.

At

\[
 \rho=\frac{819}{4000},\qquad
 G=
 \begin{pmatrix}
 0&-\rho\\
 -\rho&-2
 \end{pmatrix},
\]

the two invariant charge eigenlines may be chosen as

\[
 n_+=\binom10,\qquad n_-=\binom1{-\rho}.
\]

Both are null.  With

\[
 S=(n_+,n_-),\qquad
 J=\begin{pmatrix}0&1\\1&0\end{pmatrix},
\]

one has

\[
 S^TGS=\rho^2J.
\]

Transporting the diagonal charge generator
\(H_0=\operatorname{diag}(1,-1)\) back to the forced complement basis gives

\[
 H_G=SH_0S^{-1}
 =\begin{pmatrix}
 1&2/\rho\\
 0&-1
 \end{pmatrix}
 =\begin{pmatrix}
 1&8000/819\\
 0&-1
 \end{pmatrix}.
\]

It satisfies both exact charge identities

\[
 H_G^2=I,\qquad H_G^TG+GH_G=0.
\]

Thus the conclusion is not an artifact of calling the original basis vectors
charged.  It uses the correctly conjugated invariant charge action.

## Where the negative norm lives

The profile lift uses the canonical second fibre vector

\[
 f_2=\binom01,\qquad f_2^TGf_2=-2.
\]

Its charge projections are

\[
 \Pi_+f_2=\binom{1/\rho}{0},\qquad
 \Pi_-f_2=\binom{-1/\rho}{1}.
\]

Each component is separately null:

\[
 (\Pi_+f_2)^TG(\Pi_+f_2)=0,\qquad
 (\Pi_-f_2)^TG(\Pi_-f_2)=0.
\]

The two cross pairings are instead

\[
 (\Pi_+f_2)^TG(\Pi_-f_2)
 =(\Pi_-f_2)^TG(\Pi_+f_2)=-1.
\]

Their sum is the entire norm \(-2\).  A nonzero negative vector in this
cross-Krein plane necessarily mixes the two null charge directions.

## The complete two-profile block

Let \(B\) be the certified forward block with amplitudes
\(\sqrt{6699}/16\) and \(\sqrt{7149}/16\), and put

\[
 B_\pm=(\Pi_\pm\oplus\Pi_\pm)B.
\]

The exact one-sided pullbacks vanish:

\[
 B_+^\sharp B_+=0,\qquad B_-^\sharp B_-=0.
\]

The cross terms are equal and nonzero:

\[
 B_+^\sharp B_-
 =B_-^\sharp B_+
 =\frac12
 \begin{pmatrix}
 -6699/128&0\\
 0&-7149/128
 \end{pmatrix}.
\]

Therefore

\[
 B^\sharp B
 =B_+^\sharp B_-+B_-^\sharp B_+
 =K_4.
\]

The full rank-two negative effect has total charge zero and is entirely
cross-charge.  Its purely negative-charge projection has exactly zero
pullback.

## Consequence for Eq. (19)

Bateman--Turok's \(Q\) is claimed to contain only negatively charged
operators, which become null and orthogonal under the invariant trace.  On the
declared fibre, that description matches \(B_-\), but

\[
 B_-^\sharp B_-=0\ne K_4.
\]

Hence the new fourth-profile block cannot be hidden in \(Q\).  If it appears
in a complete Eq. (19) construction, its nonzero contribution must arise in a
neutral higher-composite sector or through additional zero-mode/dynamical
trace terms that generate the positive/negative cross pairing.

This agrees with the certified finite-mode order-\(\lambda\) result, where
\(Q_1=0\) and the completed sector is neutral.  It does not derive the
higher-composite block from that order-\(\lambda\) calculation.

## Claim boundary

Established exactly:

- the invariant null charge basis and transported generator;
- charge involution and Gram invariance;
- the two charge projectors;
- nullity of both one-sided pieces of \(f_2\);
- localization of its full norm in the cross pairing;
- the charge decomposition of both hard-profile amplitudes;
- zero one-sided profile pullbacks;
- reconstruction of \(K_4\) entirely from charge-zero cross terms; and
- failure of the purely negative \(Q\)-remainder identification on this
  fibre.

Not established:

- failure of the full Bateman--Turok Eq. (19);
- nonexistence of a neutral higher-composite completion;
- nonexistence of additional zero-mode or vacuum trace terms;
- an all-order charge-compatible projector pushforward;
- a normalized fourth-event or complete \(2\to6\) probability;
- a spacetime Møller/LSZ/S operator;
- a gravity/BRST lift or anything `LORENTZIAN-CAUSAL`; or
- literature priority.

## Verification receipt

All commands ran sequentially on 2026-08-12 with `ulimit -v 500000` and
Python 3.12.13 from
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation passed for the producer, verifier, and mutation
  tests (`0.02 s`, peak `14640 KiB`).
- Tier 0 JSON parsing passed for the work item, certificate, and schema
  (`0.10 s`, peak `14720 KiB`).
- `python3 reverse_physics/bt_eight_point_krein_charge_localization.py
  --check` passed `20/20` exact checks (`0.36 s`, peak `68072 KiB`).
- `python3
  reverse_physics/verify_bt_eight_point_krein_charge_localization.py` passed
  `20/20` independent checks (`0.43 s`, peak `72184 KiB`).
- `python3
  reverse_physics/tests/test_bt_eight_point_krein_charge_localization.py`
  passed `20/20` falsification tests (`7.98 s`, peak `72556 KiB`).
- Two-pass `pdflatex` builds of Paper V passed (`0.45 s`, `0.45 s`; peak
  `50768 KiB`, `50788 KiB`), retaining exactly its four pre-existing overfull
  boxes and introducing no new one.
- Two-pass `pdflatex` builds of Paper VI passed (`0.47 s`, `0.48 s`; peak
  `50672 KiB`, `50524 KiB`) with no overfull box or undefined reference.

The producer imports all mathematical predecessors by content hash.  Its exact
charge decomposition plus the independent matrix verifier is the affected Tier
2 chain.  Tier 3 was unnecessary because no shared core, freeze, release,
lifecycle promotion beyond `CLASSIFIED`, or Lorentzian claim changed.  The
Science Forge advisory was not rerun; its earlier same-session helpers aborted
and its census timed out after `180.17 s`, so that inconclusive output remains
outside the evidence for this claim.
