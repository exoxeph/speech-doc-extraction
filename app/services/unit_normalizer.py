_UNIT_ALIASES = {
    "gm/dl": "g/dL",
    "g/dl": "g/dL",
    "g/dL": "g/dL",
    "mg/dl": "mg/dL",
    "mg/dL": "mg/dL",
    "mg/di": "mg/dL",
    "mg/dt": "mg/dL",
    "mg/dt3": "mg/dL",
    "mg/d": "mg/dL",
    "ag/di": "mg/dL",
    "mmol/l": "mmol/L",
    "mmol/L": "mmol/L",
    "mmol/t": "mmol/L",
    "mmol/i": "mmol/L",
    "mmol/L3": "mmol/L",
    "anol/t": "mmol/L",
    "mt/min/{1.73_m2}": "mL/min/{1.73_m2}",
    "mt /min/{2-73_02)": "mL/min/{1.73_m2}",
    "10^3/ul": "10^3/uL",
    "10^3/uL": "10^3/uL",
    "10^3/µL": "10^3/uL",
}


def normalize_unit(unit: str) -> str:
    stripped = unit.strip()
    return _UNIT_ALIASES.get(stripped, stripped)
