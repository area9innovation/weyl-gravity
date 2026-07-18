from fractions import Fraction
import sympy as sp
from closed_universe_observers.generate_berger_temporal_green_order_preflight import cosine_polynomial, extreme_positive_charge_eigenvalue, first_contractive_order
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import laplacian

def test_top_extreme_charge_witness():
    assert extreme_positive_charge_eigenvalue(138) == Fraction(196000, 9)

def test_extreme_charge_formula_matches_spectral_engine():
    root_two = sp.sqrt(2)
    helicity = sp.Matrix([[1/root_two, 0, 1/root_two], [sp.I/root_two, 0, -sp.I/root_two], [0, 1, 0]])
    for two_j in range(5):
        dimension = two_j + 1
        transform = sp.kronecker_product(helicity, sp.eye(dimension))
        operator = sp.simplify(transform.conjugate().T * laplacian(two_j, 1) * transform)
        assert operator[two_j, two_j] == sp.Rational(extreme_positive_charge_eigenvalue(two_j).numerator, extreme_positive_charge_eigenvalue(two_j).denominator)

def test_degree_ten_error_lower_bounds_are_positive():
    lam = extreme_positive_charge_eigenvalue(138)
    assert all(abs(cosine_polynomial(lam * tau**2)) - 1 > 0 for tau in (Fraction(1, 8), Fraction(5, 24)))

def test_required_orders_and_clock_power():
    lam = extreme_positive_charge_eigenvalue(138)
    assert first_contractive_order(lam * Fraction(1, 8)**2) == 8
    assert first_contractive_order(lam * Fraction(5, 24)**2) == 14
