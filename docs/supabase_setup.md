# SmartPantry AI: Supabase Database Setup

## Overview

SmartPantry AI uses Supabase PostgreSQL for persistent pantry storage and Supabase Authentication for individual user accounts.

Each authenticated user has a separate pantry. Row Level Security (RLS) policies restrict access to pantry records based on the authenticated user's ID.

## Database Architecture

SmartPantry currently includes two database implementations:

- **Supabase PostgreSQL:** The current backend for authenticated user pantry storage.
- **SQLite:** An earlier local pantry implementation retained for development and testing.

The SQLite databases are not intended to replace Supabase for authenticated user storage.

## Pantry Items Table

The `public.pantry_items` table stores pantry inventory associated with individual users.

The application uses pantry information such as ingredient names, quantities, units, purchase dates, expiration dates, storage locations, and preparation dates.

The exact table schema and constraints should be verified against the Supabase project before reproducing the complete database setup.

## Prepared Date Column

The `prepared_date` column supports storage guidance for cooked foods and leftovers.

This field:

- Uses the PostgreSQL `DATE` type.
- Allows `NULL` values for items without a confirmed preparation date.
- Is populated when a user enters a preparation date for cooked food or leftovers.
- Is passed through the pantry database module when a new item is saved.

### Schema Update

For an existing `public.pantry_items` table, run the following SQL in the Supabase SQL Editor if the column is missing:

```sql
ALTER TABLE public.pantry_items
ADD COLUMN IF NOT EXISTS prepared_date DATE;
```

This statement adds the column without requiring existing pantry records to have a preparation date.

## Storage Guidance Integration

SmartPantry uses the pantry item's stored dates and food information to evaluate eligible storage-guidance rules.

The application currently references three research datasets:

1. USDA FoodKeeper
2. FoodSafety.gov cold food storage guidance
3. Oregon State University Extension storage guidance

Not every research record supports automatic reminders.

For eligible cooked meat and poultry leftovers, FoodSafety.gov guidance can generate a reminder when a confirmed `prepared_date` is available.

Storage estimates and reminders are informational and are not guarantees of food safety.

## Authentication and Security

Supabase Authentication supports individual user accounts.

Row Level Security policies should ensure that users can access and modify only their own pantry records.

Database ownership must be determined from the authenticated user identity rather than an arbitrary user ID supplied by the interface.

## Development Notes

- Existing SQLite database files are being retained while legacy dependencies are reviewed.
- The Supabase database is the current backend for authenticated pantry storage.
- The `prepared_date` field is optional.
- Database schema changes should be documented and tested before deployment.
- API keys, service-role credentials, and other secrets must not be committed to GitHub.

## Verification Checklist

- [x] `prepared_date` column added to the existing Supabase project.
- [x] Pantry insertion supports an optional preparation date.
- [x] Automated tests cover insertion with a preparation date.
- [x] Manual entry supports preparation dates for cooked food and leftovers.
- [x] Storage guidance displays eligible leftover reminders.
- [ ] Complete Supabase schema and RLS policies documented for reproducible setup.
