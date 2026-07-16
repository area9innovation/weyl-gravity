# Raw Berger endpoint Green preflight

In the raw (10+2) metric/clock presentation, the exact field block is

\[
\begin{pmatrix}A&B\\ C&I_2\end{pmatrix},
\qquad
\operatorname{ord}(A,B,C)=(4,2,4).
\]

Naively eliminating the clock pair produces (S=A-BC).  The correction is
nonzero and has order six, so direct Schur elimination is not yet a Green
construction.  Its top symbol is nevertheless rank one off characteristic
and has an exact factor (zeta^2); it vanishes on the tested null stratum.
Thus the added top order belongs to a gauge/clock extension rather than a new
physical characteristic.

The next gate is to realize this rank-one wave-divisible term as a finite
Green-hyperbolic extension (or prove an exact factorization).  No causal flag
is promoted by this preflight.
