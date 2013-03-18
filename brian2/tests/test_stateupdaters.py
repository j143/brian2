from nose.tools import assert_raises
from numpy.testing.utils import assert_equal

from brian2 import *
from brian2.utils.logger import catch_logs

def test_explicit_stateupdater_parsing():
    '''
    Test the parsing of explicit state updater descriptions.
    '''
    # These are valid descriptions and should not raise errors
    updater = ExplicitStateUpdater('return x + dt * f(x, t)', priority=10)
    updater(Equations('dv/dt = -v / tau : 1'))
    updater = ExplicitStateUpdater('''x2 = x + dt * f(x, t)
                                      return x2''', priority=10)
    updater(Equations('dv/dt = -v / tau : 1'))
    updater = ExplicitStateUpdater('''x1 = g(x, t) * dW
                                      x2 = x + dt * f(x, t)
                                      return x1 + x2''', priority=10)
    updater(Equations('dv/dt = -v / tau + v * xi * tau**-.5: 1'))
    
    updater = ExplicitStateUpdater('''x_support = x + dt*f(x, t) + dt**.5 * g(x, t)
                                      g_support = g(x_support, t)
                                      k = 1/(2*dt**.5)*(g_support - g(x, t))*(dW**2)
                                      return x + dt*f(x,t) + g(x, t) * dW + k''', priority=10)
    updater(Equations('dv/dt = -v / tau + v * xi * tau**-.5: 1'))

    
    # Examples of failed parsing
    # No return statement
    assert_raises(ValueError, lambda: ExplicitStateUpdater('x + dt * f(x, t)', 10))
    # Not an assigment
    assert_raises(ValueError, lambda: ExplicitStateUpdater('''2 * x
                                                               return x + dt * f(x, t)''', 10))
    
    # doesn't separate into stochastic and non-stochastic part
    updater = ExplicitStateUpdater('''return x + dt * f(x, t) * g(x, t) * dW''', 10)
    assert_raises(ValueError, lambda: updater(Equations('')))

def test_str_repr():
    '''
    Assure that __str__ and __repr__ do not raise errors 
    '''
    for integrator in [euler, rk2, rk4]:
        assert len(str(integrator))
        assert len(repr(integrator))


def test_integrator_code():
    '''
    Check whether the returned abstract code is as expected.
    '''
    # A very simple example where the abstract code should always look the same
    eqs = Equations('dv/dt = -v / (1 * second) : 1')
    
    # Only test very basic stuff (expected number of lines and last line)
    for integrator, lines in zip([euler, rk2, rk4], [2, 3, 6]):
        code_lines = integrator(eqs).split('\n')
        assert len(code_lines) == lines
        assert code_lines[-1] == 'v = _v'

def test_priority():
    updater = ExplicitStateUpdater('return x + dt * f(x, t)', priority=10)
    # Equations that work for the state updater
    eqs = Equations('dv/dt = -v / (10*ms) : 1')
    # namespace and specifiers should not be necessary here
    namespace = {}
    specifiers = {} 
    assert updater.get_priority(eqs, namespace, specifiers) == 10
    
    # Equation with additive noise
    eqs = Equations('dv/dt = -v / (10*ms) + xi/(10*ms)**.5 : 1')
    assert updater.get_priority(eqs, namespace, specifiers) == 0
    
    can_integrate = {euler: True, rk2: False, rk4: False, 
                     milstein: True}
    for integrator, able in can_integrate.iteritems():
        if able:
            assert integrator.get_priority(eqs, namespace, specifiers) > 0
        else:
            assert integrator.get_priority(eqs, namespace, specifiers) == 0
    
    # Equation with multiplicative noise
    eqs = Equations('dv/dt = -v / (10*ms) + v*xi/(10*ms)**.5 : 1')
    assert updater.get_priority(eqs, namespace, specifiers) == 0
    
    can_integrate = {euler: False, rk2: False, rk4: False, 
                     milstein: True}
    for integrator, able in can_integrate.iteritems():
        if able:
            assert integrator.get_priority(eqs, namespace, specifiers) > 0
        else:
            assert integrator.get_priority(eqs, namespace, specifiers) == 0
    

def test_registration():
    '''
    Test state updater registration.
    '''
    # Save state before tests
    before = dict(StateUpdateMethod.stateupdaters)
    
    lazy_updater = ExplicitStateUpdater('return x', priority=10000)
    StateUpdateMethod.register('lazy', lazy_updater)
    
    # Trying to register again
    assert_raises(ValueError,
                  lambda: StateUpdateMethod.register('lazy', lazy_updater))
    
    # Trying to register something that is not a state updater
    assert_raises(ValueError,
                  lambda: StateUpdateMethod.register('foo', 'just a string'))
    
    # reset to state before the test
    StateUpdateMethod.stateupdaters = before 


def test_determination():
    '''
    Test the determination of suitable state updaters.
    '''
    # Save state before tests
    before = dict(StateUpdateMethod.stateupdaters)
    
    eqs = Equations('dv/dt = -v / (10*ms) : 1')
    # namespace and specifiers should not be necessary here
    namespace = {}
    specifiers = {}
    
    # all methods should work for these equations.
    # First, specify them explicitly (using the object)
    for integrator in (euler, rk2, rk4, milstein):
        with catch_logs() as logs:
            returned = StateUpdateMethod.determine_stateupdater(eqs,
                                                                 namespace,
                                                                 specifiers,
                                                                 method=integrator)
            assert returned is integrator
            assert len(logs) == 0
    
    # Equation with multiplicative noise, only milstein should work without
    # a warning
    eqs = Equations('dv/dt = -v / (10*ms) + v*xi*second**-.5: 1')
    for integrator in (euler, rk2, rk4):
        with catch_logs() as logs:
            returned = StateUpdateMethod.determine_stateupdater(eqs,
                                                                 namespace,
                                                                 specifiers,
                                                                 method=integrator)
            assert returned is integrator
            # We should get a warning here
            assert len(logs) == 1
            
    with catch_logs() as logs:
        returned = StateUpdateMethod.determine_stateupdater(eqs,
                                                             namespace,
                                                             specifiers,
                                                             method=milstein)
        assert returned is milstein
        # No warning here
        assert len(logs) == 0
    
    
    # Arbitrary functions (converting equations into abstract code) should
    # always work
    my_stateupdater = lambda eqs: 'return x'
    with catch_logs() as logs:
        returned = StateUpdateMethod.determine_stateupdater(eqs,
                                                             namespace,
                                                             specifiers,
                                                             method=my_stateupdater)
        assert returned is my_stateupdater
        # No warning here
        assert len(logs) == 0
    
    
    # Specification with names
    eqs = Equations('dv/dt = -v / (10*ms) : 1')
    for name, integrator in [('euler', euler), ('rk2', rk2), ('rk4', rk4),
                             ('milstein', milstein)]:
        with catch_logs() as logs:
            returned = StateUpdateMethod.determine_stateupdater(eqs,
                                                                namespace,
                                                                specifiers,
                                                                method=name)
        assert returned is integrator
        # No warning here
        assert len(logs) == 0        

    # Now all except milstein should refuse to work
    eqs = Equations('dv/dt = -v / (10*ms) + v*xi*second**-.5: 1')
    for name in ['euler', 'rk2', 'rk4']:
        assert_raises(ValueError, lambda: StateUpdateMethod.determine_stateupdater(eqs,
                                                                                   namespace,
                                                                                   specifiers,
                                                                                   method=name))
    # milstein should work
    with catch_logs() as logs:
        StateUpdateMethod.determine_stateupdater(eqs,
                                                 namespace,
                                                 specifiers,
                                                 method='milstein')
        assert len(logs) == 0
    
    # non-existing name
    assert_raises(ValueError, lambda: StateUpdateMethod.determine_stateupdater(eqs,
                                                                               namespace,
                                                                               specifiers,
                                                                               method='does_not_exist'))
    
    # Automatic state updater choice should return euler for non-stochastic
    # equations and equations with additive noise, milstein for equations with
    # multiplicative noise
    eqs = Equations('dv/dt = -v / (10*ms) : 1')
    assert StateUpdateMethod.determine_stateupdater(eqs,
                                                    namespace,
                                                    specifiers) is euler

    eqs = Equations('dv/dt = -v / (10*ms) + 0.1*second**-.5*xi: 1')
    assert StateUpdateMethod.determine_stateupdater(eqs,
                                                    namespace,
                                                    specifiers) is euler

    eqs = Equations('dv/dt = -v / (10*ms) + v*0.1*second**-.5*xi: 1')
    assert StateUpdateMethod.determine_stateupdater(eqs,
                                                    namespace,
                                                    specifiers) is milstein

    # remove all registered state updaters --> automatic choice no longer works
    StateUpdateMethod.stateupdaters = {}
    assert_raises(ValueError, lambda: StateUpdateMethod.determine_stateupdater(eqs,
                                                                               namespace,
                                                                               specifiers))

    # reset to state before the test
    StateUpdateMethod.stateupdaters = before 

def test_static_equations():
    '''
    Make sure that the integration of a (non-stochastic) differential equation
    does not depend on whether it's formulated using static equations.
    '''
    # no static equation
    eqs1 = 'dv/dt = (-v + sin(2*pi*100*Hz*t)) / (10*ms) : 1'
    # same with static equation
    eqs2 = '''dv/dt = I / (10*ms) : 1
              I = -v + sin(2*pi*100*Hz*t): 1'''
    
    methods = ['euler', 'rk2', 'rk4']
    for method in methods:
        G1 = NeuronGroup(1, eqs1, clock=Clock(), method=method)
        G1.v = 1
        G2 = NeuronGroup(1, eqs2, clock=Clock(), method=method)
        G2.v = 1
        mon1 = StateMonitor(G1, 'v', record=True)
        mon2 = StateMonitor(G2, 'v', record=True)
        net1 = Network(G1, mon1)
        net2 = Network(G2, mon2)
        net1.run(10*ms)
        net2.run(10*ms)
        assert_equal(mon1.v, mon2.v, 'Results for method %s differed!' % method)


if __name__ == '__main__':
    test_determination()
    test_explicit_stateupdater_parsing()
    test_str_repr()
    test_integrator_code()
    test_priority()
    test_registration()
    test_static_equations()
