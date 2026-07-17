from pyXSteam.XSteam import XSteam
from conversions import convertUnits
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

PFG  = {
    PROPERTY[2]: lambda l: (ST.vL_t(l), ST.vV_t(l)),
    PROPERTY[3]: lambda l: (ST.uL_t(l), ST.uV_t(l)),
    PROPERTY[4]: lambda l: (ST.hL_t(l), ST.hV_t(l)),
    PROPERTY[5]: lambda l: (ST.sL_t(l), ST.sV_t(l))
}

CASES = {
    (PROPERTY[0],PROPERTY[1]): lambda t,p: [t,p,ST.v_pt(p,t),ST.u_pt(p,t),ST.h_pt(p,t),ST.s_pt(p,t),ST.x_ph(p,ST.h_pt(p,t))],
    (PROPERTY[1],PROPERTY[0]): lambda p,t: [t,p,ST.v_pt(p,t),ST.u_pt(p,t),ST.h_pt(p,t),ST.s_pt(p,t),ST.x_ph(p,ST.h_pt(p,t))],

    (PROPERTY[0],PROPERTY[2]): lambda t,v: temperatureCases(v,t,PROPERTY[2],lambda l1,l2: ST.v_pt(l1,l2)),
    (PROPERTY[2],PROPERTY[0]): lambda v,t: temperatureCases(v,t,PROPERTY[2],lambda l1,l2: ST.v_pt(l1,l2)),

    (PROPERTY[0],PROPERTY[3]): lambda t,u: temperatureCases(u,t,PROPERTY[3],lambda l1,l2: ST.u_pt(l1,l2)),
    (PROPERTY[3],PROPERTY[0]): lambda u,t: temperatureCases(u,t,PROPERTY[3],lambda l1,l2: ST.u_pt(l1,l2)),
     
    (PROPERTY[0],PROPERTY[4]): lambda t,h: temperatureCases(h,t,PROPERTY[4],lambda l1,l2: ST.h_pt(l1,l2)),
    (PROPERTY[4],PROPERTY[0]): lambda h,t: temperatureCases(h,t,PROPERTY[4],lambda l1,l2: ST.h_pt(l1,l2)),

    (PROPERTY[0],PROPERTY[5]): lambda t,s: temperatureCases(s,t,PROPERTY[5],lambda l1,l2: ST.s_pt(l1,l2)),
    (PROPERTY[5],PROPERTY[0]): lambda s,t: temperatureCases(s,t,PROPERTY[5],lambda l1,l2: ST.s_pt(l1,l2)),

    (PROPERTY[0],PROPERTY[6]): lambda t,x: stateFromPandH(ST.psat_t(t),ST.h_tx(t,x)),
    (PROPERTY[6],PROPERTY[0]): lambda x,t: stateFromPandH(ST.psat_t(t),ST.h_tx(t,x)),

    (PROPERTY[1],PROPERTY[2]): lambda p,v: stateFromPandH(p,ST.h_prho(p,v)),
    (PROPERTY[2],PROPERTY[1]): lambda v,p: stateFromPandH(p,ST.h_prho(p,v)),

    (PROPERTY[1],PROPERTY[3]): lambda p,u: stateFromPandH(p,findInputFromOutput(lambda x,y: ST.u_ph(x,y), u, p, u, solveForP=False)),
    (PROPERTY[3],PROPERTY[1]): lambda p,u: stateFromPandH(p,findInputFromOutput(lambda x,y: ST.u_ph(x,y), u, p, u, solveForP=False)),
    
    (PROPERTY[1],PROPERTY[4]): lambda p,h: stateFromPandH(p,h),
    (PROPERTY[4],PROPERTY[1]): lambda h,p: stateFromPandH(p,h),

    (PROPERTY[1],PROPERTY[5]): lambda p,s: stateFromPandH(p,ST.h_ps(p,s)),
    (PROPERTY[5],PROPERTY[1]): lambda s,p: stateFromPandH(p,ST.h_ps(p,s)),

    (PROPERTY[1],PROPERTY[6]): lambda p,x: stateFromPandH(p,ST.h_px(p,x)),
    (PROPERTY[6],PROPERTY[1]): lambda x,p: stateFromPandH(p,ST.h_px(p,x)),

    (PROPERTY[2],PROPERTY[3]): None,
    (PROPERTY[3],PROPERTY[2]): None,
    
    (PROPERTY[2],PROPERTY[4]): lambda v,h: stateFromPandH(ST.p_hrho(h,v),h),
    (PROPERTY[4],PROPERTY[2]): lambda h,v: stateFromPandH(ST.p_hrho(h,v),h),

    (PROPERTY[2],PROPERTY[5]): None,
    (PROPERTY[5],PROPERTY[2]): None,

    (PROPERTY[2],PROPERTY[6]): None,
    (PROPERTY[6],PROPERTY[2]): None,

    (PROPERTY[3],PROPERTY[4]): lambda u,h: stateFromPandH(findInputFromOutput(lambda x,y: ST.u_ph(x,y), u, h, h, solveForP=True),h),
    (PROPERTY[4],PROPERTY[3]): lambda h,u: stateFromPandH(findInputFromOutput(lambda x,y: ST.u_ph(x,y), u, h, u, solveForP=True),h),

    (PROPERTY[3],PROPERTY[5]): lambda u,s: stateFromPandH(findInputFromOutput(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),ST.h_ps(findInputFromOutput(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),s)),
    (PROPERTY[5],PROPERTY[3]): lambda s,u: stateFromPandH(findInputFromOutput(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),ST.h_ps(findInputFromOutput(lambda x,y: ST.u_ps(x,y), u, s, u, solveForP=True),s)),

    (PROPERTY[3],PROPERTY[6]): None,
    (PROPERTY[6],PROPERTY[3]): None,

    (PROPERTY[4],PROPERTY[5]): lambda h,s: stateFromPandH(ST.p_hs(h,s),h),
    (PROPERTY[5],PROPERTY[4]): lambda s,h: stateFromPandH(ST.p_hs(h,s),h),

    (PROPERTY[4],PROPERTY[6]): lambda h,x: stateFromPandH(findInputFromOutput(lambda x,y: ST.h_px(x,y), h, x, h, solveForP=True),h),
    (PROPERTY[6],PROPERTY[4]): lambda x,h: stateFromPandH(findInputFromOutput(lambda x,y: ST.h_px(x,y), h, x, h, solveForP=True),h),

    (PROPERTY[5],PROPERTY[6]): lambda s,x: stateFromPandH(findInputFromOutput(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),ST.h_ps(findInputFromOutput(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),s)),
    (PROPERTY[6],PROPERTY[5]): lambda x,s: stateFromPandH(findInputFromOutput(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),ST.h_ps(findInputFromOutput(lambda x,y: ST.x_ps(x,y), x, s, x, solveForP=True),s))
}



ST = XSteam(XSteam.UNIT_SYSTEM_MKS)


def checkErrors(p1Prop,p1Val,p2Prop,p2Val):
    errorString = None
    if p1Prop==p2Prop:
        errorString = 'Properties must cannot be the same'
    try:
        p1Val = float(p1Val)
        p2Val = float(p2Val)
    except ValueError:
        errorString = 'Values must be numeric'
    
    return errorString

def findInputFromOutput(func, target, fixedValue, initialGuess, solveForP=True):
    if not callable(func):
        raise TypeError("func must be callable (e.g., a lambda or function).")
    if not isinstance(target, (int, float)):
        raise TypeError("target must be a number.")
    if solveForP:
        return float(root_scalar(lambda x: func(x,fixedValue) - target, x0=initialGuess).root)
    else:
        return float(root_scalar(lambda x: func(fixedValue,x) - target, x0=initialGuess).root)

def stateFromPandH(p,h):

    t = ST.t_ph(p,h)
    v = ST.v_ph(p,h)
    u = ST.u_ph(p,h)
    s = ST.s_ph(p,h)
    x = ST.x_ph(p,h)

    return list((t,p,v,u,h,s,x))

def getSaturatedValueFromQuality(x,T,prop):
    (f,g) = PFG[prop](T)
    return f + x*(g-f)

def getQualityFromSaturatedValue(val,T,prop):
    (f,g) = PFG[prop](T)
    return (val-f)/(g-f)

def isSaturated(val,T,prop):
    (f,g) = PFG[prop](T)
    return val>f and val<g

def temperatureCases(val,T,prop,ptProperties):

    if isSaturated(val,T,prop):
        P = ST.psat_t(T)
        X = getQualityFromSaturatedValue(val,T,prop)
        v = getSaturatedValueFromQuality(X,T,PROPERTY[2]) if prop!=PROPERTY[2] else val
        u = getSaturatedValueFromQuality(X,T,PROPERTY[3]) if prop!=PROPERTY[3] else val
        h = getSaturatedValueFromQuality(X,T,PROPERTY[4]) if prop!=PROPERTY[4] else val
        s = getSaturatedValueFromQuality(X,T,PROPERTY[5]) if prop!=PROPERTY[5] else val
    else:
        P = findInputFromOutput(ptProperties,val,T,val,solveForP=True)
        v = ST.v_pt(P,T) if prop!=PROPERTY[2] else val
        u = ST.u_pt(P,T) if prop!=PROPERTY[3] else val
        h = ST.h_pt(P,T) if prop!=PROPERTY[4] else val
        s = ST.s_pt(P,T) if prop!=PROPERTY[5] else val
        X = ST.x_ph(P,h)

    return list((T,P,v,u,h,s,X))

    
def steamPropertyString(state):
    returnString = ""
    for s,p in zip(state,PROPERTY):
        returnString += str(p) + ": "
        for u in PROPERTY_UNITS[p]:
            returnString += "\t" + f"{convertUnits(s,PROPERTY_UNITS[p][0],u):0.3f}" + " " + str(u) + ","
        returnString += "\n"

    return returnString

def getSteamProperties(p1Prop,p1Val,p1Unit,p2Prop,p2Val,p2Unit):
    p1Val = float(p1Val)
    p2Val = float(p2Val)

    p1Val = convertUnits(p1Val,p1Unit,PROPERTY_UNITS[p1Prop][0])
    p2Val = convertUnits(p2Val,p2Unit,PROPERTY_UNITS[p2Prop][0])


    state = CASES[(p1Prop,p2Prop)](p1Val,p2Val)
    if state is None:
        return "Invalid Combination of properties"
    else:
        return steamPropertyString(state)
