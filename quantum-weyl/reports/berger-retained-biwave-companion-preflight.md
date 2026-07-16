# Berger retained biwave companion preflight

The support-local classical contraction does more than remove clock rows from
the abstract complex. Independent exact PBW projection verifies

\[
P_{26}=\pi_{\rm cl}P_{34}^{\rm raw}\iota_{\rm cl},
\qquad
(P_{26})_{\rm metric}=A_{10}=\Box_2^2+V_2.
\]

Thus the lower-by-two tensor biwave is exactly the metric operator that must
be solved on the retained `3|10|10|3` endpoint. It is not merely a convenient
raw-coordinate surrogate.

The local twenty-row companion is

\[
\mathcal C_{20}=
\begin{pmatrix}
\Box_2&-I_{10}\\
V_2&\Box_2
\end{pmatrix},
\qquad
J(h)=(h,\Box_2h),
\]

and the exact graph identity is

\[
\mathcal C_{20}J(h)=(0,A_{10}h).
\]

This has now been strengthened from an on-graph identity to a two-sided
graph contraction.  With

\[
p_{\rm sol}(h,y)=h,\qquad i_{\rm src}(f)=(0,f),
\]

\[
p_{\rm src}(f_1,f_2)=\Box_2f_1+f_2,
\qquad H(f_1,f_2)=(0,-f_1),
\]

the exact operator algebra verifies

\[
p_{\rm sol}J=1,\quad p_{\rm src}i_{\rm src}=1,\quad
\mathcal C_{20}J=i_{\rm src}A_{10},\quad
p_{\rm src}\mathcal C_{20}=A_{10}p_{\rm sol},
\]

and

\[
1-Jp_{\rm sol}=H\mathcal C_{20},\qquad
1-i_{\rm src}p_{\rm src}=\mathcal C_{20}H,
\]

with the side conditions `H^2=0`, `p_sol H=0`, and `H i_src=0`.  Thus an
arbitrary companion source `(f1,f2)` reduces exactly to the retained source
`Box_2 f1+f2`; the certificate no longer assumes the auxiliary variable is
already on shell.

Its order-two principal symbol is block lower triangular with determinant
`q^20`. At the exact rational Berger fixture it has rank seven on a metric-null
covector and rank twenty off the metric cone. Unlike the full 13-row
clock/graph endpoint, this retained companion introduces no extra
characteristic cone.

The pinned classical microlocal theorem also corrects the interpretation of
the raw `L13` cone. Its exact right polarization has both retained metric and
clock components; it is not a pure clock mode, and selector projection does
not kill it. The valid homological operation is to apply the BV SDR and build
this different retained witness, not to project `L13` solutions. At the raw
`sqrt(2)` characteristic fixture the retained companion has exact rank twenty.

This is the correct starting point for a causal Volterra construction, not
the construction itself. Convergence, global causal support, advanced and
retarded operators, a cyclic companion pairing and causal adjointness, the
26- and 54-row chain homotopies, Hadamard data and all quantum claims remain
open. No inverse spatial Laplacian or mode projector is allowed.

```text
PYTHONPATH=quantum-weyl python -m lorentzian.retained_biwave_companion_preflight_certificate --check
PYTHONPATH=quantum-weyl python -m unittest quantum-weyl/lorentzian/tests/test_retained_biwave_companion_preflight.py -v
```
