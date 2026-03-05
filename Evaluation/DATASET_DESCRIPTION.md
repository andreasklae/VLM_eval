# Dataset Description: Human Evaluation of Image Recognition Models

## Overview

This dataset contains human evaluations of 8 multimodal image recognition approaches applied to 210 tourist/travel photographs. Each image was processed by multiple AI models (with and without GPS metadata), and a human evaluator scored every claim the models made about what's in the image and where it was taken.

**Files:**
- `human_evaluation.json` — The main output file with all human scores and ground truth snapshots.
- `../results/.eval_work/inputs/eval_input_*.json` — Per-image source files with full ground truth and raw model outputs.

---

## Image Set

- **210 images** total, of which **150 are fully evaluated** and **60 are skipped** (excluded by the evaluator as unsuitable).
- Images are tourist/travel photos from many countries (Norway, USA, Italy, Egypt, Germany, Poland, Portugal, Australia, etc.).
- Each image has GPS EXIF metadata from the camera.

---

## Approaches (Models)

Each image was run through **2 model runs**: one **with GPS metadata** provided to the model, one **without**. Each run contains **7 approaches**:

| Approach | Type | Notes |
|---|---|---|
| GPT Vision Direct (strong) | GPT-4o vision | Direct visual analysis only |
| GPT Vision Direct (fast) | GPT-4o-mini vision | Direct visual analysis only |
| GPT Vision + Search (strong) | GPT-4o + web search | Supplements with web search if visual confidence < 0.75 |
| GPT Vision + Search (fast) | GPT-4o-mini + web search | Same threshold-based supplementation |
| Gemini Vision (strong) | Gemini 2.0 Flash | Direct visual analysis |
| Gemini Vision (fast) | Gemini 2.0 Flash-Lite | Direct visual analysis |
| Google Cloud Vision | GCV API | Landmark detection, web detection, text detection only |

**Google Cloud Vision** is special: it only appears once per image (from the no-GPS run) since it doesn't use GPS. It also has no description score and a simpler claim structure.

This yields **13 evaluation sections per image**: 1 GCV + 6 approaches with GPS + 6 approaches without GPS.

---

## Ground Truth Structure

Each image has ground truth in `ground_truth`:

```json
{
  "difficulty_with_gps": "easy" | "medium" | "hard",
  "difficulty_without_gps": "easy" | "medium" | "hard",
  "image_categories": ["landmark", "urban", "nature", "art", "other"],  // multi-select
  "locations": [
    {
      "name": "Full location name",
      "hierarchy": {
        "country": "Norway",
        "region": "Nordland",
        "city": "Kjærringøy",
        "exact": "Kjærringøy kirke graveyard"
      },
      "added_by": null | "human_evaluator"
    }
  ],
  "entities": [
    {
      "name": "Entity name",
      "type": "landmark" | "building" | "natural_feature" | ... ,
      "max_specificity": 1-5,
      "importance": "high" | "medium" | "low",
      "notes": "optional notes",
      "added_by": null | "human_evaluator"
    }
  ]
}
```

**`added_by`**: `null` means the entity/location was in the original photographer-provided ground truth. `"human_evaluator"` means it was added during evaluation (e.g., the evaluator noticed a model correctly identified something not originally in the GT).

**Entity categories** (the `type` field): `landmark`, `building`, `natural_feature`, `monument`, `religious_site`, `cultural_site`, `artwork`, `public_space`, `infrastructure`, `architectural_style`, `district`, `signage`, `viewpoint`, `transport_hub`, `establishment`, `other`.

**Entity `max_specificity`** (1-5): The maximum level of specificity a model could reasonably achieve for this entity given what's visible in the image. Uses the same scale as claim specificity (see below).

**Entity `importance`**: How central this entity is to the image — `high` (dominant/primary subject), `medium` (clearly visible but secondary), `low` (minor/background element).

**`image_categories`**: Multi-select array. Categories are `landmark`, `urban`, `nature`, `art`, `other`.

---

## Evaluation Structure (`human_evaluation.json`)

Top-level structure:

```json
{
  "metadata": { "created", "last_updated", "evaluator", "total_images", "evaluated_count" },
  "images": {
    "<image_id>": {
      "image_id": 1,
      "filename": "1.jpg",
      "status": "complete" | "skipped" | "in_progress",
      "evaluator_notes": "Free text notes about this image",
      "ground_truth": { ... },  // snapshot of GT at time of evaluation
      "evals": [ ... ]          // array of 13 approach evaluations
    }
  }
}
```

Each entry in `evals`:

```json
{
  "use_gps": true | false,
  "approach_name": "GPT Vision Direct (strong)",
  "approach_index": 0,
  "location_claims": [ ... ],
  "entity_claims": [ ... ],
  "missed_locations": [],       // always empty (not used)
  "missed_entities": [],        // always empty (not used)
  "desc_score": 1-5 | null,    // null for GCV
  "desc_reason": ""             // optional free text
}
```

---

## Scoring Rubrics

### Description Score (1-5)

Applied per approach (except GCV which has no description). Measures overall quality of the model's free-text scene description.

| Score | Meaning |
|---|---|
| 1 | Confidently wrong — describes something clearly not in the image |
| 2 | Misses main subject or is irrelevant |
| 3 | Correct direction but significantly less specific than achievable |
| 4 | Correct and as specific as the image reasonably allows |
| 5 | Correctly identifies specific landmarks, context, and key visual elements |

### Location Claim Specificity (1-5)

How geographically specific the model's claim is.

| Score | Meaning |
|---|---|
| 1 | Continent or broad multi-country region |
| 2 | Country |
| 3 | Sub-country region, state, or county |
| 4 | City, town, or named area |
| 5 | Exact place, street, or landmark address |

### Entity Claim Specificity (1-5)

How specific the model's entity identification is.

| Score | Meaning |
|---|---|
| 1 | Very generic descriptor (e.g., "building") |
| 2 | Type or category (e.g., "church") |
| 3 | Recognizable sub-type (e.g., "Gothic cathedral") |
| 4 | Named category or style (e.g., "Italian Gothic cathedral") |
| 5 | Exact named identity (e.g., "Duomo di Milano") |

### Correctness (-1 to 1)

Applied to both location and entity claims.

| Score | Meaning |
|---|---|
| 1 | Fully correct at the claimed specificity level |
| 0.5 | Core identification right but minor factual errors |
| 0 | Cannot determine; too ambiguous; non-committal |
| -0.5 | Plausible but wrong: geographically or semantically close |
| -1 | Clearly incorrect: wrong country/continent, wrong entity, unrelated |

---

## Location Claims

```json
{
  "source": "photographer_location" | "subject_location",
  "model_index": 0,
  "confidence": 0.98,           // model's self-reported confidence (0-1), may be null
  "gt_ref": "photographer_position" | "depicted_subject" | "both" | null,
  "specificity": 1-5,
  "correctness": -1 | -0.5 | 0 | 0.5 | 1,
  "reason": "",                 // optional free text
  "flag": false,                // evaluator flag for review
  "also_entity": false          // see below
}
```

**`source`**: Whether the model claimed this as the photographer's location or the depicted subject's location.

**`gt_ref`**: What the claim actually refers to in the evaluator's judgment — `"photographer_position"` (where the photo was taken from), `"depicted_subject"` (what's being photographed), `"both"`, or `null` (not linked).

**`also_entity`**: When `true`, this location claim was also treated as an entity claim. Additional fields appear:
- `entity_specificity`, `entity_correctness` — scored on the entity scale
- `entity_gt_indices` — array of GT entity indices this claim matches
- `entity_scene`, `entity_bonus` — tags (see entity claims below)

These also-entity claims are **mirrored** in the `entity_claims` array with `from_location_claim: true` for convenience.

---

## Entity Claims

```json
{
  "model_index": 0,
  "confidence": 0.81,           // model's self-reported confidence, may be null
  "not_applicable": false,      // tagged N/A — irrelevant claim, excluded from scoring
  "scene_description": false,   // tagged Scene — describes the scene, not a specific entity
  "bonus": false,               // tagged Bonus — correct but not in GT; other models not penalized for missing it
  "specificity": 1-5 | null,   // null if N/A
  "correctness": -1 to 1 | null,
  "reason": "",
  "gt_indices": [0],            // array of GT entity indices this claim matches (empty if N/A/Scene/Bonus or incorrect)
  "flag": false
}
```

**Special fields for mirrored claims from location:**
```json
{
  "from_location_claim": true,
  "location_claim_index": 1,
  "location_source": "photographer_location",
  "location_model_index": 1
}
```

### Tag Logic

- **N/A**: Claim is irrelevant noise (e.g., "blue sky"). No scores needed. Excluded from analysis.
- **Scene**: Claim describes the overall scene rather than a specific entity (e.g., "European cityscape"). Still scored for specificity/correctness but doesn't need GT linking.
- **Bonus**: Claim is correct and scored, but the entity isn't in the main ground truth — other models aren't penalized for not mentioning it. Doesn't need GT linking.
- Regular claims with `correctness > 0` (and not Scene/Bonus) must be linked to at least one GT entity via `gt_indices`.

---

## GT Entity Linking

`gt_indices` is an array of integers referencing positions in `ground_truth.entities[]`. A claim can link to multiple GT entities (e.g., a vague claim like "historic building" might match several GT entries). An empty array means the claim is not linked (either incorrect, N/A, Scene, or Bonus).

---

## Key Analytical Dimensions

**Per approach:** Compare across the 13 approach sections (6 models x 2 GPS conditions + 1 GCV).

**GPS effect:** Compare `use_gps=true` vs `use_gps=false` for the same approach on the same image.

**Difficulty stratification:** Use `difficulty_with_gps` and `difficulty_without_gps` to compare performance on easy vs hard images.

**Image categories:** Use `image_categories` to compare performance across scene types (landmark, urban, nature, art).

**Entity importance:** Use `importance` (high/medium/low) to weight entity-level metrics — missing a "high" importance entity is worse than missing a "low" one.

**Entity max_specificity:** Compare model's achieved specificity against the maximum achievable specificity per GT entity.

**False negatives:** GT entities not linked by any claim in an approach represent false negatives (missed entities). Can be derived by comparing `gt_indices` across all entity claims in an approach against the full set of GT entity indices.

**Model confidence calibration:** Compare model-reported `confidence` against human-judged `correctness`.

---

## Notes and Caveats

- `missed_locations` and `missed_entities` arrays are always empty — false negative analysis must be derived from `gt_indices` linking.
- GCV (`Google Cloud Vision`) has no description, no `desc_score`, and appears only once per image (always `use_gps=false`).
- Some GT entities have `added_by: "human_evaluator"` — these were discovered during evaluation when a model correctly identified something not in the original GT.
- The `confidence` field comes from the model's own output and may be null for some approaches (especially GCV entities).
- `flag` fields were used by the evaluator to mark claims for later review and can generally be ignored in analysis.
