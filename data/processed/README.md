# Processed Storage Reference Data

This folder contains cleaned and standardized storage reference datasets used by SmartPantry AI.

## Datasets

### storage_rules_clean.csv
- Contains 20 validated storage reference records.
- Used by `modules/storage_guidance.py`.
- Supports storage guidance and use-priority calculations.
- Includes rules for evaluating supported food items and storage conditions.

### foodkeeper_produce_dairy_shelf_life_clean.csv
- Contains 17 cleaned FoodKeeper reference records.
- Includes 7 standardized columns:
  - `food_name`
  - `foodkeeper_category`
  - `fridge_days_min`
  - `fridge_days_max`
  - `basis`
  - `note`
  - `source`
- Preserves missing storage-duration values rather than estimating them.
- Available for future integration with SmartPantry's storage guidance functionality.

## Data Sources

The original FoodKeeper reference dataset is preserved in `data/raw/`.

Processed datasets are maintained separately to protect original source records.

## Validation and Integration

- FoodKeeper data was cleaned and validated during Role 3, Phase 3.
- The storage guidance module currently uses `storage_rules_clean.csv`.
- The cleaned FoodKeeper dataset is not yet directly integrated into the storage guidance module.
- Storage guidance should be validated before being used for automatic expiration reminders.

**Status:** Role 3, Phase 3 completed and merged into `main`.
