# Celloscope AI/ML Engineer Take-Home

A FastAPI service for speech transcription and structured medical lab-report extraction.

The implementation includes transcription and lab-report extraction endpoints. Both AI-facing workflows use configurable provider adapters, with deterministic mock providers for reproducible local and Docker testing.

## Features

### Transcription

- `POST /api/v1/transcribe`
- English (`en`) transcription
- Bengali (`bn`) transcription
- automatic language mode (`auto`)
- configurable mock and real transcription providers
- audio format validation for `wav`, `mp3`, and `m4a`
- 25 MB upload limit
- explicit handling of silence and no-speech audio

### Lab Report Extraction

- `POST /api/v1/documents/extract`
- JPEG and PNG upload validation
- configurable mock and real OCR providers
- provider-independent metadata and result models
- conservative non-lab document handling
- exact `raw_line` preservation for extracted result rows
- numeric value, unit, and date normalization

## Quick Start

### Docker

The default Docker configuration uses mock providers and requires no credentials, model downloads, or external services.

```bash
docker compose up
```

The API will be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

Docker is intentionally mock-only for submission reproducibility. It does not install Tesseract or package/download real transcription models. Real providers remain available through configuration for local/manual evaluation outside the default Docker path.

### Local Development

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -q
```

### Real Transcription Provider

The real transcription adapter uses `faster-whisper`.

```bash
python -m pip install -r requirements-real.txt
```

Copy the example environment file:

```bash
cp .env.example .env
```

Set:

```env
TRANSCRIPTION_PROVIDER=faster-whisper
```

The first real-provider run may download the Whisper model. The default Docker path does not use this provider.

### Real OCR Provider

The real OCR adapter uses the `tesseract` command-line binary. Install Tesseract locally and set:

```env
OCR_PROVIDER=tesseract
```

The default Docker path does not use this provider.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `TRANSCRIPTION_PROVIDER` | `mock` | Transcription adapter to use. Supported values: `mock`, `faster-whisper`. |
| `MOCK_TRANSCRIPTION_RESPONSE_DIR` | `testdata/mock_responses/transcription` | Directory containing mock transcription responses. |
| `OCR_PROVIDER` | `mock` | OCR adapter to use. Supported values: `mock`, `tesseract`. |
| `MOCK_OCR_RESPONSE_DIR` | `testdata/mock_responses/ocr` | Directory containing mock OCR responses. |

The repository does not contain credentials. Local `.env` files are ignored by Git.

## API

### `GET /health`

Returns service health.

```json
{"status": "ok"}
```

### `POST /api/v1/transcribe`

Transcribes an uploaded audio file.

#### Request

Multipart form data:

| Field | Description |
|---|---|
| `file` | Audio file. Supported extensions: `wav`, `mp3`, `m4a`. |
| `language` | `bn`, `en`, or `auto`. |

#### Example

```bash
curl -X POST \
  http://localhost:8000/api/v1/transcribe \
  -F "file=@testdata/audio/en_clean.mp3" \
  -F "language=en"
```

#### Response

```json
{
  "transcript": "The university laboratory opens at 9 in the morning, and the report will be ready by 5.",
  "detected_language": "en",
  "duration": 10.47,
  "provider": "faster-whisper"
}
```

#### Validation

The endpoint rejects:

- unsupported language values
- unsupported audio formats
- files larger than 25 MB

Errors are returned as structured JSON instead of stack traces.

Example:

```json
{
  "error": {
    "code": "UNSUPPORTED_AUDIO_FORMAT",
    "message": "Supported audio formats are wav, mp3 and m4a."
  }
}
```

### No-Speech Behavior

Valid audio containing silence or ambient noise is treated as a successful transcription request with no detected speech.

```json
{
  "transcript": "",
  "detected_language": null,
  "duration": 6.86,
  "provider": "faster-whisper"
}
```

This distinguishes valid audio containing no speech from an invalid upload.

### `POST /api/v1/documents/extract`

Extracts structured data from an uploaded English medical lab report image.

#### Request

Multipart form data:

| Field | Description |
|---|---|
| `file` | Report image. Supported extensions: `jpg`, `jpeg`, `png`. |

#### Example

```bash
curl -X POST \
  http://localhost:8000/api/v1/documents/extract \
  -F "file=@path/to/lab-report.jpg"
```

#### Response

```json
{
  "document_type": "lab_report",
  "meta": {
    "patient_name": "John Doe",
    "age": "28",
    "sex": "Male",
    "report_date": "2026-08-07",
    "lab_name": "ABC Diagnostic Centre",
    "reference_no": "R12345"
  },
  "results": [
    {
      "test_name": "Hemoglobin",
      "value": {
        "kind": "scalar",
        "numeric": 12.5,
        "operator": null,
        "range": null,
        "raw": "12.5"
      },
      "unit": "g/dL",
      "reference_range": "13.0 - 17.0",
      "flag": "L",
      "raw_line": "Hemoglobin    12.5    gm/dl    13.0 - 17.0    L"
    }
  ],
  "provider": "mock"
}
```

For non-lab documents, the service returns:

```json
{
  "document_type": "unknown",
  "meta": {
    "patient_name": null,
    "age": null,
    "sex": null,
    "report_date": null,
    "lab_name": null,
    "reference_no": null
  },
  "results": [],
  "provider": "mock"
}
```

## Architecture

```text
HTTP request
     |
     v
   api/
     |
     v
 services/
     |
     v
 adapters/
   /    \
mock    real
```

### `api/`

HTTP routing, upload handling, request/response schemas, and request validation.

### `services/`

Application orchestration and transcription business logic. This layer does not depend on FastAPI types.

### `adapters/`

Provider-specific integration. Model or provider SDK imports are contained within this layer.

### Provider Adapter Pattern

Transcription providers implement the same provider contract:

```text
TranscriptionProvider
  -> MockTranscriptionAdapter
  -> FasterWhisperTranscriptionAdapter
```

The active implementation is selected through environment configuration rather than source-code changes.

OCR providers follow the same pattern:

```text
OCRProvider
  -> MockOCRAdapter
  -> TesseractOCRAdapter
```

### Mock Transcription Provider

The default configuration uses a deterministic mock provider. The mock adapter reads recorded provider responses from disk, makes no network request, and loads no ML model.

This allows the full API path to run from a clean clone through Docker without credentials or model downloads.

### Mock OCR Provider

The mock OCR adapter reads recorded OCR lines from JSON fixtures and preserves line text exactly. This makes parser behavior deterministic and allows `raw_line` preservation to be tested without OCR engine variability.

## Test Data

The transcription test clips under `testdata/audio/` were recorded or generated specifically for this exercise. Reference transcripts were manually written from the intended spoken content rather than generated by the transcription model.

| Sample | Purpose |
|---|---|
| `en_clean.mp3` | baseline English transcription |
| `bn_clean.mp3` | baseline Bengali transcription |
| `en_noisy.mp3` | English speech under background noise |
| `bn_noisy.mp3` | Bengali speech under background noise |
| `bn_en_codeswitch.mp3` | Bengali-English code switching |
| `en_low_volume.mp3` | weak/low-volume speech |
| `silence.mp3` | required no-speech handling |
| `ambient_noise.mp3` | hallucination/no-speech robustness |

Additional generated WAV files are kept as lightweight smoke-test fixtures.

The set intentionally contains both straightforward and degraded inputs. Clean recordings establish baseline behavior, while noisy, low-volume, code-switched, silence, and ambient-noise samples exercise conditions likely to expose transcription and language-detection failures.

### Reference Transcripts

Ground-truth transcripts are stored in:

```text
testdata/audio/reference_transcripts.json
```

### Endpoint 2 Report Dataset

Endpoint 2 uses synthetic lab-report content derived from Synthea CSV exports. The source text fixtures are stored in:

```text
testdata/reports/source_text/
```

The Synthea-derived fixtures use synthetic patient demographics, encounter/facility data, test names, values, and units from the local Synthea dataset. Reference ranges are marked `N/A` where Synthea does not provide them.

For Endpoint 2 image testing, these synthetic report texts were displayed on-screen and photographed with a phone under varied conditions. Some captures intentionally include minor surrounding UI or screen context. This keeps the data realistic for OCR while avoiding real medical records.

The dataset also includes purpose-built synthetic fixtures for parser normalization edge cases and a non-lab receipt negative case.

Reference metadata is stored in:

```text
testdata/reports/reference_reports.json
```

## Testing

Run:

```bash
pytest -q
```

The tests cover:

- successful mock-backed transcription
- successful mock-backed document extraction
- Bengali, English, and automatic language values
- unsupported language values
- unsupported audio formats
- unsupported and malformed document uploads
- files over the 25 MB limit
- silence/no-speech behavior
- response structure
- provider selection from typed settings
- service/provider injection
- real-provider adapter mapping with a fake model
- OCR provider adapter mapping with a fake runner
- lab metadata parsing
- numeric value, unit, and date normalization
- result-row parsing with exact `raw_line` preservation
- conservative non-lab document handling
- testdata reference integrity

## Transcription Evaluation

The real `faster-whisper` provider was manually evaluated against the recorded MP3 samples.

| Sample | Language | Result |
|---|---|---|
| `en_clean.mp3` | en | Good; numbers were normalized as digits. |
| `bn_clean.mp3` | bn | Weak; language was detected as Bengali, but output used Devanagari-like transliteration instead of Bengali script. |
| `en_noisy.mp3` | en | Good; punctuation and number formatting differed from the reference. |
| `bn_noisy.mp3` | bn | Weak; language was detected as Bengali, but output used Devanagari-like transliteration. |
| `bn_en_codeswitch.mp3` | auto | Weak; detected Bengali, but mixed-script/code-switch transcription quality was poor. |
| `en_low_volume.mp3` | en | Exact match. |
| `silence.mp3` | no speech | Passed; returned an empty transcript. |
| `ambient_noise.mp3` | no speech | Passed; returned an empty transcript. |

## Value Normalization

Lab result values use a structured representation:

```json
{
  "kind": "scalar",
  "numeric": 0.5,
  "operator": "<",
  "range": null,
  "raw": "<0.5"
}
```

Range-valued results preserve both numeric endpoints instead of inventing a scalar:

```json
{
  "kind": "range",
  "numeric": null,
  "operator": null,
  "range": {
    "lower": 0.8,
    "upper": 1.2
  },
  "raw": "0.8 - 1.2"
}
```

Supported value formats include plain decimals, comma thousands, qualified values such as `<0.5`, simple scientific notation such as `1.2 x 10^3`, and numeric ranges such as `0.8 - 1.2`.

Malformed or ambiguous OCR values are not guessed. Unknown units are preserved verbatim, and only known aliases such as `gm/dl -> g/dL` are canonicalized.

## Document OCR Evaluation

The real `tesseract` OCR provider was manually evaluated against the acquired Endpoint 2 report images.

| Sample | Document type | Results | Result |
|---|---|---:|---|
| `report_01_standard_clean.jpg` | `lab_report` | 9 | Good metadata and structured rows; one GFR test name is split/noisy from OCR. |
| `report_01_standard_angled.jpg` | `lab_report` | 8 | Mostly usable; patient name was missed and some unit/range OCR noise remains. |
| `report_02_complex_dark.jpg` | `lab_report` | 7 | Degraded OCR; parser recovers rows, but some values are OCR-misread. |
| `report_02_complex_cropped.jpg` | `lab_report` | 4 | Header is cropped out, so metadata is null; partial rows are recovered. |
| `report_03_alternate_rotated.jpg` | `lab_report` | 7 | Recovered via OCR fallback; metadata is partial and OCR text is noisy. |
| `report_04_normalization_clean.jpg` | `lab_report` | 5 | Scalar, qualified, thousands, and range values are represented; OCR misreads are preserved rather than corrected. |
| `report_04_normalization_angled.jpg` | `lab_report` | 1 | OCR quality is poor; only one noisy row is recovered. |
| `not_lab_receipt.jpg` | `unknown` | 0 | Passed non-lab handling; no fake lab results are produced. |

Observed OCR-level limitations are intentionally not corrected using fixture source knowledge. For example, Tesseract read `CRP <0.5` as `RP <8.5`, and read `1.2 x 10^3` as `1.2 x 1043`; the service preserves the OCR evidence instead of silently substituting expected source text.

## Design Decisions

Consequential implementation decisions and rejected alternatives are documented in [`DECISIONS.md`](DECISIONS.md).

## Known Limitations

- Bengali transcription quality is currently weak with `faster-whisper`; the model detects Bengali but returns Devanagari-like transliteration for the recorded samples.
- Code-switched Bengali-English audio is unreliable with the current real provider.
- The evaluation dataset is intentionally small and is not a statistically representative ASR benchmark.
- Real-provider execution may require network access for the first model download. The default Docker configuration uses the mock provider.
- Tesseract OCR works on clean synthetic reports but degrades on rotated and angled images.
- The parser preserves OCR mistakes in `raw_line` and unknown units rather than silently correcting them.
