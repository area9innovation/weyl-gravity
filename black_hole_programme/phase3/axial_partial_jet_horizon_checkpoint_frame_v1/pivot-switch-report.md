# Mixed horizon pivot-switch repair

Dependency tag: `REDUCED-MODE`.

## Positive bounded result

The former mixed-line refusal at panel 27 is reproduced.  At the preceding
transition the fixed rational chart

\[
M=\begin{pmatrix}
1&0&0&0\\
0&1&0&0\\
0&0&1&-1\\
0&0&0&1
\end{pmatrix},
\qquad \det M=1,
\]

selects the row \(e_2-e_3\), whose ball excludes zero.  This row has the
largest certified modulus lower bound in the fixed atlas
\(\{e_2,e_3,e_2-e_3,e_2+e_3\}\).  The same \(M\) is applied to the base and
intrinsic tangent, and the full dual generator is conjugated by
\(\operatorname{diag}(M,M)\).

The repair also retains the exact correlation discarded by rectangular ball
division.  If \(s\) is the selected base pivot and \(t\) its tangent, then the
normalized pivot is set by the algebraic identities

\[
s/s=1,\qquad (ts-st)/s^2=0.
\]

With that fixed GL/projective chart, one panel beyond the former obstruction
passes both the Taylor self-map and the next pivot gate.  A resumable
post-switch checkpoint is stored in `pivot-switch-run.json`.

## Boundary

This is deliberately a one-panel representation repair.  It does not reach
\(r=4\), construct the complete \(H_4\) frame, recover \(T_+\), or establish
the global Stokes identity.
