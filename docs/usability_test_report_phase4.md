# Usability Test Report — Phase 4

**Tester:** Hnin Aung — Role 1: Research, Data Sources, Documentation, Evaluation
**Date:** 15 November 2026
**Build tested:** https://smartpantry-ai-demo.streamlit.app

## What this is

I used the deployed SmartPantry app the way an ordinary person would, and recorded everything that was confusing, inconsistent, or wrong. Where the app gave a number, I checked that number against the original government source rather than taking it on trust.

Eight findings are recorded below. Each one says what I did, what happened, why it matters, and what I suggest.

## How I tested

- Browser: Chrome, desktop, signed in with a real Supabase account
- Screens covered: Home, My Pantry, Scan Food, Food Safety, Recipes, Mochi AI
- Storage guidance tested with four foods chosen to stress different cases: a normal food, a food with no published value, a food with no individual source entry, and a food name that does not exist in the source
- Recall checker tested with the app's own example term
- Every number the app returned was checked against USDA FoodKeeper and Oregon State University Extension PNW 612

## Summary of findings

| # | Area | Severity |
|---|---|---|
| 1 | Storage guidance — source not on result | Low |
| 2 | Storage guidance — silent name mismatch | Medium |
| 3 | Storage guidance — no-data message | High |
| 4 | Storage guidance — second source not credited | Medium |
| 5 | Storage guidance — inconsistent name matching | Medium |
| 6 | Recall checker — result volume | High |
| 7 | Recall checker — search precision | High |
| 8 | Recall checker — terminated recalls shown as current | Highest |

## What was verified as correct

Before the problems, the things that worked. These were checked against the source files, not assumed.

| Food | Source value | App showed |
|---|---|---|
| Carrots | USDA FoodKeeper, 14–21 days from purchase | 14 days, use by 2026-11-29 |
| Spinach | FoodKeeper and Oregon State both 3–7 days | 3 days, use by 2026-11-18 |
| Milk | No day count published by USDA | No date given |

- In every case where a range existed, the app used the lower, more conservative end. That is the correct choice for food safety.
- Date arithmetic was correct in both cases checked.
- Use Priority changed appropriately as days remaining fell (14 days = LOW, 3 days = MEDIUM).
- The app did not invent a shelf life for milk. This is the single most important correct behaviour in the feature.
- The pantry Add Ingredient form now has purchase date, package expiration date, and storage location fields. These were missing when I tested in Phase 3 and I reported it; they have since been added.

## Finding 1 — Source is named on the section, not on the result

**Severity: Low**

**What I did:** Food Safety, entered `carrots` with purchase date 2026-11-15, clicked Check Storage Guidance.

**What happened:** The result showed "Recommended use reminder: 2026-11-29", Use Priority LOW, Days Remaining 14. The section heading above the form says "Check available FoodKeeper guidance for refrigerated ingredients", so FoodKeeper is named, but the result card itself carries no source and no link.

**Why it matters:** A user who scrolls past the heading, or screenshots the result, loses the attribution. For food safety guidance the source should travel with the number.

**Suggestion:** Print "Source: USDA FoodKeeper" beneath the result, with a link to the published data.

## Finding 2 — The app matches a different food name and does not say so

**Severity: Medium**

**What I did:** Entered `carrots`.

**What happened:** A value was returned. USDA FoodKeeper has no row called "Carrots". The row that actually holds this value is "Carrots, parsnips". The app matched that row and displayed the result with no indication that the name differed from what was typed.

**Why it matters:** Silent matching is only safe when it is always right. The user has no way to check whether the value they are reading belongs to the food in their fridge.

**Suggestion:** Show the matched source row — "Matched: Carrots, parsnips (USDA FoodKeeper)".

## Finding 3 — The no-data message reads as a failure

**Severity: High**

**What I did:** Entered `milk` with the same date.

**What happened:** The app returned "FoodKeeper rule does not support purchase-date calculations."

**Why it matters:** The behaviour here is correct and deliberate. USDA FoodKeeper publishes no day count for fresh milk, and the app refuses to estimate one rather than guessing. That refusal is the strongest safety property the feature has. But the sentence is written in developer language and reads like an error. A user cannot tell the difference between "this app is broken" and "this number does not exist anywhere".

**Suggestion:** "USDA FoodKeeper does not publish a shelf life for milk. Check the date printed on the carton." State the limit as a fact about the data, not as a limitation of the code.

## Finding 4 — Only one of the two sources is credited

**Severity: Medium**

**What I did:** Entered `spinach`.

**What happened:** The app returned 3 days, use by 2026-11-18, Use Priority MEDIUM. The value is correct: FoodKeeper and Oregon State both give 3–7 days. But FoodKeeper has no individual spinach entry — spinach sits inside the combined row "Lettuce (leaf, spinach)". The interface credits only FoodKeeper, while the project now draws on two sources.

**Why it matters:** The documented data pipeline uses USDA FoodKeeper as the primary source and Oregon State University Extension PNW 612 as a second source for foods FoodKeeper does not list individually. The app's wording does not reflect that.

**Suggestion:** Name the source per result rather than per section, so a value drawn from Oregon State is labelled as such.

## Finding 5 — Name matching is inconsistent

**Severity: Medium**

**What I did:** Entered `banana slices`.

**What happened:** "No matching FoodKeeper rule found." FoodKeeper does contain a "Bananas" entry.

**Why it matters:** `carrots` was matched to "Carrots, parsnips" — a partial match was accepted. `banana slices` was refused even though "Bananas" exists. The user cannot predict which behaviour they will get. The message also offers no next step, so a user who types a food the way they would say it in a kitchen reaches a dead end.

**Suggestion:** Apply one matching rule consistently, and offer the nearest candidate — "No exact match. Did you mean Bananas?"

## Finding 6 — Recall results are too many to use

**Severity: High**

**What I did:** Food Recall Checker, entered `peanut butter` (the app's own example term), clicked Search FDA Recalls.

**What happened:** "Found 1696 FDA recall records." The results are an unordered list with no filter, no sort, and no date ordering.

**Why it matters:** A person checking whether their food is safe will not read 1,696 records. In practice this means the feature returns nothing usable, even though the lookup itself works.

**Suggestion:** Sort newest first, show a count of active recalls separately, and allow filtering by date or status.

## Finding 7 — Search precision is low

**Severity: High**

**What I did:** Same search.

**What happened:** Many returned products contain no peanut butter. Examples returned: Coffee Toffee (ingredients include "butter (milk)"), Jolly Time Microwave popcorn Extra Butter, Trader Joe's Chocolate Chip Cookies, El Original Cheese Bread Pan de Queso Grande, and Poco Dolce Bittersweet Chocolate ("may contain traces of peanuts").

**Why it matters:** The query appears to match "peanut" and "butter" as separate words, and to match allergen statements as well as product names. A user searching their peanut butter is shown cheese bread and popcorn, which makes the feature feel unreliable even when it is working.

**Suggestion:** Match the full phrase against product name fields, and exclude or separately label matches that come only from allergen text.

## Finding 8 — Terminated recalls are shown like current ones

**Severity: Highest**

**What I did:** Expanded the second result, "1.5 oz PEANUT BUTTER COOKIES, 80/case".

**What happened:** Recall number F-2473-2016. Reason: voluntary recall due to potential contamination with Listeria monocytogenes. Recall status: **Terminated**.

**Why it matters:** This recall is from 2016 and is closed. It appears in the list looking identical to an active recall. The status is only visible after opening the record, and with 1,696 results nobody will open them one at a time. A user could believe a closed ten-year-old recall is a live danger, or — worse — stop reading the list before reaching a recall that is active.

This is the most serious finding in the report because it affects the safety-critical half of the application.

**Suggestion:** Show recall status and date on the collapsed row. Default the view to active recalls, with terminated ones behind a toggle.

## Patterns across the findings

Findings 2, 4 and 5 are the same underlying issue seen three times: the app resolves a food name against the source data and does not tell the user what it resolved to. Fixing that once would address all three.

Findings 6, 7 and 8 are the same issue on the recall side: a large, unranked, unlabelled result set. Status and date on each row, plus tighter matching, would address all three.

Finding 3 is different in kind. Nothing is broken. The app behaves correctly and explains itself badly. It is a wording change, and it is the cheapest high-value fix in the list.

## What I checked the numbers against

- USDA FSIS FoodKeeper Data (EN) — https://www.fsis.usda.gov/shared/data/EN/FoodKeeper-Data.xls
- Oregon State University Extension, *Storing Food for Safety and Quality* (PNW 612), Table 3 — https://extension.oregonstate.edu/sites/default/files/documents/pnw612.pdf

Both files are committed to this repository under `data/processed`, and the notebook `notebooks/shelf_life_data_sourcing.ipynb` reproduces the comparison.

## Limits of this test

- One tester, one browser, one session. These are findings, not measured success rates.
- Four foods tested for storage guidance and one term for recalls. Coverage is deliberately chosen to stress edge cases, not to be exhaustive.
- Scan Food, Recipes and Mochi AI were opened and their screens recorded, but not exercised with real uploads or queries in this session.
- No second tester, so nothing here is confirmed by independent observation.
