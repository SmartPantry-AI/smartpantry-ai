# SmartPantry AI - Barcode Data Source Evaluation

## Overview

**Project:** SmartPantry AI  
**Phase:** Phase 5 - Final Refinement  
**Evaluation Date:** November 25, 2026  
**Module:** `modules/barcode_lookup.py`  
**Current Data Provider:** Open Food Facts  
**Alternative Data Provider:** USDA FoodData Central  
**Evaluation Type:** Technical Feasibility and Comparative Analysis  
**Implementation Status:** Deferred - Pending Further Evaluation  

## 1. Objective

The purpose of this evaluation was to determine whether integrating the USDA FoodData Central Global Branded Food Products Database could improve SmartPantry's existing barcode-based product identification.

The investigation focused on:

- Barcode retrieval and GTIN normalization.
- Product metadata availability and quality.
- Product record freshness.
- API response structure and compatibility.
- Potential effects on downstream SmartPantry modules.
- Implementation complexity and licensing considerations.

## 2. Research Contribution

The investigation was initiated following research conducted by Hnin Aung during Phase 5 of the SmartPantry AI project.

Her research identified USDA FoodData Central as a potential primary barcode data provider, with Open Food Facts serving as a fallback.

The recommendation was subsequently evaluated through manual database searches, live API requests, and comparative analysis to determine its suitability for the existing SmartPantry architecture.

## 3. Evaluation Methodology

Three packaged food products previously tested through SmartPantry's Open Food Facts integration were selected for a controlled comparison.

| Product | Original UPC-A |
|---|---|
| Kraft Mac & Cheese | `021000653713` |
| Cheez-It Original Crackers | `024100705665` |
| Knorr Pasta Sides Alfredo | `041000022531` |

The evaluation consisted of:

1. Reviewing USDA FoodData Central API documentation.
2. Performing manual searches through the USDA website.
3. Investigating equivalent GTIN representations.
4. Performing four live USDA API requests.
5. Performing three live Open Food Facts API requests.
6. Comparing product retrieval, metadata availability, descriptive quality, and record modification dates.
7. Evaluating architectural compatibility and implementation risks.

A total of seven live API requests were performed.

No application source code, database records, or existing integrations were modified during this evaluation.

The results represent a limited three-product sample and should not be interpreted as a comprehensive measure of database accuracy, coverage, or reliability.

## 4. USDA FoodData Central API Validation

### 4.1 API Configuration

- **Endpoint:** `https://api.nal.usda.gov/fdc/v1/foods/search`
- **HTTP Method:** GET
- **Authentication:** Public DEMO_KEY
- **Data Type:** Branded
- **Response Format:** JSON

The search endpoint returned product metadata directly, without requiring a separate food details request for the evaluated records.

### 4.2 Live API Request Results

| Test | Product | Query | Total Hits | FDC ID | Result |
|---|---|---|---:|---|---|
| USDA-01 | Kraft | `021000653713` | 1 | 2631957 | Exact match |
| USDA-02 | Cheez-It | `024100705665` | 0 | N/A | No match |
| USDA-03 | Cheez-It | `00024100705665` | 1 | 2774117 | Equivalent GTIN match |
| USDA-04 | Knorr | `041000022531` | 1 | 394736 | Exact match |

All four requests returned valid JSON responses. The unsuccessful Cheez-It lookup represented an empty search result rather than an API failure.

### 4.3 Retrieved Product Metadata

| Field | Kraft | Cheez-It | Knorr |
|---|---|---|---|
| Product description | THICK 'N CREAMY MACARONI & CHEESE SAUCE MIX, THICK 'N CREAMY | Kellogg's Cheez It Crackers Original 7oz | PASTA SIDES ALFREDO |
| Brand | KRAFT | Kellogg's Cheez It | Not provided |
| Brand owner | Kraft Heinz Foods Company | Kellogg Company US | Lipton |
| Category | Pasta Dinners | Biscuits/Cookies | Pasta Dinners |
| Package weight | 7.25 oz/206 g | 7 ONZ | Not provided |
| Modified date | 2023-07-10 | 2026-06-22 | 2018-04-11 |
| Published date | 2023-09-14 | 2026-07-23 | 2019-04-01 |
| Data source | LI | GDSN | LI |

### 4.4 API Field Mapping

The USDA response contains a list of product dictionaries within the `foods` field.

The following mapping was established using the actual API responses:

| SmartPantry Field | USDA Field |
|---|---|
| `barcode` | Original scanned barcode |
| `barcode_type` | OpenCV decoding result |
| `product_name` | `description` |
| `brand` | `brandName` |
| `source_category` | `foodCategory` |
| `quantity` | `packageWeight` |
| `product_data_source` | USDA FoodData Central |
| `input_method` | Existing SmartPantry value |
| `user_confirmed` | Existing SmartPantry confirmation workflow |

The returned `gtinUpc` field would be used to validate product identity against the original scanned barcode.

### 4.5 Key Findings

- All three products were located after accounting for equivalent GTIN representations.
- Two of three products were retrieved using their original UPC-A.
- Cheez-It required an equivalent GTIN-14 representation.
- Two of three products contained all evaluated product metadata fields.
- The Knorr response omitted both `brandName` and `packageWeight`.
- Product record modification dates varied significantly.
- No HTTP or JSON parsing failures were observed.

Missing metadata must not be replaced with unrelated fields. Brand ownership is not equivalent to brand identity, serving size is not equivalent to package weight, and database modification dates are not product expiration dates.

### 4.6 USDA Validation Summary

| Metric | Observed Result |
|---|---|
| Live API requests | 4 |
| Valid JSON responses | 4/4 |
| Products located using original UPC-A | 2/3 |
| Products located after GTIN normalization | 3/3 |
| Products with complete evaluated metadata | 2/3 |
| HTTP or JSON failures observed | 0 |

These findings establish preliminary technical feasibility but do not demonstrate overall database accuracy or production readiness.

## 5. Open Food Facts API Validation

### 5.1 API Configuration

- **Endpoint:** `https://world.openfoodfacts.org/api/v3/product/{barcode}.json`
- **HTTP Method:** GET
- **Authentication:** Not required for these read-only requests
- **Response Format:** JSON
- **Requested Fields:** `code`, `product_name`, `brands`, `categories`, `quantity`, `last_modified_t`

The requested fields were limited to relevant product metadata and record modification timestamps to support direct comparison with USDA FoodData Central.

### 5.2 Live API Request Results

| Test | Product | Original UPC-A | Returned GTIN-13 | Result |
|---|---|---|---|---|
| OFF-01 | Kraft | `021000653713` | `0021000653713` | Successful |
| OFF-02 | Cheez-It | `024100705665` | `0024100705665` | Successful |
| OFF-03 | Knorr | `041000022531` | `0041000022531` | Successful |

All three requests returned valid JSON responses with a status of `success_with_warnings`.

Each response included the warning:

`different_normalized_product_code`

The API classified the warning's impact as `none`. All three returned identifiers were equivalent to their original scanned UPC-A representations.

### 5.3 Retrieved Product Metadata

| Field | Kraft | Cheez-It | Knorr |
|---|---|---|---|
| Product name | mac & cheese | ORIGINAL | Fettuccine in a Creamy Parmesan & Romano Flavored Cheese Sauce |
| Brand | Kraft | Cheez-It | Knorr |
| Category | Pastas, Macaroni and cheese | Crackers | Pasta dishes, Pastas, Undefined |
| Quantity | 206 g | 7 oz | 64 g |
| Last modified | July 2026 | June 2026 | October 2026 |
| Data provider | Open Food Facts | Open Food Facts | Open Food Facts |

### 5.4 Key Findings

- All three products were retrieved using their original UPC-A.
- Open Food Facts automatically normalized the submitted barcodes to equivalent GTIN-13 representations.
- All three products contained the evaluated metadata fields.
- All three records had more recent modification dates than their corresponding USDA records.
- The Cheez-It product name, `ORIGINAL`, demonstrated that metadata availability does not guarantee descriptive quality.
- The Knorr quantity of 64 g requires verification against the physical packaging because it matches the serving size reported by USDA.
- No HTTP or JSON parsing failures were observed.

### 5.5 Open Food Facts Validation Summary

| Metric | Observed Result |
|---|---|
| Live API requests | 3 |
| Valid JSON responses | 3/3 |
| Products located using original UPC-A | 3/3 |
| Products with complete evaluated metadata | 3/3 |
| Automatic barcode normalization | 3/3 |
| HTTP or JSON failures observed | 0 |

## 6. Comparative Results

### 6.1 Quantitative Comparison

| Evaluation Criterion | Open Food Facts | USDA FoodData Central |
|---|---:|---:|
| Products successfully located | 3/3 | 3/3 |
| Original UPC-A retrieval | 3/3 | 2/3 |
| Product name available | 3/3 | 3/3 |
| Brand available | 3/3 | 2/3 |
| Category available | 3/3 | 3/3 |
| Quantity field available | 3/3 | 2/3 |
| Complete evaluated metadata | 3/3 | 2/3 |
| More recently modified record | 3/3 | 0/3 |
| API requests performed | 3 | 4 |
| HTTP or JSON failures observed | 0 | 0 |

### 6.2 Qualitative Product Comparison

| Product | Preferred Metadata Source | Reason |
|---|---|---|
| Kraft | USDA | More descriptive product name |
| Cheez-It | USDA | More meaningful and complete product description |
| Knorr | Open Food Facts | More descriptive product name and available brand information |

These preferences are based on the observed usefulness of the returned product descriptions and identification metadata. They do not represent independently verified product accuracy.

### 6.3 Comparative Conclusion

Both providers successfully located all three evaluated products when equivalent GTIN representations were considered.

Open Food Facts demonstrated advantages in automatic barcode normalization, metadata field availability, and record modification recency.

USDA FoodData Central demonstrated advantages in descriptive product naming for two of the three evaluated products.

Neither provider consistently outperformed the other across all evaluation criteria.

Within this sample, USDA did not locate any additional products that Open Food Facts could not already retrieve.

The evaluation therefore did not establish sufficient evidence to justify immediately replacing the existing Open Food Facts integration.

## 7. Technical Findings and Architectural Considerations

### 7.1 Barcode Normalization

The evaluation demonstrated that different product databases may store equivalent barcodes using different GTIN representations.

For example, the Cheez-It product was identified using the following representations:

| Representation | Barcode |
|---|---|
| Original UPC-A | `024100705665` |
| GTIN-13 | `0024100705665` |
| GTIN-14 | `00024100705665` |

Open Food Facts automatically normalized the original UPC-A, while USDA required an explicitly normalized search query in this case.

A future integration should:

- Preserve the original scanned barcode.
- Store barcode identifiers as strings to preserve leading zeros.
- Validate supported barcode formats and check digits.
- Generate equivalent GTIN representations when appropriate.
- Validate returned product identifiers before accepting search results.
- Avoid accepting unrelated search results based solely on search ranking.

### 7.2 Metadata Validation

Successful barcode retrieval does not guarantee complete, accurate, or sufficiently descriptive product metadata.

The evaluation identified the following examples:

- Open Food Facts returned `ORIGINAL` as the Cheez-It product name.
- USDA omitted brand and package weight information for Knorr.
- Both providers used different category naming conventions.
- Package weight formatting differed between providers.
- Product record modification dates varied considerably.

A future integration should distinguish between missing metadata, insufficiently descriptive metadata, and conflicting metadata.

Missing information should remain unknown unless it can be obtained from an appropriate source or confirmed by the user.

### 7.3 Data Source Traceability

SmartPantry currently preserves product data source information through the `product_data_source` field.

Any future multi-source implementation should maintain accurate source attribution and distinguish between externally retrieved metadata and user-confirmed information.

If individual metadata fields are combined from different providers, additional field-level source tracking may be necessary.

### 7.4 Downstream Integration Considerations

Changes to barcode product metadata could affect several existing SmartPantry components.

| Component | Potential Impact |
|---|---|
| Storage guidance | Product descriptions and categories may affect food matching and storage recommendations. |
| Recall matching | Product names, brands, and normalized identifiers may affect recall classification. |
| Recipe recommendations | Detailed branded product descriptions may require ingredient normalization. |
| Mochi AI assistant | Product metadata may affect pantry interpretation and contextual responses. |
| Supabase pantry records | Original identifiers, source attribution, and user-confirmed metadata must remain consistent. |
| Streamlit interface | Product confirmation forms and source labels must reflect the actual data provider. |

These potential impacts require integration testing before a second barcode provider can be introduced safely.

No downstream improvements have been established through this evaluation.

### 7.5 Error Handling and Fallback Considerations

A future multi-source integration should distinguish between:

- No matching product found.
- Missing or insufficient product metadata.
- Network connection failures.
- Request timeouts.
- API rate limits.
- Authentication failures.
- Invalid JSON responses.
- Unexpected response structures.
- Conflicting product identifiers.

An empty search result should not be treated as an API failure.

Fallback behavior should be explicitly defined, bounded, and tested to prevent unnecessary requests and excessive lookup delays.

### 7.6 Data Freshness and Food Safety

Database modification and publication dates describe product records rather than the physical food items stored in a user's pantry.

These dates must not be interpreted as:

- Purchase dates.
- Manufacturing dates.
- Preparation dates.
- Expiration dates.
- Best-before dates.

SmartPantry must continue to rely on appropriate storage guidance, available package information, and user-confirmed dates when evaluating pantry items.

The existing principle remains unchanged:

**We do not guess dates we cannot source.**


## 8. Licensing and API Usage Considerations

### 8.1 Open Food Facts

According to the official Open Food Facts documentation:

- The database is licensed under the Open Database License (ODbL).
- Individual database contents are licensed under the Database Contents License.
- Product images are subject to separate licensing requirements.

A future multi-source integration must evaluate applicable attribution, share-alike, and data redistribution obligations before combining or redistributing product metadata.

Open Food Facts also establishes API usage requirements, including application identification through a custom User-Agent and request rate limits.

### 8.2 USDA FoodData Central

Before implementation, the USDA data usage terms, attribution guidance, API authentication requirements, and rate limits should be reviewed.

A registered API key should be configured through environment variables rather than embedded in application source code.

The public DEMO_KEY was used exclusively for this feasibility investigation.

### 8.3 SmartPantry Data Architecture

A future licensing review should distinguish between:

- Externally retrieved product metadata.
- User-confirmed product information.
- Private pantry inventory records.
- Application-generated recommendations.
- Combined or redistributed product datasets.

The licensing implications of storing and combining metadata within SmartPantry's Supabase architecture require further evaluation.

This investigation does not establish full licensing compliance or determine that private user pantry records must be publicly redistributed.

## 9. Evaluation Limitations

The following limitations apply to this investigation:

- Only three packaged food products were evaluated.
- All three products had previously been retrieved through Open Food Facts.
- Products were not randomly selected.
- Product metadata was not independently verified against physical packaging.
- Record modification dates do not establish product information accuracy.
- API response times were not formally measured.
- Sustained availability, rate-limit behavior, and production performance were not evaluated.
- Automated fallback behavior was not implemented or tested.
- Downstream integration benefits were not experimentally established.
- Licensing implications require further review.

The results demonstrate preliminary technical feasibility within a limited sample rather than overall database superiority.

## 10. Architectural Decision

**Decision Date:** November 25, 2026

**Decision Status:** Accepted - Conditional Deferral

SmartPantry will retain Open Food Facts as its barcode product metadata provider while prioritizing final application refinement and presentation readiness.

Although USDA FoodData Central demonstrated potential improvements in descriptive product naming, the evaluation did not establish additional product coverage within the selected sample.

Introducing a second provider would require additional normalization, metadata validation, fallback handling, source attribution, and integration testing.

The decision to defer implementation is based on:

- Preserving existing application stability.
- Limiting unnecessary feature expansion.
- Prioritizing unresolved integration and food safety considerations.
- Maintaining the established testing baseline.
- Allowing sufficient time for final documentation and presentation preparation.

### 10.1 Existing Testing Baseline

At the time of this evaluation, SmartPantry's most recently recorded regression testing results were:

- Tests passed: 186
- Subtests passed: 3
- Failures: 0

These results represent the existing application baseline before any USDA integration.

The seven live API requests documented in this evaluation are separate from the automated regression test suite.

### 10.2 Conditional Reconsideration

USDA integration is deferred rather than rejected.

The integration may be reconsidered before the December 1, 2026 final presentation if all presentation-critical tasks are completed and sufficient time remains for implementation, validation, and regression testing.

Otherwise, it will remain a documented future enhancement.

## 11. Future Implementation Criteria

Before introducing USDA FoodData Central into SmartPantry, the following requirements should be satisfied:

- [ ] Complete all presentation-critical development tasks.
- [ ] Resolve relevant licensing and attribution considerations.
- [ ] Expand evaluation to a more representative product sample.
- [ ] Evaluate products that Open Food Facts cannot retrieve.
- [ ] Establish measurable criteria for metadata quality.
- [ ] Define primary and fallback provider behavior.
- [ ] Implement and validate GTIN normalization.
- [ ] Preserve original scanned barcode identifiers.
- [ ] Implement bounded requests and appropriate error handling.
- [ ] Securely configure USDA API credentials.
- [ ] Preserve accurate product data source attribution.
- [ ] Complete mocked unit tests.
- [ ] Complete controlled live API validation.
- [ ] Verify storage guidance integration.
- [ ] Verify recall matching integration.
- [ ] Verify recipe recommendation integration.
- [ ] Verify Mochi AI assistant integration.
- [ ] Verify Supabase persistence and Streamlit confirmation workflows.
- [ ] Complete full regression testing without new failures.
- [ ] Update relevant project documentation and notebooks.

## 12. Conclusion

The comparative evaluation established USDA FoodData Central as a technically feasible alternative product metadata provider.

Open Food Facts demonstrated stronger metadata field availability and automatic barcode normalization within the evaluated sample, while USDA provided more descriptive product names for two of the three products.

The findings support retaining the current barcode integration while preserving USDA FoodData Central as a potential future enhancement.

This decision reflects SmartPantry's commitment to evidence-based development, data integrity, application stability, and responsible feature prioritization.

## 13. References

### Internal Research

- Aung, Hnin. SmartPantry AI Phase 5 Research Report. November 24, 2026.

### External Documentation

- [USDA FoodData Central](https://fdc.nal.usda.gov/)
- [USDA FoodData Central API Guide](https://fdc.nal.usda.gov/api-guide/)
- [Open Food Facts](https://world.openfoodfacts.org/)
- [Open Food Facts API Documentation](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/)
- [Open Food Facts Licensing Guidance](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/tutorials/license-be-on-the-legal-side/)

### Primary Evaluation Data

Seven live API requests performed on November 25, 2026:

- Four USDA FoodData Central search requests.
- Three Open Food Facts product lookup requests.

The observed API responses and comparative findings are documented in Sections 4 through 6.
