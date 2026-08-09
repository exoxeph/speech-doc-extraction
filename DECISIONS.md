# Design Decisions

## Decision 1 - Provider Adapters With Mock Defaults

Chosen: transcription and OCR integrations are hidden behind provider interfaces, with mock providers as the default.

Rejected: calling Whisper or OCR libraries directly from FastAPI routes.

Reason: the assignment requires a clean, testable AI service. Mock defaults make Docker and tests deterministic without credentials, model downloads, or external services.

Tradeoff: mock output does not measure model quality, so real-provider evaluation is documented separately.

## Decision 2 - Structured Lab Values

Chosen: lab values are represented as an object with `numeric`, optional `operator`, and original `raw` text.

Rejected: forcing every value into a plain float.

Reason: formats like `<0.5` carry clinically relevant qualifier information. A structured value preserves that information without guessing.

Tradeoff: the API response is slightly more verbose than a single numeric field.

## Decision 3 - Preserve Uncertain OCR Text

Chosen: unknown units and OCR-misread fields are preserved verbatim instead of corrected automatically.

Rejected: heuristic or LLM-based correction of ambiguous OCR such as `gm/di -> g/dL`.

Reason: medical extraction should prioritize traceability. The `raw_line` lets a reviewer compare structured output against OCR evidence.

Tradeoff: some outputs remain messy when OCR quality is poor.

## Decision 4 - Tesseract as the Real OCR Adapter

Chosen: use the local Tesseract CLI as the optional real OCR provider.

Rejected: commercial OCR APIs for the initial implementation.

Reason: Tesseract keeps the real-provider path local and avoids adding credentials. It is also easy to isolate in `adapters/ocr`.

Tradeoff: Tesseract quality is weak on rotated and angled images without preprocessing.

## Decision 5 - Conservative Non-Lab Detection

Chosen: require lab-report evidence before parsing numeric rows.

Rejected: parsing any line that looks like `name + number`.

Reason: receipts and menus contain numeric rows that can look table-like. Returning `document_type: unknown` is safer than fabricating medical results.

Tradeoff: some sparse lab reports may be classified as unknown until the evidence rules are expanded.
