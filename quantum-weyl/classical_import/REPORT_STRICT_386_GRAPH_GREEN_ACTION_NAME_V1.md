# Strict 386 graph Green-action convergent name

## Outcome

Yes. On the unit ultrastatic cylinder, the flat rank-15 adjoint-tractor Hodge wave is named by the canonical S3 Hodge spectral projectors and the exact retarded/advanced oscillator Duhamel kernels, with the scalar zero mode handled by s_0(tau)=tau. Smooth compact sources carry support-indexed LF spectral names; finite projector truncations converge in that topology, and continuity of the unique normally-hyperbolic Green operators makes the displayed partial actions a convergent operator name. The exact support-local curved BGG maps, trace/Weyl shear, and graph SDR then give named actions on all 30 endpoint and 386 graph rows. This serializes a convergent name, not a finite coefficient table or an effective complexity bound. A receiver-accepted common import snapshot, local D, q2, Hadamard and QME remain open.

## What is now portable

The nonlocal map is serialized as a **convergent operator name**, not as a finite jet matrix. A compact source is named by its support interval and canonical whole-eigenspace Hodge projections on the compact `S^3` slice. Each truncation is acted on by the displayed oscillator Duhamel formula. Continuity of the unique normally-hyperbolic Green map carries spectral convergence to the output topology.

| level | named action |
|---|---|
| parent | `Lambda_parent,sign = W_parent G_parent,sign` |
| trace-free endpoint | `p_BGG Lambda_parent,sign i_BGG` |
| 30-row endpoint | `U (Lambda_TF,sign direct-sum h_trace) U^-1` |
| 386-row graph | `H_alg_graph + i_end_graph Lambda_end,sign p_end_graph` |

## Spectral kernel

For eigenvalue `lambda>0`, `s_lambda(tau)=sin(sqrt(lambda) tau)/sqrt(lambda)`; for the scalar harmonic mode, `s_0(tau)=tau`. The future-supported sign integrates from the past to `t`; the past-supported sign is the oppositely signed integral from `t` to the future. Exact checks give:

- positive-mode ODE residual: `0`; initial derivative: `1`
- zero-mode ODE residual: `0`; initial derivative: `1`
- transpose relation: `k_plus(t,s)=k_minus(s,t)`

The spatial branches are scalar `k(k+2)` for `k>=0`, exact one-form `k(k+2)` for `k>=1`, and coexact one-form `(k+1)^2` for `k>=1`, each tensored with the rank-15 flat adjoint tractor bundle. Whole spectral projectors avoid selecting an eigenbasis inside degenerate eigenspaces. The round-sphere p-form spectrum is imported from the content-pinned Lauret source (Theorem 2.1, specialized to `n=2`, `p=0,1`); the receiver checks the displayed specialization but does not formalize the source's completeness proof.

## Topology and support

The source is `Gamma_c^infinity` with its strict LF topology over compact time slabs; the target has the compact-open `C^infinity` Frechet topology, restricted to the relevant causal orientation. The pinned normally-hyperbolic theorem supplies continuity, uniqueness and `supp G_sign f subset J_sign(supp f)`. Every BGG, trace/Weyl and graph-SDR map surrounding `G` is finite-order support-local.

## Honest boundary

This is a mathematical convergent name. It is not an effective projector implementation, a uniform complexity bound, serialized coordinate bytes for the distribution kernel, or an independently formalized weak-base proof of S3 Hodge spectral completeness. The weakest foundational base remains uncalibrated. This certificate does not itself accept a unary-causal common snapshot; that is a separate successor result. Separately, the authoritative classical Gate-A contract remains fail closed until all twenty exports, seven hashes and ten identities—including strict `D`, `q2` and residual data—share one snapshot. Hadamard, renormalized products and QME are not promoted.

## Verification

```text
python3 quantum-weyl/classical_import/build_strict_386_graph_green_action_name.py --check
python3 quantum-weyl/classical_import/check_strict_386_graph_green_action_name.py
python3 quantum-weyl/classical_import/verify_strict_386_graph_green_action_name.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_386_graph_green_action_name.py -v
```
