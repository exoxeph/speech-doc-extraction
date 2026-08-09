# Tesseract OCR Evaluation

Real OCR provider: `tesseract`

Synthetic report samples were evaluated through `DocumentExtractionService`, not by reading OCR output manually outside the application path.

| Sample | Outcome |
|---|---|
| `report_clean.jpg` | Detected as `lab_report`; metadata extracted; 3 result rows extracted. OCR misread `gm/dl` as `gm/di`, which was preserved verbatim. |
| `report_dark.jpg` | Detected as `lab_report`; metadata extracted; 3 result rows extracted. Similar unit OCR errors to the clean report. |
| `report_cropped.jpg` | Detected as `lab_report`; metadata extracted; 3 result rows extracted. |
| `report_angled.jpg` | Detected as `lab_report`; metadata partially extracted; 2 result rows extracted. OCR corrupted the patient name and one WBC value. |
| `report_rotated.jpg` | Detected as `lab_report`; metadata and result row were significantly corrupted by OCR. |
| `not_lab_report.jpg` | Detected as `unknown`; no metadata or result rows emitted. |

The parser preserves OCR evidence in `raw_line` and does not correct OCR-misread units or values automatically. This is deliberate: incorrect OCR corrections would create unsupported medical data guesses.
