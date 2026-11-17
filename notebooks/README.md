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

Historical Phase 3 findings are preserved where relevant, while updated Phase 4 sections document current implementations and validation results.

## Notebook Directory

### Available Notebooks

| Notebook | Corresponding Module | Description |
|---|---|---|
| `barcode_lookup.ipynb` | `modules/barcode_lookup.py` | Barcode decoding, Open Food Facts product identification, error handling, and historical integration testing |
| `storage_guidance.ipynb` | `modules/storage_guidance.py` | FoodKeeper-based storage guidance, date validation, source-backed rules, and unsupported-food handling |
| `recipe_recommender.ipynb` | `modules/recipe_recommender.py` | Ingredient matching, expiration-priority scoring, Spoonacular integration, recall-aware filtering, recipe alternatives, and automated testing |
| `image_recognition.ipynb` | `modules/image_recognition.py` | Food image recognition, original 25-image evaluation, production-function validation, and documented limitations |
| `ai_assistant.ipynb` | `modules/ai_assistant.py` | Mochi's conversational assistant, pantry command validation, confirmation safeguards, mocked testing, and Phase 4 findings |
| `recall_checker.ipynb` | `modules/recall_checker.py` | FDA and USDA FSIS recall retrieval, product matching, recall normalization, safety-gate decisions, and automated validation |

### Mochi AI Assistant Testing

The `ai_assistant.ipynb` notebook documents Mochi's conversational assistant and pantry command validation.

The original notebook documented ten test scenarios covering:

- Structured pantry command interpretation
- Quantity-schema validation and correction
- Pantry additions with and without confirmation
- Unsupported pantry actions
- Missing ingredient validation
- Zero, negative, and nonnumeric quantities
- Missing measurement units

The notebook preserves the original quantity-validation issue and demonstrates the corrected implementation.

The updated Phase 4 notebook includes validation against the current production implementation.

**Phase 4 validation result:** 15 of 15 tests passed.

Testing uses controlled inputs, mocked OpenAI responses, and simulated pantry objects where appropriate.

These results validate the tested assistant behaviors but do not establish complete live API reliability, persistent database correctness, or end-to-end Streamlit integration.

Mochi's original testing notebook and quantity-schema correction were merged into `main` through PR #29. Subsequent notebook documentation updates are maintained separately until merged.

### Recipe Recommender Testing

The `recipe_recommender.ipynb` notebook documents the current production recipe recommendation system.

Validation covers:

- Ingredient normalization and matching
- Expiration-priority scoring
- Pantry coverage and recipe ranking
- Spoonacular response conversion and integration
- Recall-aware recipe filtering
- Recipe alternatives
- Missing or unverified ingredients
- API error handling using mocked responses

**Automated test result:** 22 of 22 tests passed in Google Colab.

The notebook imports functions from `modules/recipe_recommender.py` and runs the corresponding automated tests.

The original recipe-ranking demonstrations and historical development results are preserved.

Automated tests do not require live Spoonacular API requests. Passing mocked tests does not establish live API availability or guarantee the quality of every recommendation.

### Image Recognition Testing

The `image_recognition.ipynb` notebook documents SmartPantry's AI-powered food identification component.

The original evaluation included five baseline food images and twenty additional images with challenging lighting, positioning, and visual conditions.

**Original recorded evaluation:** 25 of 25 food images were identified correctly.

The Phase 4 notebook preserves those recorded results and includes additional production-function validation.

**Phase 4 mocked function tests:** 2 of 2 passed.

The results demonstrate successful identification within the evaluated sample. They do not establish general accuracy across all foods, packaging, environments, or image conditions.

The notebook documents limitations and distinguishes historical live-model observations from current mocked validation.

### Recall Checker Testing

The `recall_checker.ipynb` notebook documents SmartPantry's recall detection and safety-gate component.

The notebook preserves the original Phase 3 FDA research, prototype experiments, USDA investigation, and historical results while documenting the expanded Phase 4 implementation.

Current functionality includes:

- FDA food recall retrieval
- USDA FSIS recall retrieval through a third-party API
- Standardized recall records
- Product matching using available identifying information, including names, brands, UPCs, and lot codes
- Recall classification and prioritization
- Recipe eligibility decisions
- Conservative handling of incomplete recall checks

The notebook includes controlled production-function validation and automated testing through `tests/test_recall_checker.py`.

The Phase 4 implementation supports both FDA and USDA recall sources. However, the USDA service is accessed through a third-party endpoint rather than a direct official USDA API.

**Important:** The current FDA and USDA retrieval functions report `check_status="INCOMPLETE"`. Successful retrieval does not establish complete recall verification.

Products classified as `POSSIBLE_MATCH` or `RECALLED` are blocked by the recipe safety gate.

Incomplete checks are blocked by default. Limited acknowledgment behavior is available for eligible nonmatching results, but acknowledgment does not establish product safety or override a possible or confirmed recall match.

Historical development results and current production validation are documented separately.

### Role 1: Shelf-Life Data Sourcing

**Notebook:** `shelf_life_data_sourcing.ipynb`  
**Contributor:** Hnin Aung  
**Status:** Completed by contributor; PR #30 review and merge status requires confirmation.

This notebook supports the storage-guidance component by researching and documenting shelf-life information from USDA FoodKeeper and supplementary Oregon State University Extension guidance.

Its responsibilities include:

- Retrieving and examining FoodKeeper data
- Converting published storage ranges into days
- Identifying the appropriate date basis for storage calculations
- Documenting missing shelf-life information
- Investigating food-name matching limitations
- Recording source attribution
- Exporting research data for review

The contributor reported successful execution from a clean kernel, with five of five validation checks passing.

**Important:** This notebook is a research and data-preparation component. Its exported dataset is separate from the processed data currently used by the application.

The notebook's export should be reviewed and validated before any values are incorporated into application datasets.

The notebook supports `modules/storage_guidance.py` but does not replace that module.

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

When validating notebook changes that have not yet been merged into `main`, use the corresponding development branch to ensure the notebook and imported files match.

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

Historical Phase 3 code may be preserved as non-executable documentation when its purpose is to demonstrate the original development process rather than execute against the current production implementation.

Current Phase 4 validation sections should import and test the production modules rather than duplicate outdated implementations.

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

### Recall Verification Limitations

SmartPantry currently retrieves FDA recall information through the FDA API and USDA FSIS recall information through a third-party service.

Both retrieval functions report incomplete verification status. A successful API response or absence of matching recall records must not be interpreted as confirmation that a product is recall-free.

The recipe safety gate blocks confirmed or possible recall matches.

Incomplete checks are blocked by default, with limited acknowledgment behavior supported for eligible nonmatching results.

Acknowledgment does not change the underlying verification status or permit potentially recalled products.

Recall information is intended to support user awareness and safety decisions, not provide a guarantee of food safety.

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
