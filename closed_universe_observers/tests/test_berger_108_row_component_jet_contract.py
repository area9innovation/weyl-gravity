from fractions import Fraction
import pytest
from closed_universe_observers.berger_108_row_component_jet_contract import (
    U_BERGER,
    V_BERGER,
    commutator,
    derivative,
    generator,
    multiply,
    normalize,
    scale,
)
from closed_universe_observers.generate_berger_108_row_component_jet_contract import build

ONE=(Fraction(1),Fraction(0)); SQRT10=(Fraction(0),Fraction(1))
def test_sqrt10_reduces_exactly(): assert multiply(normalize([(SQRT10,[])]),normalize([(SQRT10,[])]))=={(): (Fraction(10),Fraction(0))}
def test_factor_order_and_like_terms_are_canonical():
    a=generator("profile","f0",(1,)); b=generator("background","R0_1")
    assert normalize([(ONE,[a,b]),(ONE,[b,a])])=={tuple(sorted((a,b))):(Fraction(2),Fraction(0))}
def test_four_derivations_and_leibniz():
    f=normalize([(ONE,[generator("profile","rho0",(1,0,0))])]); r=normalize([(ONE,[generator("background","R0_1")])])
    for axis in range(4): assert derivative(multiply(f,r),axis)==normalize([(c,m) for m,c in multiply(derivative(f,axis),r).items()]+[(c,m) for m,c in multiply(f,derivative(r,axis)).items()])
def test_noncommuting_berger_frame_is_reduced_to_pbw_order():
    f=normalize([(ONE,[generator("profile","f0",(1,))])])
    assert commutator(f,1,2)==scale(derivative(f,3),U_BERGER)
    assert commutator(f,2,3)==scale(derivative(f,1),V_BERGER)
    assert commutator(f,3,1)==scale(derivative(f,2),V_BERGER)
    assert all(commutator(f,0,axis)=={} for axis in (1,2,3))
def test_berger_structure_mutations_are_detected():
    f=normalize([(ONE,[generator("background","R0_1")])])
    expected=scale(derivative(f,3),U_BERGER)
    assert commutator(f,1,2,structure_variant="drop_e1_e2")!=expected
    assert commutator(f,1,2,structure_variant="flip_e1_e2")!=expected
def test_parameters_are_flat_and_bad_indices_fail():
    p=normalize([(ONE,[generator("parameter","g0")])]); assert derivative(p,0)=={}
    with pytest.raises(ValueError): generator("profile","f0",(),(0,0,0))
def test_contract_is_complete_but_payloads_fail_closed():
    v=build(); assert len(v["carrier_contract"]["rows"])==108 and v["carrier_contract"]["pairing_rank"]==108
    assert v["activation_disposition"]["coefficient_normal_form_executable"]
    assert v["activation_disposition"]["noncommuting_berger_frame_pbw_repaired"]
    assert not v["activation_disposition"]["scalar_q1_payload_exported"] and not v["activation_disposition"]["scalar_q2_payload_exported"]
