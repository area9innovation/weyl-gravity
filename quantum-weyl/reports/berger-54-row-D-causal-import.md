# Berger 54-row classical D and causal-reduction import

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

This layered quantum-side handoff preserves the earlier pinned unary import
and consumes the corrected classical commit `46208d7c`. The companion
`BERGER_54_ROW_LOCAL_D_IMPORT` is the canonical D-only prerequisite receipt;
this integrated receipt repeats the D identities against the same contraction
to ensure that the later causal layer has not combined incompatible inputs. It independently
reconstructs the 54-row PBW-valued classical unary differential, cyclic
pairing, contraction, complete helical `D=e_0` action, and retained 26-row D
action. Exact composition verifies

```text
[q_1,D]=0
D iota_cl=iota_cl D_26
pi_cl D=D_26 pi_cl
[D,S_cl]=0
D^sharp Omega+Omega D=0
```

on every gauge-fixed row. Here `q_1` is the classical unary operator, not the
quantum correction proportional to hbar.

The causal theorem is also replayed in its corrected conditional form. Given

```text
q_26 Lambda_26,+/- + Lambda_26,+/- q_26 = 1_26,
```

the lifted operator

```text
Lambda_54,+/- = S_cl + iota_cl Lambda_26,+/- pi_cl
```

satisfies the 54-row identity because

```text
(1-iota_cl pi_cl) + iota_cl 1_26 pi_cl = 1_54.
```

Finite-order support locality and cyclic adjointness transfer through the
contraction. No `Lambda_26,+/-` is constructed here. The mixed-order retained
metric Green problem, Hadamard data, support-local q2, general nonlinear
Koszul--Tate export, renormalized Ward insertion, QME, and quantum D verdict
remain open.

Machine receipt:
`quantum-weyl/transfer/certificates/BERGER_54_ROW_D_CAUSAL_INPUT_IMPORT.json`.

Verification:

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_54_d_causal_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_54_d_causal_import.py -v
```
