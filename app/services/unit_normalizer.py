_UNIT_ALIASES = {
    "gm/dl": "g/dL",
    "g/dl": "g/dL",
    "g/dL": "g/dL",
    "mg/dl": "mg/dL",
    "mg/dL": "mg/dL",
    "mmol/l": "mmol/L",
    "mmol/L": "mmol/L",
    "10^3/ul": "10^3/uL",
    "10^3/uL": "10^3/uL",
    "10^3/µL": "10^3/uL",
}


def normalize_unit(unit: str) -> str:
    stripped = unit.strip()
    return _UNIT_ALIASES.get(stripped, stripped)
