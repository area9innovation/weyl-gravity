# Bounded 110-row conjugate-pair extension no-go

## Result

Exactly one complementary-degree pair survives the degree test: a scalar
`chi` of degree zero and `chi_plus` of degree one, with
`<chi,chi_plus>=1`.  The alternative degree pair `(-1,2)` cannot receive
`q2` of two degree-zero old inputs.  Within the declared parity-even,
auxiliary-affine, action-arity-at-most-three and first-order Ward suborbit,
with only the metric-natural old `A--K` contraction and no clock/frame
insertion inside it, the complete decisive action basis is

```text
lambda tau e0 chi_plus + mu tau chi_plus
+ sum_b beta_b chi g_b h_b <K_b,dA>.
```

Pair rescaling leaves one nondegenerate normalized action class:
`lambda=1`, `mu=0`, `beta_0=beta_1=-1`.

## Original-rail substitution

Exact action differentiation emits
`2` unary keys and
`276` cyclic binary keys.  Substitution into
the original `tau_star` arity-two row cancels the former

```text
tau_star <- (e0 e1 A_0,K0_01)  coefficient +g0 h0.
```

It leaves the independent old-input coefficient

```text
tau_star <- (e1 A_0,
e2 K0_12)  coefficient -2 g0 h0.
```

This coefficient is the frozen emitter unary crossed with the frozen typed
Maxwell binary orbit.  The auxiliary action cannot reach it:
`<K,dA>` contains `K_12(e1 A_2-e2 A_1)`, never an `A_0--K_12` Hessian, and an
outer operator in `span{1,e0}` cannot change the component label.

## Boundary

This is a scoped minimal no-go for the complete bounded ansatz above, not a
claim against larger carriers, parity-odd terms or higher differential order.
The calculation stops on the nonzero `tau_star` row.  No `q3`, `K_Berger`,
observer-morphism, detector, cone, causal, branch, particle or quantum gate is
promoted.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_110_ROW_CONJUGATE_PAIR_EXTENSION_NO_GO.json`.
