# coding=utf-8
'''
THIS FILE IS AUTOMATICALLY GENERATED BY A STATIC CODE GENERATION TOOL
DO NOT EDIT BY HAND

Instead edit the template:

    dev/tools/static_codegen/units_template.py
'''
from .fundamentalunits import (Unit, get_or_create_dimension,
                               standard_unit_register,
                               additional_unit_register)

{all}

Unit.automatically_register_units = False

#### FUNDAMENTAL UNITS
metre = Unit.create(get_or_create_dimension(m=1), "metre", "m")
meter = Unit.create(get_or_create_dimension(m=1), "meter", "m")
liter = Unit(0.001, dim=(meter**3).dim, name="liter", dispname="l")
litre = Unit(0.001, dim=(meter**3).dim, name="litre", dispname="l")
kilogram = Unit.create(get_or_create_dimension(kg=1), "kilogram", "kg")
kilogramme = Unit.create(get_or_create_dimension(kg=1), "kilogramme", "kg")
gram = Unit(0.001, dim=kilogram.dim, name="gram", dispname="g")
gramme = Unit(0.001, dim=kilogram.dim, name="gramme", dispname="g")
second = Unit.create(get_or_create_dimension(s=1), "second", "s")
amp = Unit.create(get_or_create_dimension(A=1), "amp", "A")
ampere = Unit.create(get_or_create_dimension(A=1), "ampere", "A")
kelvin = Unit.create(get_or_create_dimension(K=1), "kelvin", "K")
mole = Unit.create(get_or_create_dimension(mol=1), "mole", "mol")
mol = Unit.create(get_or_create_dimension(mol=1), "mol", "mol")
molar = Unit.create((mole/liter).dim, name="molar", dispname="M")
candle = Unit.create(get_or_create_dimension(candle=1), "candle", "cd")
fundamental_units = [metre, meter, gram, second, amp, kelvin, mole, candle]

{derived}
{definitions}

{base_units}
{scaled_units}
{powered_units}
{additional_units}
{all_units}

class _Celsius(object):
    '''
    A dummy object to raise errors when ``celsius`` is used. The use of
    `celsius` can lead to ambiguities when mixed with temperaturs in `kelvin`,
    so its use is no longer supported. See github issue #817 for details.
    '''
    error_text = ('The unit "celsius" is no longer supported to avoid '
                  'ambiguities when mixed with absolute temperatures defined '
                  'in Kelvin. Directly use "kelvin" when you are only '
                  'interested in temperature differences, and add the '
                  '"zero_celsius" constant from the brian2.units.constants '
                  'module if you want to convert a temperature from °C to °K.')

    def __mul__(self, other):
        raise TypeError(_Celsius.error_text)

    def __rmul__(self, other):
        raise TypeError(_Celsius.error_text)

    def __div__(self, other):
        raise TypeError(_Celsius.error_text)

    def __rdiv__(self, other):
        raise TypeError(_Celsius.error_text)

    def __pow__(self, other):
        raise TypeError(_Celsius.error_text)

    def __eq__(self, other):
        raise TypeError(_Celsius.error_text)

    def __neq__(self, other):
        raise TypeError(_Celsius.error_text)

celsius = _Celsius()

Unit.automatically_register_units = True

map(standard_unit_register.add, powered_units + scaled_units + base_units)
map(additional_unit_register.add, additional_units)
