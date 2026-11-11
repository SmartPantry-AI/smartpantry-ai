# SmartPantry AI - Jupyter Notebooks

This directory contains the SmartPantry AI team's Jupyter notebooks (`.ipynb`) documenting component development, data sourcing, testing, evaluation, and system integration.

**Project Status:** Phase 4 - Application Integration, Testing, and Refinement

## Purpose

The notebooks provide reproducible demonstrations of SmartPantry AI's development and testing for instructor review.

Where applicable, notebooks correspond to Python modules in the `modules/` directory.

- **Python modules** contain the application's reusable functionality.
- **Jupyter notebooks** document research, explain implementations, and demonstrate testing and evaluation.
- **The Streamlit application** provides the user-facing interface.

The notebooks serve as supporting technical documentation and testing evidence. They do not replace the application's Python modules.

## Notebook Directory

### Available Notebooks

| Notebook | Corresponding Module | Description |
|---|---|---|
| `barcode_lookup.ipynb` | `modules/barcode_lookup.py` | Barcode decoding, Open Food Facts lookups, product identification, and negative testing |
| `storage_guidance.ipynb` | `modules/storage_guidance.py` | FoodKeeper-based storage guidance, date validation, source-backed rules, and handling unsupported foods |
| `recipe_recommender.ipynb` | `modules/recipe_recommender.py` | Ingredient matching, expiration-priority scoring, recipe ranking, and evaluation |
| `image_recognition.ipynb` | `modules/image_recognition.py` | Food image recognition, recorded model evaluation, identification accuracy, and limitations |
| `ai_assistant.ipynb` | `modules/ai_assistant.py` | Mochi's conversational assistant, pantry command validation, confirmation safeguards, mocked testing, and Phase 4 findings |

### Mochi AI Assistant Testing

The `ai_assistant.ipynb` notebook documents ten test scenarios covering:

- Structured pantry command interpretation
- Quantity-schema validation and correction
- Pantry additions with and without confirmation
- Unsupported pantry actions
- Missing ingredient validation
- Zero, negative, and nonnumeric quantities
- Missing measurement units

The notebook preserves the original quantity-validation issue and demonstrates the corrected implementation.

**Testing result:** All ten tests passed when executed from a clean VS Code kernel.

These tests use mocked OpenAI responses and pantry objects. They do not verify live API behavior, persistent database operations, or complete Streamlit integration.

Mochi's testing notebook and quantity-schema correction were merged into `main` through PR #29.

### Role 1: Shelf-Life Data Sourcing

**Notebook:** `shelf_life_data_sourcing.ipynb`  
**Contributor:** Hnin Aung  
**Status:** Completed by contributor; awaiting PR #30 review and merge.

This notebook supports the storage-guidance component by researching and documenting shelf-life information from USDA FoodKeeper and supplementary Oregon State University Extension guidance.

Its responsibilities include:

- Retrieving and examining FoodKeeper data
- Converting published storage ranges into days
- Identifying the appropriate date basis for storage calculations
- Documenting missing shelf-life information
- Investigating food-name matching limitations
- Recording source attribution
- Exporting research data for review

The contributor reports successful execution from a clean kernel, with five of five validation checks passing.

**Important:** This notebook is a research and data-preparation component. Its exported dataset is separate from the processed data currently used by the application.

The notebook's export should be reviewed and validated before any values are incorporated into application datasets.

The notebook supports `modules/storage_guidance.py` but does not replace that module.

### Notebook Pending Contributor Revision

| Current Filename | Planned Filename | Corresponding Module | Description |
|---|---|---|---|
| `SmartPantry_Recall_Test.ipynb` | `recall_checker.ipynb` | `modules/recall_checker.py` | FDA recall retrieval, product matching, safety-status handling, and testing |

The recall notebook will be standardized after its contributor's revisions are completed and reviewed.

### Planned Phase 4 Notebook

| Planned Notebook | Corresponding Modules | Purpose |
|---|---|---|
| `smartpantry_integration.ipynb` | Multiple modules | Reproducible demonstrations of SmartPantry's end-to-end integration, including pantry inventory, food identification, storage guidance, recall checks, recipes, and Mochi |

The master integration notebook is planned and has not yet been added to the repository.

## How to Open

### Google Colab

1. Visit https://colab.research.google.com/.
2. Select **GitHub** and search for `SmartPantry-AI/smartpantry-ai`.
3. Select the notebook you want to open.
4. Follow the notebook's setup instructions.

**Note:** Some notebooks import Python modules or read files from the repository. Opening an individual notebook in Colab does not automatically make the entire repository available.

Clone or otherwise provide the required project files before running those notebooks.

### Jupyter Notebook / JupyterLab / VS Code

1. Clone or download the SmartPantry AI repository.
2. Open the repository folder.
3. Install dependencies from `requirements.txt`.
4. Install any additional notebook-specific dependencies identified in the notebook.
5. Open the desired `.ipynb` file.
6. Select the appropriate Python environment or kernel.
7. Follow the notebook's setup instructions and run the cells in order.

Some research notebooks require additional datasets or packages that are not necessary for the Streamlit application itself.

## Reproducibility and Testing

Each notebook should include:

1. Component overview and objectives
2. Dependencies and setup instructions
3. Inputs, processing, and expected outputs
4. Implementation or demonstration
5. Tests and observed results
6. Integration with SmartPantry
7. Limitations and future improvements

Whenever possible, demonstrations should use controlled sample data or recorded results without requiring live API calls.

Live API tests should be optional and clearly identified. Simulated results must not be presented as live verification.

Saved test results should distinguish expected behavior from observed behavior, and a successful demonstration should not be described as broader validation than the tests support.

Notebooks intended for reproducible execution should be verified from a clean kernel before submission.

### Research Data and Exports

Research notebooks may generate CSV files or other intermediate datasets.

These outputs should be stored separately from application datasets unless an integration step has been explicitly reviewed and approved.

In particular:

- Research exports should not automatically overwrite files in `data/processed/`.
- Original source references should be preserved.
- Missing values should remain identifiable.
- Date calculations must preserve their measurement basis, such as purchase date, refrigeration date, or opening date.
- Alternative data sources must be identified rather than silently substituted.

A research notebook successfully generating a dataset does not automatically mean the application is using that dataset.

## Food Safety and Data Limitations

SmartPantry uses source-backed storage guidance and recall information.

- Missing storage data must not be replaced with invented expiration dates.
- An unavailable recall service must not be treated as successful verification.
- A missing recall match does not guarantee that a food product is safe.
- Recipe rankings indicate relevance and priority, not food-safety clearance.
- Published storage ranges must not be presented as guaranteed safety dates.
- Foods without supported shelf-life values must retain an appropriate `UNKNOWN` status.
- Source-specific storage conditions and date bases must be preserved.

USDA FoodKeeper is a primary source for storage research. Oregon State University Extension provides supplementary research where additional food-specific guidance is available.

Documentation of a source does not necessarily mean its values have been integrated into the live application.

These limitations should remain visible in the relevant notebooks and application demonstrations.

## Security

- Never commit API keys, passwords, access tokens, or `.env` files containing secrets.
- Use environment variables or supported secret-management tools.
- Avoid committing personal information or sensitive user data.
- Prefer mocked API responses for repeatable automated tests.
- Do not use production user data when controlled test data is sufficient.

## Project

**SmartPantry AI**  
Houston City College  
Phase 4 - Application Integration, Testing, and Refinement

Repository: https://github.com/SmartPantry-AI/smartpantry-ai
