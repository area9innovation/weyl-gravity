# Temporal Green order-five high-mode preflight

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The six external-clock rails define the formal degree-ten cosine/sine matrix
polynomial.  They do not make it a controlled Green approximation through
`two_j=138`.  The one-dimensional extreme charge block has exact eigenvalue
`196000/9`; at the certified detector time radii, the degree-ten cosine
polynomial has absolute error at least about `9.7e5` for `D0` and `1.9e8` for
`D1`, using only that the exact cosine is bounded by one.

The existing geometric remainder proof first becomes contractive at series
order 8 for `D0` and 14 for `D1`.  A common implementation therefore needs
external-clock streams through `p=28`.  This obstructs fixed-order promotion,
not the exact Green function.  Adaptive polynomial application, the spatial
tail, full Maxwell/massive images, recoil and Bridge 3 remain open.
