"""Human- and machine-readable dictionary for the minimal chain comparison."""

from __future__ import annotations

from typing import Iterator

from bridge.bv_complex.conformal_polynomials import SYMMETRIC_PAIRS
from bridge.bv_complex.polynomial_bv import PolynomialBVBlock


TRACEFREE_COMPONENTS = tuple(
    [f"({first}{second})" for first, second in SYMMETRIC_PAIRS if first != second]
    + [f"({axis}{axis})-(33)" for axis in range(3)]
)


MODULE_DATA = {
    ("gauge", 0): {
        "raw_variable": "c_mu",
        "bv_variable": "diffeomorphism ghost c_mu",
        "field_redefinition": "c_raw=c",
        "ghost_number": 1,
        "antifield_number": 0,
        "local_degree": -1,
        "differential": "K_0 c",
        "target": "M_n:h_0",
    },
    ("gauge", 1): {
        "raw_variable": "Omega",
        "bv_variable": "Weyl ghost omega",
        "field_redefinition": "Omega=omega+(partial.c)/4",
        "ghost_number": 1,
        "antifield_number": 0,
        "local_degree": -1,
        "differential": "tau",
        "target": "M_n:tau",
    },
    ("metric", 0): {
        "raw_variable": "h_0",
        "bv_variable": "trace-free metric fluctuation",
        "field_redefinition": "h_0=h-eta tr(h)/4",
        "ghost_number": 0,
        "antifield_number": 0,
        "local_degree": 0,
        "differential": "B_lin h_0",
        "target": "E_n:hstar_0",
    },
    ("metric", 1): {
        "raw_variable": "tau",
        "bv_variable": "metric trace",
        "field_redefinition": "tau=tr(h)/8",
        "ghost_number": 0,
        "antifield_number": 0,
        "local_degree": 0,
        "differential": "0",
        "target": "0",
    },
    ("equation", 0): {
        "raw_variable": "hstar_0",
        "bv_variable": "trace-free metric antifield",
        "field_redefinition": "hstar_0=hstar-eta tr(hstar)/4",
        "ghost_number": -1,
        "antifield_number": 1,
        "local_degree": 1,
        "differential": "partial^mu hstar_0(mu nu)",
        "target": "I_n:i_star",
    },
    ("equation", 1): {
        "raw_variable": "tau_star",
        "bv_variable": "trace metric antifield",
        "field_redefinition": "tau_star=2 tr(hstar)",
        "ghost_number": -1,
        "antifield_number": 1,
        "local_degree": 1,
        "differential": "Omega_star",
        "target": "I_n:Omega_star",
    },
    ("identity", 0): {
        "raw_variable": "i_star_mu",
        "bv_variable": "diffeomorphism-ghost antifield",
        "field_redefinition": "i_star=-(cstar+partial omegastar/4)/2",
        "ghost_number": -2,
        "antifield_number": 2,
        "local_degree": 2,
        "differential": "0",
        "target": "0",
    },
    ("identity", 1): {
        "raw_variable": "Omega_star",
        "bv_variable": "Weyl-ghost antifield",
        "field_redefinition": "Omega_star=omegastar",
        "ghost_number": -2,
        "antifield_number": 2,
        "local_degree": 2,
        "differential": "0",
        "target": "0",
    },
}


def _spin_label(kind: str, component: int) -> str:
    if kind == "scalar":
        return ""
    if kind == "vector":
        return f"_{component}"
    if kind == "symmetric_tf":
        return "_" + TRACEFREE_COMPONENTS[component]
    return f"_{component}"


def _monomial_label(exponent: tuple[int, ...]) -> str:
    terms = []
    for axis, power in enumerate(exponent):
        if power == 0:
            continue
        terms.append(f"P{axis}" if power == 1 else f"P{axis}^{power}")
    return "1" if not terms else "*".join(terms)


def _so4_content(kind: str, level: int) -> str:
    spin = {
        "scalar": "(0,0)",
        "vector": "(1/2,1/2)",
        "symmetric_tf": "(1,1)",
    }[kind]
    return f"{spin} tensor Sym^{level}(1/2,1/2)"


def row_dictionary() -> list[dict[str, object]]:
    rows = []
    raw_names = {"gauge": "G_n", "metric": "M_n", "equation": "E_n", "identity": "I_n"}
    for key, data in MODULE_DATA.items():
        chain_row, module_index = key
        rows.append(
            {
                "raw_row": raw_names[chain_row],
                "module_index": module_index,
                **data,
                "equality_certificate": "F Q_BV = Q_raw F exactly",
            }
        )
    return rows


def basis_records(
    energy: int, block: PolynomialBVBlock | None = None
) -> Iterator[dict[str, object]]:
    """Yield one dictionary row for every raw basis vector at fixed energy."""

    block = PolynomialBVBlock.at_energy(energy) if block is None else block
    if block.energy != energy:
        raise ValueError("dictionary block has the wrong energy")
    # Slicing one sparse SymPy column for every basis vector is needlessly
    # expensive.  Count the stored entries once and keep the dictionary
    # generation linear in the sparse matrix size.
    column_nnz = [0] * block.dimension
    for _, column in block.q.todok():
        column_nnz[column] += 1
    raw_names = {"gauge": "G_n", "metric": "M_n", "equation": "E_n", "identity": "I_n"}
    for chain_slice in block.slices:
        module_offset = 0
        for module_index, (module, level) in enumerate(chain_slice.modules):
            metadata = MODULE_DATA[(chain_slice.name, module_index)]
            for local_index, (component, exponent) in enumerate(module.basis(level)):
                raw_index = chain_slice.start + module_offset + local_index
                label = (
                    metadata["raw_variable"]
                    + _spin_label(module.spin_kind, component)
                    + "["
                    + _monomial_label(exponent)
                    + "]"
                )
                yield {
                    "energy": energy,
                    "raw_row": raw_names[chain_slice.name],
                    "raw_index": raw_index,
                    "raw_basis_element": label,
                    "bv_variable": metadata["bv_variable"],
                    "field_redefinition": metadata["field_redefinition"],
                    "conventional_bv_ghost_number": metadata["ghost_number"],
                    "antifield_number": metadata["antifield_number"],
                    "local_tangent_degree": metadata["local_degree"],
                    "compact_degree": energy,
                    "primary_weight": str(module.dimension_primary),
                    "polynomial_level": level,
                    "so4_content": _so4_content(module.spin_kind, level),
                    "differential_image": metadata["differential"],
                    "differential_target": metadata["target"],
                    "image_nnz": column_nnz[raw_index],
                    "equality_certificate": "exact",
                }
            module_offset += module.dimension(level)
