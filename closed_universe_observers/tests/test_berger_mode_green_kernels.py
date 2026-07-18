import sympy as sp
from closed_universe_observers.generate_berger_mode_green_kernels import sine_kernel_series,wave_audit
def test_cauchy_jump_and_ode()->None:
 for j in range(3):
  for p in (0,1,2):
   a=wave_audit(j,p,sp.Integer(2));assert a["initial_value_defect_count"]==0;assert a["initial_derivative_defect_count"]==0;assert a["ode_coefficient_defect_count_through_tau9"]==0
def test_massless_zero_mode_limit()->None:
 a=wave_audit(0,0);assert a["spatial_operator_rank"]==0;assert a["kernel"].endswith("zero-eigenvalue limit tau")
def test_wrong_recurrence_sign_fails()->None:assert wave_audit(1,1,wrong_sign=True)["ode_coefficient_defect_count_through_tau9"]>0
def test_symbolic_mass_is_supported()->None:
 m=sp.Symbol("m_squared",positive=True);a=wave_audit(1,2,m);assert a["mass_squared"]=="m_squared";assert a["spatial_operator_rank"]==a["dimension"]
def test_entire_series_needs_no_diagonalization()->None:
 A=sp.Matrix([[2,1],[1,3]]);t=sp.Symbol("t");S=sine_kernel_series(A,t,2);assert sp.diff(S,t).subs(t,0)==sp.eye(2)
