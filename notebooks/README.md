# SmartPantry AI - Jupyter Notebooks

This directory contains the SmartPantry AI team's Jupyter notebooks (`.ipynb`) documenting component development, data sourcing, testing, evaluation, and system integration.

**Project Status:** Phase 4 - Application Integration and Refinement

## Purpose

The notebooks provide reproducible demonstrations of SmartPantry AI's functionality for instructor review.

Where applicable, notebooks correspond to Python modules in the `modules/` directory.

- **Python modules** contain the application's reusable functionality.
- **Jupyter notebooks** explain, demonstrate, and evaluate that functionality.
- **The Streamlit application** provides the user-facing interface.

The notebooks are supporting technical documentation, not replacements for the application's Python modules.

## Notebook Directory

| Notebook | Corresponding Module | Description |
|---|---|---|
| `barcode_lookup.ipynb` | `modules/barcode_lookup.py` | Barcode decoding, Open Food Facts lookups, and negative testing |
| `storage_guidance.ipynb` | `modules/storage_guidance.py` | FoodKeeper-based storage guidance, date validation, and handling unsupported foods |
| `recipe_recommender.ipynb` | `modules/recipe_recommender.py` | Ingredient matching, expiration-priority scoring, recipe ranking, and evaluation |
| `image_recognition.ipynb` | `modules/image_recognition.py` | Food image recognition, recorded model evaluation, and identification accuracy |

### Notebooks Pending Renaming

The following notebooks are being updated by their contributors. Their filenames will be standardized after those revisions are complete.

| Current Filename | Planned Filename | Purpose |
|---|---|---|
| `Role1_Shelf_Life_Data_Sourcing_Hnin.ipynb` | `shelf_life_data_sourcing.ipynb` | USDA FoodKeeper research, data preparation, and source documentation |
| `SmartPantry_Recall_Test.ipynb` | `recall_checker.ipynb` | FDA recall retrieval, product matching, safety-status handling, and testing |

The shelf-life research notebook supports `modules/storage_guidance.py` but is not a separate application module.

### Planned Phase 4 Notebooks

| Planned Notebook | Corresponding Module | Purpose |
|---|---|---|
| `ai_assistant.ipynb` | `modules/ai_assistant.py` | Mochi assistant behavior, prompt design, safety constraints, testing, and planned integration with SmartPantry services |
| `smartpantry_integration.ipynb` | Multiple modules | Reproducible end-to-end demonstrations of SmartPantry's integrated architecture |

These notebooks are planned and have not yet been added to the repository.

## How to Open

### Google Colab

1. Visit https://colab.research.google.com/.
2. Select **GitHub** and search for `SmartPantry-AI/smartpantry-ai`.
3. Select the notebook you want to open.
4. Follow that notebook's setup instructions.

**Note:** Some notebooks import Python modules or read files from the repository. Opening an individual notebook in Colab does not automatically make the entire repository available. Clone or otherwise provide the required project files before running those notebooks.

### Jupyter Notebook / JupyterLab / VS Code

1. Clone or download the SmartPantry AI repository.
2. Open the repository folder.
3. Install the required dependencies from `requirements.txt`.
4. Open the desired `.ipynb` file.
5. Follow the notebook's setup instructions and run the cells in order.

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

## Food Safety and Data Limitations

SmartPantry uses source-backed storage guidance and recall information.

- Missing storage data must not be replaced with invented expiration dates.
- An unavailable recall service must not be treated as successful verification.
- A missing recall match does not guarantee that a food product is safe.
- Recipe rankings indicate relevance and priority, not food-safety clearance.

These limitations should remain visible in the relevant notebooks and application demonstrations.

## Security

- Never commit API keys, passwords, access tokens, or `.env` files containing secrets.
- Use environment variables or supported secret-management tools.
- Avoid committing personal information or sensitive user data.
- Prefer mocked API responses for repeatable automated tests.

## Project

**SmartPantry AI**  
Houston City College  
Phase 4 - Application Integration, Testing, and Refinement

Repository: https://github.com/SmartPantry-AI/smartpantry-ai
