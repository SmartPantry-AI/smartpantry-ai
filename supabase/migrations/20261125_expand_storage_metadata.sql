-- SmartPantry AI - Phase 5
-- Expand storage metadata for condition-specific guidance.
-- Preserve existing pantry records and database constraints.

BEGIN;

ALTER TABLE public.pantry_items
    ADD COLUMN food_classification text,
    ADD COLUMN preparation_state text,
    ADD COLUMN package_state text,
    ADD COLUMN opened_date date,
    ADD COLUMN thawed_date date;

ALTER TABLE public.pantry_items
    ADD CONSTRAINT pantry_items_food_classification_check
        CHECK (food_classification IN ('REGULAR', 'COOKED')),

    ADD CONSTRAINT pantry_items_preparation_state_check
        CHECK (preparation_state IN ('WHOLE', 'CUT', 'RAW', 'COOKED')),

    ADD CONSTRAINT pantry_items_package_state_check
        CHECK (package_state IN ('OPENED', 'UNOPENED'));

COMMIT;

