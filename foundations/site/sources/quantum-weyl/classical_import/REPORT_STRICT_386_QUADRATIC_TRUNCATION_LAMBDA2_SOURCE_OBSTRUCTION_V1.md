# Strict 386-row q2-only lambda-squared source obstruction

## Outcome

No. An exact q1-closed pure-diffeomorphism metric fixture has nonzero q2 Jacobiator 75760/27 in the Weyl Noether row. Therefore the q2-only lambda-squared source has exact closure defect 37880/27. This proves that the quadratic truncation cannot be a Weyl-BV Maurer-Cartan or Moller map by itself. It is not a no-go for full Weyl gravity: the suspended arity-three identity requires q1 q3=-3 q2 q2, which would cancel the defect. The next import is now precise: an authoritative classical q3 plus an exact arity-three carrier bridge, with witness target -75760/9.

## Exact source calculation

```text
q1(r1)+(1/2)q2(x,x)=0
S2=q2(x,r1)+(1/6)q3(x,x,x)
N S2[q3=0]=(1/2)J2(x)
```

- Exact Jacobiator witness: `75760/27`.
- Exact q2-only source defect: `37880/27`.
- Required `q1 q3` witness value: `-75760/9`.

## Interpretation

The quadratic receiver candidate is now exactly ruled out as a standalone Maurer--Cartan interaction. This is positive information about the import boundary: full Weyl gravity must supply the cubic Taylor component required by its arity-three identity.

## Reproduction

```text
python3 quantum-weyl/classical_import/build_strict_386_quadratic_truncation_lambda2_source_obstruction.py --check
python3 quantum-weyl/classical_import/check_strict_386_quadratic_truncation_lambda2_source_obstruction.py
python3 quantum-weyl/classical_import/verify_strict_386_quadratic_truncation_lambda2_source_obstruction.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_quadratic_truncation_lambda2_source_obstruction.py -v
```

## Boundaries

- This does not establish that the receiver-constructed q2 is the authoritative nonlinear Weyl BV operation.
- This does not establish the authoritative q3 or any higher Taylor component.
- This does not establish failure of lambda-squared source closure in the full Weyl theory after q3 is included.
- This does not establish a no-go theorem against Weyl gravity, its BV complex or its physical spectrum.
- This does not establish an analytic Moller map, Hadamard state, renormalized products, QME restoration, residual transfer or Lorentzian quantum theory.
