# Berger lower-by-two import and equal-connection factor screen

Classical commit `db099319` supplies the authoritative exact normal form
`A10=Box_2^2+V_2`, with `Box_2` the covariant rough wave on symmetric
two-tensors and `ord(V_2)<=2`. The quantum consumer pins its certificate and
operator artifacts, independently reconstructs the identity, replays the
degree-two rank ledger `(9,10,7,10)`, and confirms that all 92 nonzero
quadratic entries are nondivisible by the scalar wave polynomial.

The pinned raw ten-row Berger metric endpoint has exact scalar-biwave
principal part.  The PBW cubic symbol is not tested by naive polynomial
division: the square of the exact scalar wave already contains a cubic PBW
commutator term.  After subtracting that exact square, every remaining cubic
entry is divisible by twice the wave symbol.  This fixes the first-order
connection of an equal-factor split uniquely; it has 24 nonzero matrix
entries.

Let

\[
N=\Box_0 I_{10}+\Gamma^a e_a.
\]

The exact remainder `A-N^2` has order two.  If the endpoint factored as

\[
(N+E)(N+F)
\]

with invariant order-zero matrix potentials, its quadratic symbol would be
`zeta^2(E+F)`.  It is not.  The normalized dual functional

\[
\ell(S)=-u^{-2}[p_0p_3]S_{h_{00},h_{03}}
\]

vanishes on `zeta^2 Mat10` and evaluates to one on the exact remainder,
whose selected entry is `-u^2 p0 p3`.  This is an exact obstruction to the
shared-connection Laplace-type factor ansatz.

The downstream result is intentionally narrow.  It does not constrain two factors with
different first-order parts, a larger auxiliary-field system, or a first-order
reduction. The classical causal Volterra/Levi resolvent route also remains
open. It constructs no advanced/retarded operator and does not promote
the retained causal homotopy or any quantum lifecycle state.

Classical commit `d6c64253` adds the decisive endpoint-level boundary. The
quantum consumer independently reconstructs its bordered Douglis determinant
and rank fixtures: `L13` has a genuine rank-one characteristic at
`p0^2=2|p_spatial|^2`, away from the metric cone. A metric-causal inverse on
arbitrary 13-row sources is therefore impossible. The next physical route is
the hybrid retained chain homotopy, not a full `G13_pm`.

Verification:

```bash
PYTHONPATH=quantum-weyl python3 -m lorentzian.metric_equal_connection_factor_screen_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/lorentzian/tests/test_metric_equal_connection_factor_screen.py -v
```
