# VLM_eval

VLM (vision-language model) evaluation framework for image recognition. This repo contains the evaluation setup for comparing multiple multimodal approaches on tourist/travel images: **210 images**, **8 approaches**, with and without GPS metadata. It was developed for a Master's thesis in Informatics (UiO) on multimodal LLM-based tourism and cultural heritage applications.

## Repository structure

| Directory | Description |
|-----------|-------------|
| **backend/** | Image recognition FastAPI server and 8 approaches: GPT Vision Direct (strong/fast), GPT Vision + Search (strong/fast), Gemini Vision (strong/fast), Google Cloud Vision. See [backend/README.md](backend/README.md) for API, setup, and env vars. |
| **Evaluation/** | Human evaluation dataset, evaluation UI, and analysis docs. Schema and rubrics: [Evaluation/DATASET_DESCRIPTION.md](Evaluation/DATASET_DESCRIPTION.md). |
| **results/** | Batch test outputs and `results/.eval_work/inputs/` (per-image eval inputs). |
| **scripts/** | Build, preprocess, and merge scripts for the evaluation pipeline. |

## Quick start

### 1. Backend (recognition server)

```bash
cd backend
pip install -r requirements.txt
```

Configure environment variables (API keys are **not** in the repo). Copy `backend/.env.example` to `backend/.env` and fill in your keys, or set them in the environment. For Google Cloud Vision, place a service account JSON key in `backend/` (e.g. `*_key.json`); the server can use `GOOGLE_APPLICATION_CREDENTIALS` or a fallback path. See [backend/README.md](backend/README.md) for the full list.

```bash
python run_server.py
```

Server runs at `http://localhost:8000` by default.

### 2. Batch test

From the repo root (with the server running):

```bash
python batch_test.py
# Optional: --server-url http://localhost:8000  --output-dir results/my_run
```

### 3. Evaluation UI

```bash
cd Evaluation
pip install -r requirements-ui.txt
python evaluation_ui.py
```

Open the URL shown in the terminal (e.g. http://127.0.0.1:5000) to use the human evaluation interface.

## Dataset

- **210 images** (tourist/travel, with GPS EXIF); **150** are fully evaluated, 60 skipped.
- Each image is run with **8 approaches** in two modes: **with GPS** and **without GPS** (13 evaluation sections per image).
- Main evaluation output: **Evaluation/human_evaluation.json**. Per-image source files: **results/.eval_work/inputs/eval_input_*.json**.
- The images have not been uploaded to this repository as they are private and the photographers do not want them shered. The eval notebook and the human_evaluation.json are based on them though, but a rerun of a new set of images will overwrite this file and the eval notebook accordingly.

Details on ground truth, rubrics, and scoring are in [Evaluation/DATASET_DESCRIPTION.md](Evaluation/DATASET_DESCRIPTION.md).

## Secrets

API keys and credentials are **not** included in this repository. Use `backend/.env` for environment variables and a service account JSON file in `backend/` for Google Cloud Vision; both are listed in `.gitignore`. Copy `backend/.env.example` to `backend/.env` and add your values.

## Publishing this repo

To push this directory to a new GitHub repo (e.g. `VLM_eval`), run from this directory: `./push_to_github.sh`. It inits git, commits with `.gitignore` first (so `backend/.env` and `backend/*_key.json` are never committed), then pushes to `https://github.com/andreasklae/VLM_eval.git`. Edit the remote URL in the script if needed.

## License and attribution

Thesis project, University of Oslo. Data sources (e.g. Riksantikvaren, Wikipedia, Store Norske Leksikon) have their own licenses; see the main project documentation for details.
