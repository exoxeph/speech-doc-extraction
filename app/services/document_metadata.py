import re

from app.services.models import LabReportMeta


def parse_lab_report_meta(lines: list[str]) -> LabReportMeta:
    return LabReportMeta(
        patient_name=_find_labeled_value(lines, [r"patient\s*name"]),
        age=_find_age(lines),
        sex=_find_sex(lines),
        report_date=(
            _find_labeled_value(lines, [r"report\s*date"])
            or _find_labeled_value(lines, [r"date"])
        ),
        lab_name=_find_lab_name(lines),
        reference_no=_find_labeled_value(lines, [r"reference\s*no", r"ref\s*no\.?"]),
    )


def _find_labeled_value(lines: list[str], labels: list[str]) -> str | None:
    for line in lines:
        for label in labels:
            match = re.search(
                rf"\b{label}\b\s*[:#.-]?\s*(?P<value>.+)$",
                line,
                flags=re.IGNORECASE,
            )
            if match:
                value = match.group("value").strip()
                return value or None

    return None


def _find_age(lines: list[str]) -> str | None:
    for line in lines:
        match = re.search(r"\bage\b\s*[:#.-]?\s*(?P<age>\d{1,3})\b", line, re.IGNORECASE)
        if match:
            return match.group("age")

    return None


def _find_sex(lines: list[str]) -> str | None:
    for line in lines:
        match = re.search(
            r"\bsex\b\s*[:#.-]?\s*(?P<sex>male|female|m|f)\b",
            line,
            flags=re.IGNORECASE,
        )
        if match:
            value = match.group("sex")
            if value.lower() == "m":
                return "Male"
            if value.lower() == "f":
                return "Female"
            return value[:1].upper() + value[1:].lower()

    return None


def _find_lab_name(lines: list[str]) -> str | None:
    non_empty = [line.strip() for line in lines[:5] if line.strip()]
    for index, stripped in enumerate(non_empty):
        if _is_report_title(stripped):
            if index > 0:
                return non_empty[index - 1]
            continue

        if re.search(r"\b(lab|laboratory|diagnostic|centre|center)\b", stripped, re.IGNORECASE):
            return stripped

    return None


def _is_report_title(line: str) -> bool:
    return bool(
        re.search(
            r"\b(laboratory|lab)\b.*\b(result|report)\b|\b(result|report)\b.*\b(laboratory|lab)\b",
            line,
            re.IGNORECASE,
        )
    )
