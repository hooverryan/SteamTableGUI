from pyXSteam.XSteam import XSteam
from conversions import convert_units
from scipy.optimize import root_scalar

PROPERTY_UNITS = {
    "Temperature": ["°C","°F"],
    "Pressure": ["bar", "Pa", "kPa", "MPa", "psi"],
    "Specific Volume": ["m³/kg","ft³/lb"],
    "Internal Energy": ["kJ/kg","BTU/lb"],
    "Enthalpy": ["kJ/kg","BTU/lb"],
    "Entropy": ["kJ/(kg °C)","BTU/(lb °F)"],
    "Quality": ["frac","%"]
    }
PROPERTY = list(PROPERTY_UNITS.keys())

""" Dictionary of saturated liquid and saturated vapor functions
    Used in get_saturated_value_from_quality, get_quality_from_saturated_value,
    and is_saturated functions

    Keys: Properties used to for saturated mixtures
    Values: lambda list of saturated liquid and saturated vapor functions
"""
PFG  = {
    PROPERTY[2]: lambda l: (ST.vL_t(l), ST.vV_t(l)),
    PROPERTY[3]: lambda l: (ST.uL_t(l), ST.uV_t(l)),
    PROPERTY[4]: lambda l: (ST.hL_t(l), ST.hV_t(l)),
    PROPERTY[5]: lambda l: (ST.sL_t(l), ST.sV_t(l))
}

""" Dictionary of calculation steps for each possible combination of properties

    Keys: Property pairs
    Values: steps to calculate the state given the pair of input properties
            Each set of steps is different given the available XSteam functions
"""
CASES = {
    # Case 1 - Temperature and Pressure
    (PROPERTY[0],PROPERTY[1]): lambda t,p: [t,p,ST.v_pt(p,t),ST.u_pt(p,t),ST.h_pt(p,t),ST.s_pt(p,t),ST.x_ph(p,ST.h_pt(p,t))],
    (PROPERTY[1],PROPERTY[0]): lambda p,t: [t,p,ST.v_pt(p,t),ST.u_pt(p,t),ST.h_pt(p,t),ST.s_pt(p,t),ST.x_ph(p,ST.h_pt(p,t))],

    # Case 2 - Temperature and Specific Volume
    (PROPERTY[0],PROPERTY[2]): lambda t,v: temperature_cases(v,t,PROPERTY[2],lambda l1,l2: ST.v_pt(l1,l2)),
    (PROPERTY[2],PROPERTY[0]): lambda v,t: temperature_cases(v,t,PROPERTY[2],lambda l1,l2: ST.v_pt(l1,l2)),

    # Case 3 - Temperature and Internal Energy
    (PROPERTY[0],PROPERTY[3]): lambda t,u: temperature_cases(u,t,PROPERTY[3],lambda l1,l2: ST.u_pt(l1,l2)),
    (PROPERTY[3],PROPERTY[0]): lambda u,t: temperature_cases(u,t,PROPERTY[3],lambda l1,l2: ST.u_pt(l1,l2)),

    # Case 4 - Temperature and Enthalpy
    (PROPERTY[0],PROPERTY[4]): lambda t,h: temperature_cases(h,t,PROPERTY[4],lambda l1,l2: ST.h_pt(l1,l2)),
    (PROPERTY[4],PROPERTY[0]): lambda h,t: temperature_cases(h,t,PROPERTY[4],lambda l1,l2: ST.h_pt(l1,l2)),

    # Case 5 - Temperature and Entropy
    (PROPERTY[0],PROPERTY[5]): lambda t,s: temperature_cases(s,t,PROPERTY[5],lambda l1,l2: ST.s_pt(l1,l2)),
    (PROPERTY[5],PROPERTY[0]): lambda s,t: temperature_cases(s,t,PROPERTY[5],lambda l1,l2: ST.s_pt(l1,l2)),

    # Case 6 - Temperature and Quality
    (PROPERTY[0],PROPERTY[6]): lambda t,x: state_from_P_and_H(ST.psat_t(t),ST.h_tx(t,x)),
    (PROPERTY[6],PROPERTY[0]): lambda x,t: state_from_P_and_H(ST.psat_t(t),ST.h_tx(t,x)),

    # Case 7 - Pressure and Specific Volume
    (PROPERTY[1],PROPERTY[2]): lambda p,v: state_from_P_and_H(p,ST.h_prho(p,v)),
    (PROPERTY[2],PROPERTY[1]): lambda v,p: state_from_P_and_H(p,ST.h_prho(p,v)),

    # Case 8 - Pressure and Internal Energy
    (PROPERTY[1],PROPERTY[3]): lambda p,u: state_from_P_and_H(p,find_input_from_output(lambda x,y: ST.u_ph(x,y), u, p, u, solveForP=False)),
    (PROPERTY[3],PROPERTY[1]): lambda p,u: state_from_P_and_H(p,find_input_from_output(lambda x,y: ST.u_ph(x,y), u, p, u, solveForP=False)),

    # Case 9 - Pressure and Enthalpy
    (PROPERTY[1],PROPERTY[4]): lambda p,h: state_from_P_and_H(p,h),
    (PROPERTY[4],PROPERTY[1]): lambda h,p: state_from_P_and_H(p,h),

    # Case 10 - Pressure and Entropy
    (PROPERTY[1],PROPERTY[5]): lambda p,s: state_from_P_and_H(p,ST.h_ps(p,s)),
    (PROPERTY[5],PROPERTY[1]): lambda s,p: state_from_P_and_H(p,ST.h_ps(p,s)),

    # Case 11 - Pressure and Quality
    (PROPERTY[1],PROPERTY[6]): lambda p,x: state_from_P_and_H(p,ST.h_px(p,x)),
    (PROPERTY[6],PROPERTY[1]): lambda x,p: state_from_P_and_H(p,ST.h_px(p,x)),

    # Case 12 - Specific Volume and Internal Energy (not implemented)
    (PROPERTY[2],PROPERTY[3]): None,
    (PROPERTY[3],PROPERTY[2]): None,

    # Case 13 - Specific Volume and Enthalpy
    (PROPERTY[2],PROPERTY[4]): lambda v,h: state_from_P_and_H(ST.p_hrho(h,v),h),
    (PROPERTY[4],PROPERTY[2]): lambda h,v: state_from_P_and_H(ST.p_hrho(h,v),h),

    # Case 14 - Specific Volume and Entropy (not implemented)
    (PROPERTY[2],PROPERTY[5]): None,
    (PROPERTY[5],PROPERTY[2]): None,

    # Case 15 - Specific Volume and Quality (not implemented)
    (PROPERTY[2],PROPERTY[6]): None,
    (PROPERTY[6],PROPERTY[2]): None,

    # Case 16 - Internal Energy and Enthalpy
    (PROPERTY[3],PROPERTY[4]): lambda u,h: state_from_P_and_H(find_input_from_output(lambda x,y: ST.u_ph(x,y), u, h, h, solveForP=True),h),
    (PROPERTY[4],PROPERTY[3]): lambda h,u: state_from_P_and_H(find_input_from_output(lambda x,y: ST.u_ph(x,y), u, h, u, solveForP=True),h),

    # Case 17 - Internal Energy and Entropy
    (PROPERTY[3],PROPERTY[5]): lambda u,s: state_from_P_and_H(find_input_from_output(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),ST.h_ps(find_input_from_output(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),s)),
    (PROPERTY[5],PROPERTY[3]): lambda s,u: state_from_P_and_H(find_input_from_output(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),ST.h_ps(find_input_from_output(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),s)),

    # Case 18 - Internal Energy and Quality (not implemented)
    (PROPERTY[3],PROPERTY[6]): None,
    (PROPERTY[6],PROPERTY[3]): None,

    # Case 19 - Enthalpy and Entropy
    (PROPERTY[4],PROPERTY[5]): lambda h,s: state_from_P_and_H(ST.p_hs(h,s),h),
    (PROPERTY[5],PROPERTY[4]): lambda s,h: state_from_P_and_H(ST.p_hs(h,s),h),

    # Case 20 - Enthalpy and Quality
    (PROPERTY[4],PROPERTY[6]): lambda h,x: state_from_P_and_H(find_input_from_output(lambda x,y: ST.h_px(x,y), h, x, h, solveForP=True),h),
    (PROPERTY[6],PROPERTY[4]): lambda x,h: state_from_P_and_H(find_input_from_output(lambda x,y: ST.h_px(x,y), h, x, h, solveForP=True),h),

    # Case 21 - Entropy and Quality
    (PROPERTY[5],PROPERTY[6]): lambda s,x: state_from_P_and_H(find_input_from_output(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),ST.h_ps(find_input_from_output(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),s)),
    (PROPERTY[6],PROPERTY[5]): lambda x,s: state_from_P_and_H(find_input_from_output(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),ST.h_ps(find_input_from_output(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),s))
}

ST = XSteam(XSteam.UNIT_SYSTEM_MKS)

def find_input_from_output(func, target, fixedValue, initialGuess, solveForP=True) -> float:
    """ Finds one input argument to a state property calculation given the other input and the output
    
        Args:
            func (lambda function): specific XSteam property function (e.g., x_ph)
            target (float): the output value for the XSteam property function (e.g., x for x_ph)
            fixedValue (float): the input value that is fixed
            initialGuess (float): initial guess for the input value to be solved for
            solveForP (bool): flag whether or not to solve for pressure.  Pressure is
                              the first input (e.g., x_ph).  If pressure is known this is false.
                              If pressure is the unknown, this is true.
        
        Returns:
            (float) The input value to the function that corresponds to the other input and output
            
        Raises:
            TypeError if the function is not callable
            TypeError if the target is not numeric
    """
    if not callable(func):
        raise TypeError("func must be callable (e.g., a lambda or function).")
    if not isinstance(target, (int, float)):
        raise TypeError("target must be a number.")
    if solveForP:
        return float(root_scalar(lambda x: func(x,fixedValue) - target, x0=initialGuess).root)
    else:
        return float(root_scalar(lambda x: func(fixedValue,x) - target, x0=initialGuess).root)

def state_from_P_and_H(p,h) -> list:
    """ Generates state information from pressure and enthalpy
        
        Args:
            p (float): pressure
            h (float): enthalpy
            
        Returns:
            (list) list of state parameters (t,p,v,u,h,s,x) in the same order
                   as the PROPERTY list
    """

    t = ST.t_ph(p,h)
    v = ST.v_ph(p,h)
    u = ST.u_ph(p,h)
    s = ST.s_ph(p,h)
    x = ST.x_ph(p,h)

    return list((t,p,v,u,h,s,x))

def get_saturated_value_from_quality(x,T,prop) -> float:
    """ Returns a saturated mixture property value from temperature and quality
    
        Args:
            x (float): quality
            T (float): temperature
            prop (str): PROPERTY list item that will specify the XSteam function
                        to use (e.g., enthalpy for h_tx)
        
        Returns:
            (float) the saturated mixture property value
    """
    (f,g) = PFG[prop](T)
    return f + x*(g-f)

def get_quality_from_saturated_value(val,T,prop) -> float:
    """ Returns a quality given a saturated mixture proprety
    
        Args:
            val (float): saturated mixture property value
            T (float): temperature
            prop (str): PROPRETY list item that will specify the XSteam functions
                        to use (e.g., hL_t and hV_t for enthalpy)
        
        Returns:
            (float) the quality
    """
    (f,g) = PFG[prop](T)
    return (val-f)/(g-f)

def is_saturated(val,T,prop) -> bool:
    """ Returns whether or not the state is saturated
    
        Args:
            val (float): saturated mixture property value
            T (float): temperature
            prop (str): PROPRETY list item that will specify the XSteam functions
                        to use (e.g., hL_t and hV_t for enthalpy)
        
        Returns:
            (float) True if the state is saturated
    """
    (f,g) = PFG[prop](T)
    return val>=f and val<=g

def temperature_cases(val,T,prop,ptProperties) -> list:
    """ Generates states based on state combinations that include temperature
    
        Args:
            val (float): property value
            T (float): temperature
            prop (str): PROPRETY list item that will be used to specify the
                        XSteam functions to use
            ptProperties (lambda function): specific XSteam property function (e.g., h_pt)
        
        Returns:
            (list) list of state parameters (t,p,v,u,h,s,x) in the same order
                   as the PROPERTY list
    """

    if is_saturated(val,T,prop):
        P = ST.psat_t(T)
        X = get_quality_from_saturated_value(val,T,prop)
        v = get_saturated_value_from_quality(X,T,PROPERTY[2]) if prop!=PROPERTY[2] else val
        u = get_saturated_value_from_quality(X,T,PROPERTY[3]) if prop!=PROPERTY[3] else val
        h = get_saturated_value_from_quality(X,T,PROPERTY[4]) if prop!=PROPERTY[4] else val
        s = get_saturated_value_from_quality(X,T,PROPERTY[5]) if prop!=PROPERTY[5] else val
    else:
        P = find_input_from_output(ptProperties,val,T,val,solveForP=True)
        v = ST.v_pt(P,T) if prop!=PROPERTY[2] else val
        u = ST.u_pt(P,T) if prop!=PROPERTY[3] else val
        h = ST.h_pt(P,T) if prop!=PROPERTY[4] else val
        s = ST.s_pt(P,T) if prop!=PROPERTY[5] else val
        X = ST.x_ph(P,h)

    return list((T,P,v,u,h,s,X))

    
def get_state_property_string(state) -> str:
    """
        Args:
            state (list): list of state parameters (t,p,v,u,h,s,x) in the same
                          order as the PROPERTY list
                          
        Returns:
            (str) string of state properties
    
    """
    returnString = ""
    for s,p in zip(state,PROPERTY):
        returnString += str(p) + ": "
        for u in PROPERTY_UNITS[p]:
            returnString += "\t" + f"{convert_units(s,PROPERTY_UNITS[p][0],u):0.3f}" + " " + str(u) + ","
        returnString += "\n"

    return returnString

def get_state_properties(p1Prop,p1Val,p1Unit,p2Prop,p2Val,p2Unit) -> str:
    """ Gets the state property given two input properties
        
        The input values are immediately converted to the
        XSteam MKS unit system prior to any calculations using
        the convert_units() function.
        
        Args:
            p1Prop (str): property for Property 1
            p1Val (str): value of Property 1 from text box
            p1Unit (str): units for Property 1
            p2Prop (str): property for Property 2
            p2Val (str): value of Property 2 from text box
            p2Unit (str): units for Property 2
                          
        Returns:
            (str) string of state properties
    
    """
    p1Val = float(p1Val)
    p2Val = float(p2Val)

    p1Val = convert_units(p1Val,p1Unit,PROPERTY_UNITS[p1Prop][0])
    p2Val = convert_units(p2Val,p2Unit,PROPERTY_UNITS[p2Prop][0])


    state = CASES[(p1Prop,p2Prop)](p1Val,p2Val)
    if state is None:
        return "Selected combination of properties is not supported."
    else:
        return get_state_property_string(state)
