# AnemoScan — Binary Anemia Screening Prototype

AnemoScan is a student research prototype for screening anemia from a tightly framed image of one eye's conjunctival area.

The final application is **binary only**:

- **Anemia Detected**
- **No Anemia Detected**
- a model probability is shown with the result
- no hemoglobin prediction is produced by the application
- no anemia severity category is produced by the application

This is a research prototype and **not a medical diagnosis or a substitute for laboratory hemoglobin testing**.

## Scan workflow

```text
STEP 0 — New Patient Entry
        ↓
STEP 1 — Live Camera + Quality Gate
        ↓
STEP 2 — Capture
        ↓
STEP 3 — Auto-Save
        ↓
STEP 4 — Auto-Trigger Analysis
        ↓
STEP 5 — Analyzing
        ↓
STEP 6 — Result
        ↓
STEP 7 — Scan Another / Done
```

### Camera gate

- One eye is framed at a time.
- The guide is intentionally tight around the eye/conjunctival region.
- The live quality score must reach **70/100** before capture is enabled.
- The app also checks simple framing/eye-visibility heuristics.
- If the subject is too far, too close, the eye is not clearly visible, or quality is below 70, the shutter remains locked.

The camera quality threshold (**70/100**) is separate from the AI classification threshold (**0.50 / 50% probability**).

## Model contract

The API expects the final image-only ONNX classifier in `api/model/model.onnx`.

Expected input:

```text
[1, 3, 224, 224] float32
```

Preprocessing:

```text
RGB → resize 224×224 → divide by 255 → ImageNet mean/std normalization → CHW
```

The classifier returns one output. The API converts the model output to a probability and applies a 0.50 threshold.

Example response:

```json
{
  "anemiaDetected": true,
  "anemiaProbability": 0.89,
  "status": "Anemia Detected"
}
```

The API validates the ONNX model at startup so an incompatible old Hb-regression model cannot silently be deployed.

## Project structure

```text
anemoscan/
  web/            React + TypeScript + Vite frontend
  api/            FastAPI + SQLAlchemy + ONNX Runtime backend
    model/        final binary model.onnx
    tests/        API tests
  notebooks/      original training notebooks/reference material
  docs/           project guides
  tools/          dataset utilities
```

## Local development

### API

```bash
cd api
python -m venv .venv
.venv\\Scripts\\activate        # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Web

```bash
cd web
npm ci
npm run dev
```

Set `VITE_API_URL` when the API is hosted separately. Leave it empty for same-origin/local configurations.

## Research note

The final model performance was measured on a small held-out test set during model development. Those results are not external clinical validation. Any academic report should describe the model as a screening prototype and discuss dataset size, sampling, image-quality dependence, and the need for independent validation.
