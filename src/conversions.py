from pyXSteam.XSteam import XSteam
from pyXSteam.UnitConverter import UnitConverter

UC_MKS = UnitConverter(XSteam.UNIT_SYSTEM_MKS)
UC_FLS = UnitConverter(XSteam.UNIT_SYSTEM_FLS)
UC_BARE = UnitConverter(XSteam.UNIT_SYSTEM_BARE)

CONVERSIONS = {
    # Temperature
    ("°C","°F"): lambda x: UC_FLS.fromSIunit_T(UC_MKS.toSIunit_T(x)),
    ("°F","°C"): lambda x: UC_MKS.fromSIunit_T(UC_FLS.toSIunit_T(x)),
    ("°C","°C"): lambda x: x,
    ("°F","°F"): lambda x: x,

    # Pressure
    ("bar","Pa"): lambda x: UC_MKS.toSIunit_p(x)*1e6,
    ("bar","kPa"): lambda x: UC_MKS.toSIunit_p(x)*1e3,
    ("bar","MPa"): lambda x: UC_MKS.toSIunit_p(x),
    ("bar","psi"): lambda x: UC_FLS.fromSIunit_p(UC_MKS.toSIunit_p(x)),
    ("bar","bar"): lambda x: x,
    ("Pa","bar"): lambda x: UC_MKS.fromSIunit_p(x/1e6),
    ("kPa","bar"): lambda x: UC_MKS.fromSIunit_p(x/1e3),
    ("MPa","bar"): lambda x: UC_MKS.fromSIunit_p(x),
    ("psi","bar"): lambda x: UC_MKS.fromSIunit_p(UC_FLS.toSIunit_p(x)),

    # Specific Volume
    ("m³/kg","ft³/lb"): lambda x: UC_FLS.fromSIunit_v(x),
    ("ft³/lb","m³/kg"): lambda x: UC_FLS.toSIunit_v(x),
    ("m³/kg","m³/kg"): lambda x: x,
    ("ft³/lb","ft³/lb"): lambda x: x,

    # Internal Energy/Entropy
    ("kJ/kg","BTU/lb"): lambda x: UC_FLS.fromSIunit_h(x),
    ("BTU/lb","kJ/kg"): lambda x: UC_FLS.toSIunit_h(x),
    ("kJ/kg","kJ/kg"): lambda x: x,
    ("BTU/lb","BTU/lb"): lambda x: x,

    # Entropy
    ("kJ/(kg °C)","BTU/(lb °F)"): lambda x: UC_FLS.fromSIunit_s(x),
    ("BTU/(lb °F)","kJ/(kg °C)"): lambda x: UC_FLS.toSIunit_s(x),
    ("kJ/(kg °C)","kJ/(kg °C)"): lambda x: x,
    ("BTU/(lb °F)","BTU/(lb °F)"): lambda x: x,
    
    # Quality
    ("frac","%"): lambda x: x*100,
    ("%","frac"): lambda x: x/100,
    ("frac","frac"): lambda x: x,
    ("%","%"): lambda x:x

}



def convertUnits(val,fromUnit,toUnit):
    key=(fromUnit,toUnit)
    if key in CONVERSIONS:
        return CONVERSIONS[key](val)
    else:
        raise ValueError(f"Conversion from '{fromUnit}' to '{toUnit}' is not supported.")