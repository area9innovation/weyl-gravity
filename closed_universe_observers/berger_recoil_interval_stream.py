"""Exact interval primitives for Berger recoil shell aggregation.

This module exposes the certified finite detector-coefficient image and then
starts the shell evaluator after the still-open nested Green-convolution gate.
The shell inputs are already-enclosed channel values I_abc[two_j,k]; the
evaluator applies the certified coupling and Peter--Weyl factors.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import factorial, isqrt
from typing import Any, Mapping, Sequence

import sympy as sp


@dataclass(frozen=True)
class RationalInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    @classmethod
    def point(cls, value: Fraction | int) -> "RationalInterval":
        value = Fraction(value)
        return cls(value, value)

    @classmethod
    def from_serialized(cls, value: Mapping[str, str]) -> "RationalInterval":
        return cls(Fraction(value["lower"]), Fraction(value["upper"]))

    def __add__(self, other: "RationalInterval") -> "RationalInterval":
        return RationalInterval(self.lower + other.lower, self.upper + other.upper)

    def __neg__(self) -> "RationalInterval":
        return RationalInterval(-self.upper, -self.lower)

    def __sub__(self, other: "RationalInterval") -> "RationalInterval":
        return self + (-other)

    def __mul__(self, other: "RationalInterval") -> "RationalInterval":
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return RationalInterval(min(products), max(products))

    def scale(self, scalar: Fraction | int) -> "RationalInterval":
        return self * RationalInterval.point(Fraction(scalar))

    def serialize(self) -> dict[str, str]:
        return {
            "lower": str(self.lower),
            "upper": str(self.upper),
            "width": str(self.upper - self.lower),
        }


@dataclass(frozen=True)
class ComplexRationalInterval:
    real: RationalInterval
    imaginary: RationalInterval

    @classmethod
    def point(
        cls, real: Fraction | int = 0, imaginary: Fraction | int = 0
    ) -> "ComplexRationalInterval":
        return cls(RationalInterval.point(real), RationalInterval.point(imaginary))

    def __add__(self, other: "ComplexRationalInterval") -> "ComplexRationalInterval":
        return ComplexRationalInterval(
            self.real + other.real,
            self.imaginary + other.imaginary,
        )

    def __neg__(self) -> "ComplexRationalInterval":
        return ComplexRationalInterval(-self.real, -self.imaginary)

    def __mul__(self, other: "ComplexRationalInterval") -> "ComplexRationalInterval":
        return ComplexRationalInterval(
            self.real * other.real - self.imaginary * other.imaginary,
            self.real * other.imaginary + self.imaginary * other.real,
        )

    def scale(self, scalar: Fraction | int) -> "ComplexRationalInterval":
        scalar_interval = RationalInterval.point(Fraction(scalar))
        return ComplexRationalInterval(
            self.real * scalar_interval,
            self.imaginary * scalar_interval,
        )

    def absolute_upper(self) -> Fraction:
        # |z|_2 <= |Re z| + |Im z|, sufficient for the induced row-sum norm.
        return _absolute_upper(self.real) + _absolute_upper(self.imaginary)

    def serialize(self) -> dict[str, dict[str, str]]:
        return {"real": self.real.serialize(), "imaginary": self.imaginary.serialize()}


def _sum_intervals(values: Sequence[RationalInterval]) -> RationalInterval:
    total = RationalInterval.point(0)
    for value in values:
        total = total + value
    return total


def detector_profile_coefficient_interval(
    certificate: Mapping[str, Any],
    *,
    detector: str,
    two_j: int,
    block: str,
    row: int,
    column: int,
    t_power: int,
    coframe_component: int | None = None,
) -> dict[str, object]:
    """Read one certified finite advanced-Maxwell detector coefficient.

    Missing serialized entries inside the validated index domain are exact
    structural zeros.  The provider is intentionally limited to two_j<=4.
    """
    if certificate.get("result_id") != "BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE":
        raise ValueError("wrong detector coefficient certificate")
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
    if not 0 <= two_j <= 4:
        raise ValueError("finite detector coefficient provider covers only 0<=two_j<=4")
    dimension = two_j + 1
    if not 0 <= row < dimension or not 0 <= column < dimension:
        raise ValueError("row and column must lie in the selected representation")
    if t_power < 0:
        raise ValueError("t_power must be nonnegative")
    if block == "spatial_one_form_advanced_polynomial":
        if coframe_component not in (1, 2, 3):
            raise ValueError("spatial block requires coframe_component=1,2,3")
    elif block == "temporal_scalar_advanced_polynomial":
        if coframe_component is not None:
            raise ValueError("temporal block has no coframe component")
    else:
        raise ValueError("unknown detector coefficient block")

    detector_row = next(row_value for row_value in certificate["detectors"] if row_value["detector_id"] == detector)
    mode = next(mode_value for mode_value in detector_row["modes"] if mode_value["two_j"] == two_j)
    match = None
    for entry in mode[block]:
        if entry["row"] != row or entry["column"] != column:
            continue
        if block.startswith("spatial") and entry["coframe_component"] != coframe_component:
            continue
        match = next((coefficient for coefficient in entry["coefficients"] if coefficient["T_power"] == t_power), None)
        break
    if match is None:
        real = imaginary = RationalInterval.point(0)
        structural_zero = True
    else:
        real = RationalInterval.from_serialized(match["real"])
        imaginary = RationalInterval.from_serialized(match["imag"])
        structural_zero = False
    return {
        "detector": detector,
        "two_j": two_j,
        "block": block,
        "coframe_component": coframe_component,
        "row": row,
        "column": column,
        "T_power": t_power,
        "real": real.serialize(),
        "imaginary": imaginary.serialize(),
        "structural_zero": structural_zero,
        "uniform_entire_series_remainders": mode["uniform_entire_series_remainders"],
        "claim_boundary": "finite advanced Maxwell detector coefficient through two_j=4; not a massive or recoil-channel coefficient",
    }


def _absolute_upper(interval: RationalInterval) -> Fraction:
    return max(abs(interval.lower), abs(interval.upper))


def _sqrt_fraction_interval(value: Fraction, bits: int) -> RationalInterval:
    if value < 0:
        raise ValueError("cannot enclose a negative square root on the real line")
    if bits < 8:
        raise ValueError("radical_bits must be at least 8")
    scale = 1 << bits
    scaled_numerator = value.numerator * scale * scale
    quotient = scaled_numerator // value.denominator
    lower_integer = isqrt(quotient)
    lower = Fraction(lower_integer, scale)
    if lower_integer * lower_integer * value.denominator == scaled_numerator:
        return RationalInterval.point(lower)
    return RationalInterval(lower, Fraction(lower_integer + 1, scale))


def _real_interval_power(interval: RationalInterval, exponent: int) -> RationalInterval:
    if exponent < 0:
        raise ValueError("negative interval powers are not supported")
    result = RationalInterval.point(1)
    factor = interval
    power = exponent
    while power:
        if power & 1:
            result = result * factor
        factor = factor * factor
        power >>= 1
    return result


def _sympy_real_interval(
    expression: sp.Expr,
    *,
    mass_squared_interval: RationalInterval,
    radical_bits: int,
) -> RationalInterval:
    """Evaluate the exact payload expression by outward rational intervals."""
    if expression.is_Integer:
        return RationalInterval.point(int(expression))
    if expression.is_Rational:
        return RationalInterval.point(Fraction(int(expression.p), int(expression.q)))
    if expression.is_Symbol and expression.name == "mu_squared":
        return mass_squared_interval
    if expression.is_Add:
        return _sum_intervals(
            [
                _sympy_real_interval(
                    term,
                    mass_squared_interval=mass_squared_interval,
                    radical_bits=radical_bits,
                )
                for term in expression.args
            ]
        )
    if expression.is_Mul:
        value = RationalInterval.point(1)
        for factor in expression.args:
            value = value * _sympy_real_interval(
                factor,
                mass_squared_interval=mass_squared_interval,
                radical_bits=radical_bits,
            )
        return value
    if expression.is_Pow:
        base, exponent = expression.args
        if exponent == sp.Rational(1, 2) and base.is_Rational and base >= 0:
            return _sqrt_fraction_interval(
                Fraction(int(base.p), int(base.q)), radical_bits
            )
        if exponent.is_Integer:
            return _real_interval_power(
                _sympy_real_interval(
                    base,
                    mass_squared_interval=mass_squared_interval,
                    radical_bits=radical_bits,
                ),
                int(exponent),
            )
    raise ValueError(f"unsupported exact kernel expression: {sp.sstr(expression)}")


def _sympy_complex_interval(
    serialized: str,
    *,
    mass_squared_interval: RationalInterval,
    radical_bits: int,
) -> ComplexRationalInterval:
    expression = sp.sympify(
        serialized,
        locals={"mu_squared": sp.Symbol("mu_squared", real=True), "I": sp.I},
    )
    real_part, imaginary_part = expression.as_real_imag(deep=True)
    return ComplexRationalInterval(
        _sympy_real_interval(
            sp.expand(real_part),
            mass_squared_interval=mass_squared_interval,
            radical_bits=radical_bits,
        ),
        _sympy_real_interval(
            sp.expand(imaginary_part),
            mass_squared_interval=mass_squared_interval,
            radical_bits=radical_bits,
        ),
    )


def _zero_complex_matrix(dimension: int) -> list[list[ComplexRationalInterval]]:
    return [
        [ComplexRationalInterval.point() for _ in range(dimension)]
        for _ in range(dimension)
    ]


def _identity_complex_matrix(dimension: int) -> list[list[ComplexRationalInterval]]:
    value = _zero_complex_matrix(dimension)
    for index in range(dimension):
        value[index][index] = ComplexRationalInterval.point(1)
    return value


def _multiply_complex_interval_matrices(
    left: Sequence[Sequence[ComplexRationalInterval]],
    right: Sequence[Sequence[ComplexRationalInterval]],
) -> list[list[ComplexRationalInterval]]:
    dimension = len(left)
    output = _zero_complex_matrix(dimension)
    for row in range(dimension):
        for inner in range(dimension):
            if left[row][inner] == ComplexRationalInterval.point():
                continue
            for column in range(dimension):
                if right[inner][column] == ComplexRationalInterval.point():
                    continue
                output[row][column] = output[row][column] + (
                    left[row][inner] * right[inner][column]
                )
    return output


def _serialize_sparse_complex_interval_matrix(
    matrix: Sequence[Sequence[ComplexRationalInterval]],
) -> list[dict[str, object]]:
    zero = ComplexRationalInterval.point()
    return [
        {"row": row, "column": column, **entry.serialize()}
        for row, entries in enumerate(matrix)
        for column, entry in enumerate(entries)
        if entry != zero
    ]


def enclose_exact_mode_sine_kernel(
    certificate: Mapping[str, Any],
    *,
    two_j: int,
    family: str,
    form_degree: int,
    mass_squared_interval: RationalInterval,
    slab_length: Fraction,
    series_order: int = 5,
    radical_bits: int = 80,
) -> dict[str, object]:
    """Interval-enclose one exact finite Berger sine-kernel matrix block.

    The returned coefficients enclose ``(-1)^n A^n/(2n+1)!``.  The uniform
    remainder is valid for ``0 <= tau <= slab_length`` whenever the certified
    geometric majorant has ratio below one.  A massive mass range is a runtime
    specialization and is not promoted to a physical model choice.
    """
    if certificate.get("result_id") != "BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD":
        raise ValueError("wrong exact mode-kernel certificate")
    if not 0 <= two_j <= 4:
        raise ValueError("exact mode-kernel payload covers only 0<=two_j<=4")
    if family not in ("Maxwell", "massive_two_form"):
        raise ValueError("family must be Maxwell or massive_two_form")
    if not 0 <= series_order <= 5:
        raise ValueError("series_order must lie between zero and five")
    slab_length = Fraction(slab_length)
    if slab_length <= 0:
        raise ValueError("slab_length must be positive")
    if family == "Maxwell" and mass_squared_interval != RationalInterval.point(0):
        raise ValueError("Maxwell blocks require the exact zero mass interval")
    if family == "massive_two_form" and mass_squared_interval.lower <= 0:
        raise ValueError("massive two-form blocks require a strictly positive mass-squared interval")

    block = next(
        (
            value
            for value in certificate["blocks"]
            if value["two_j"] == two_j
            and value["family"] == family
            and value["form_degree"] == form_degree
        ),
        None,
    )
    if block is None:
        raise ValueError("requested family/form-degree block is absent")
    dimension = int(block["dimension"])
    operator = _zero_complex_matrix(dimension)
    for entry in block["operator_nonzero_entries"]:
        operator[int(entry["row"])][int(entry["column"])] = _sympy_complex_interval(
            str(entry["value"]),
            mass_squared_interval=mass_squared_interval,
            radical_bits=radical_bits,
        )

    operator_norm_upper = max(
        (
            sum((entry.absolute_upper() for entry in row), Fraction(0))
            for row in operator
        ),
        default=Fraction(0),
    )
    dimensionless_norm = operator_norm_upper * slab_length * slab_length
    first_omitted_order = series_order + 1
    ratio_denominator = (2 * first_omitted_order + 2) * (2 * first_omitted_order + 3)
    ratio_upper = dimensionless_norm / ratio_denominator
    if ratio_upper >= 1:
        raise ValueError(
            "series tail majorant does not contract; reduce the slab or export more exact orders"
        )

    power = _identity_complex_matrix(dimension)
    coefficients = []
    series_rows = {int(row["series_order"]): row for row in block["series_coefficients"]}
    for order in range(series_order + 1):
        if order:
            power = _multiply_complex_interval_matrices(power, operator)
        scalar = Fraction(series_rows[order]["scalar_factor"])
        coefficient = [
            [entry.scale(scalar) for entry in row]
            for row in power
        ]
        coefficients.append(
            {
                "series_order": order,
                "tau_power": 2 * order + 1,
                "entries": _serialize_sparse_complex_interval_matrix(coefficient),
            }
        )

    first_omitted = (
        slab_length
        * dimensionless_norm**first_omitted_order
        / factorial(2 * first_omitted_order + 1)
    )
    remainder_upper = first_omitted / (1 - ratio_upper)
    return {
        "two_j": two_j,
        "family": family,
        "form_degree": form_degree,
        "dimension": dimension,
        "mass_squared_interval": mass_squared_interval.serialize(),
        "slab_length": str(slab_length),
        "radical_bits": radical_bits,
        "series_order": series_order,
        "coefficient_matrices": coefficients,
        "operator_row_sum_norm_upper": str(operator_norm_upper),
        "dimensionless_norm_upper": str(dimensionless_norm),
        "tail_ratio_upper": str(ratio_upper),
        "uniform_sine_kernel_remainder_upper": str(remainder_upper),
        "claim_boundary": "one finite exact-payload block on a caller-declared rational mass/slab domain; switches, detector profiles, form contractions and I_abc remain unbound",
    }


def _polynomial_uniform_upper(
    coefficients: Sequence[RationalInterval], slab_length: Fraction
) -> Fraction:
    return sum(
        (_absolute_upper(coefficient) * slab_length**power for power, coefficient in enumerate(coefficients)),
        Fraction(0),
    )


def _volterra_polynomial_convolution(
    source: Sequence[RationalInterval], kernel: Sequence[RationalInterval]
) -> tuple[RationalInterval, ...]:
    output = [RationalInterval.point(0) for _ in range(len(source) + len(kernel))]
    for source_power, source_coefficient in enumerate(source):
        for kernel_power, kernel_coefficient in enumerate(kernel):
            output_power = source_power + kernel_power + 1
            beta = Fraction(
                factorial(source_power) * factorial(kernel_power),
                factorial(output_power),
            )
            output[output_power] = output[output_power] + (
                source_coefficient * kernel_coefficient
            ).scale(beta)
    return tuple(output)


def evaluate_nested_green_time_convolution_interval(
    *,
    source_coefficients: Sequence[RationalInterval],
    source_remainder_upper: Fraction,
    kernel_stages: Sequence[Mapping[str, Any]],
    slab_length: Fraction,
    orientation: str,
) -> dict[str, object]:
    """Compose supplied polynomial Green-kernel enclosures causally.

    In the retarded coordinate ``x=t-t_left`` and advanced coordinate
    ``x=t_right-t``, each stage evaluates ``integral_0^x K(x-y)f(y)dy``.
    Coefficients use the exact beta-integral factor, while uniform input and
    kernel remainders are propagated on the declared finite slab.
    """
    slab_length = Fraction(slab_length)
    source_remainder_upper = Fraction(source_remainder_upper)
    if orientation not in ("retarded", "advanced"):
        raise ValueError("orientation must be retarded or advanced")
    if slab_length <= 0:
        raise ValueError("slab_length must be positive")
    if source_remainder_upper < 0:
        raise ValueError("source remainder upper bound must be nonnegative")
    if not source_coefficients:
        raise ValueError("source polynomial must contain at least one coefficient")
    if not kernel_stages:
        raise ValueError("at least one Green-kernel stage is required")

    coefficients = tuple(source_coefficients)
    remainder = source_remainder_upper
    stage_rows = []
    for stage_index, stage in enumerate(kernel_stages):
        kernel = tuple(stage.get("coefficients", ()))
        kernel_remainder = Fraction(stage.get("uniform_remainder_upper", 0))
        if not kernel:
            raise ValueError("each Green-kernel stage needs polynomial coefficients")
        if kernel_remainder < 0:
            raise ValueError("kernel remainder upper bound must be nonnegative")
        source_upper = _polynomial_uniform_upper(coefficients, slab_length)
        kernel_upper = _polynomial_uniform_upper(kernel, slab_length)
        output = _volterra_polynomial_convolution(coefficients, kernel)
        output_remainder = slab_length * (
            source_upper * kernel_remainder
            + kernel_upper * remainder
            + remainder * kernel_remainder
        )
        stage_rows.append(
            {
                "stage": stage_index,
                "kernel_label": str(stage.get("label", f"stage_{stage_index}")),
                "polynomial_coefficients": [value.serialize() for value in output],
                "uniform_remainder_upper": str(output_remainder),
            }
        )
        coefficients = output
        remainder = output_remainder

    return {
        "orientation": orientation,
        "causal_coordinate": "t-t_left" if orientation == "retarded" else "t_right-t",
        "slab_length": str(slab_length),
        "stages": stage_rows,
        "polynomial_coefficients": [value.serialize() for value in coefficients],
        "uniform_remainder_upper": str(remainder),
        "claim_boundary": "supplied finite-slab polynomial Green enclosures only; no physical Berger mode binding or recoil channel evaluated",
    }


def evaluate_recoil_shell_interval(
    *,
    two_j: int,
    detector: int,
    source_preparation: int,
    source_coupling: Fraction,
    feedback_couplings: Mapping[int, Fraction],
    inverse_berger_volume: RationalInterval,
    channel_columns: Mapping[int, Sequence[RationalInterval]],
) -> dict[str, object]:
    """Aggregate one `(a,b,two_j)` shell from enclosed `I_abc[k]` values.

    The function evaluates
      ((two_j+1)/Vol) g_b sum_c g_c^2 sum_k I_abc[two_j,k].
    It does not construct any `I_abc`; that remains the detector-profile and
    nested causal-convolution responsibility.
    """
    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    if detector not in (0, 1) or source_preparation not in (0, 1):
        raise ValueError("detector and source_preparation must be 0 or 1")
    if set(feedback_couplings) != {0, 1} or set(channel_columns) != {0, 1}:
        raise ValueError("both feedback channels c=0,1 are required")
    if inverse_berger_volume.lower <= 0:
        raise ValueError("inverse Berger volume enclosure must be positive")
    expected_columns = two_j + 1
    if any(len(channel_columns[c]) != expected_columns for c in (0, 1)):
        raise ValueError("each feedback channel must contain two_j+1 passive columns")

    feedback_rows = []
    coupled_sum = RationalInterval.point(0)
    for feedback in (0, 1):
        bare = _sum_intervals(channel_columns[feedback])
        coupling_square = Fraction(feedback_couplings[feedback]) ** 2
        coupled = bare.scale(coupling_square)
        coupled_sum = coupled_sum + coupled
        feedback_rows.append(
            {
                "feedback_emitter": feedback,
                "passive_column_count": expected_columns,
                "bare_column_sum": bare.serialize(),
                "feedback_coupling_square": str(coupling_square),
                "coupled_column_sum": coupled.serialize(),
            }
        )

    source_scaled = coupled_sum.scale(Fraction(source_coupling))
    peter_weyl_weight = inverse_berger_volume.scale(two_j + 1)
    shell_interval = source_scaled * peter_weyl_weight
    return {
        "two_j": two_j,
        "detector": detector,
        "source_preparation": source_preparation,
        "feedback_rows": feedback_rows,
        "source_coupling": str(Fraction(source_coupling)),
        "source_scaled_sum": source_scaled.serialize(),
        "peter_weyl_weight": peter_weyl_weight.serialize(),
        "shell_interval": shell_interval.serialize(),
        "claim_boundary": "aggregation of supplied channel intervals only; no detector coefficient or Green convolution evaluated",
    }
