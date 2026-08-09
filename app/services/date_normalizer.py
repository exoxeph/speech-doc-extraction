from datetime import date
import re


_MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def normalize_report_date(text: str) -> str | None:
    candidate = text.strip()
    if not candidate:
        return None

    normalized = _normalize_iso_date(candidate)
    if normalized:
        return normalized

    normalized = _normalize_named_month_date(candidate)
    if normalized:
        return normalized

    return _normalize_unambiguous_slash_date(candidate)


def _normalize_iso_date(candidate: str) -> str | None:
    match = re.match(r"^(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$", candidate)
    if not match:
        return None

    return _format_date(match.group("year"), match.group("month"), match.group("day"))


def _normalize_named_month_date(candidate: str) -> str | None:
    match = re.match(
        r"^(?P<day>\d{1,2})\s+(?P<month>[A-Za-z]+)\s+(?P<year>\d{4})$",
        candidate,
    )
    if not match:
        match = re.match(
            r"^(?P<month>[A-Za-z]+)\s+(?P<day>\d{1,2}),?\s+(?P<year>\d{4})$",
            candidate,
        )
    if not match:
        return None

    month = _MONTHS.get(match.group("month").lower())
    if month is None:
        return None

    return _format_date(match.group("year"), str(month), match.group("day"))


def _normalize_unambiguous_slash_date(candidate: str) -> str | None:
    match = re.match(r"^(?P<first>\d{1,2})/(?P<second>\d{1,2})/(?P<year>\d{4})$", candidate)
    if not match:
        return None

    first = int(match.group("first"))
    second = int(match.group("second"))
    year = match.group("year")

    if first > 12 and second <= 12:
        return _format_date(year, str(second), str(first))
    if second > 12 and first <= 12:
        return _format_date(year, str(first), str(second))

    return None


def _format_date(year: str, month: str, day: str) -> str | None:
    try:
        parsed = date(int(year), int(month), int(day))
    except ValueError:
        return None

    return parsed.isoformat()
