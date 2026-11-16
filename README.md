# 🥫 SmartPantry AI

**Your Intelligent Pantry & Kitchen Companion**

SmartPantry AI is a collaborative capstone project designed to help users organize household food, reduce food waste, and make more informed decisions about food storage and meal planning.

The application combines pantry inventory management, barcode scanning, AI-powered food image recognition, storage guidance, food recall screening, recipe recommendations, and an AI assistant named **Mochi**.

Built with Python and Streamlit, SmartPantry AI uses Supabase for user authentication and persistent pantry storage.

> **Project Status:** Phase 4 — Database Integration, User Accounts, Persistent Pantry Management, and Application Refinement  
> **Development Stage:** Functional prototype with ongoing testing and improvements.

---

# 🚨 TEAM MEMBERS: READ THIS BEFORE WORKING ON THE PROJECT 🚨

> ## ⛔ DO NOT WORK DIRECTLY ON THE `main` BRANCH
>
> The `main` branch is the stable, shared version of SmartPantry AI.
>
> **Do not make project changes, commit, or push directly to `main`.**
>
> Every team member must create a separate branch for their work and submit changes through a **Pull Request (PR)** before anything is merged into `main`.

## Required GitHub Workflow: Follow Every Time

**Before making ANY project changes:**

1. 🔄 Make sure your local `main` branch is up to date.
2. 🌿 Create a new branch for your task.
3. 💻 Make changes only on that branch.
4. 🧪 Test your work.
5. 💾 Commit changes with a descriptive commit message.
6. ⬆️ Push your branch to GitHub.
7. 🔀 Open a Pull Request into `main`.
8. 👀 Review the Pull Request and confirm the changes are ready to merge.
9. ✅ Merge the approved Pull Request into `main`.

### ⚠️ Why This Matters

Multiple team members work in the same repository. Working directly on `main` increases the risk of overwritten code, merge conflicts, broken features, and lost work.

**When in doubt, stop and ask the team before merging or pushing to `main`.**

### Quick Rule

```text
❌ DO NOT:
Your Computer → main → Push

✅ DO:
Your Computer → Feature Branch → Push → Pull Request → Review → main
```

---

## 🎯 Project Goal

SmartPantry AI aims to reduce food waste, improve food safety awareness, and help users make better use of ingredients they already have.

### Core Workflow

**Identify Food → Save to Pantry → Monitor Storage → Screen for Recalls → Recommend Recipes**

The application supports multiple ways to identify and add food, allowing users to manage their pantry through a single interface.

---

## 🚀 Current Features

### 1. Pantry Inventory Management

- Add ingredients through multiple input methods.
- View saved pantry items.
- Track available item information, including quantities and dates.
- Store inventory in a persistent database.
- Retrieve pantry records across application sessions.
- Maintain separate inventory records for authenticated users.
- Group matching pantry ingredients while retaining individual batch information.

### 2. Barcode Scanning

- Upload barcode images for product identification.
- Decode supported barcodes using OpenCV.
- Retrieve available product details using Open Food Facts.
- Add identified products to the pantry.

Product identification depends on barcode readability and the completeness of external product records.

### 3. AI Image Recognition

- Upload food images for AI-assisted identification.
- Recognize food items using OpenAI's vision capabilities.
- Add recognized ingredients to the pantry.

AI-generated identifications may require user verification.

### 4. Mochi AI Assistant 🍡

Mochi provides conversational assistance for pantry management and meal ideas.

Confirmed functionality includes:

- Adding pantry items through supported natural-language commands.
- Requesting confirmation before saving pantry additions.
- Retrieving saved pantry inventory through supported commands.
- Suggesting recipes based on ingredients provided in a conversation.
- Providing missing ingredients and cooking instructions.

Natural-language command recognition is still being refined. Mochi's conversational recipe suggestions are separate from its pantry-retrieval commands.

### 5. Storage Guidance and Reminders

SmartPantry uses curated food storage information from:

- USDA FoodKeeper
- FoodSafety.gov
- Oregon State University Extension

Supported functionality includes:

- Ingredient-specific storage recommendations.
- Refrigerator storage guidance.
- Use-soon reminders based on supported dates and source rules.
- Priority indicators for upcoming reminders.
- Supplementary storage information where available.

Storage guidance depends on supported ingredient names, storage locations, available dates, and source coverage.

**Use-soon reminders are informational estimates, not guaranteed food safety expiration dates.**

### 6. Food Recall Screening

SmartPantry retrieves available food recall information from FDA and USDA sources.

The application can:

- Screen saved pantry items against retrieved recall records.
- Identify potential product-name overlaps.
- Display records requiring further verification.
- Present recall-screening information in the Food Safety section.

**Potential matches are not confirmed recalls.** Users must verify identifying information such as brand, UPC, lot number, and packaging.

An incomplete screening result must not be interpreted as confirmation that a product is safe.

### 7. Recipe Recommendations

SmartPantry integrates with the Spoonacular API to retrieve recipe suggestions.

The application can:

- Use saved pantry ingredients when requesting recipes.
- Rank retrieved recipes using ingredient matching and supported expiration-related priorities.
- Display available and missing ingredients.
- Help users identify possible meals using their existing inventory.

Mochi also provides conversational recipe suggestions as a separate AI-assisted feature.

### 8. User Authentication and Persistent Storage

SmartPantry uses Supabase for:

- Email/password authentication.
- PostgreSQL database storage.
- User-associated pantry records.
- Persistent inventory retrieval.
- Row Level Security policies designed to restrict access to each user's records.

Separate test-user pantry records and database persistence have been verified during development.

An earlier SQLite implementation is retained for development and testing. Supabase is the current backend for authenticated pantry storage.

---

## 🧪 Phase 4 Testing and Verification

The team has performed module-level testing, integration testing, and live application testing.

### Confirmed Live Application Tests

| Component | Observed Result |
|---|---|
| Barcode scanning | Pasta product identified and saved |
| Manual entry | Carrots successfully added |
| Image recognition | Spinach recognized and saved |
| Mochi pantry addition | Tomato added through a supported command |
| Mochi pantry retrieval | Saved inventory successfully displayed |
| Supabase persistence | Added items appeared in the database |
| User accounts | Separate test-user pantry records verified |
| FoodKeeper guidance | Spinach storage reminder displayed |
| OSU Extension guidance | Supplementary spinach information displayed |
| FoodSafety.gov guidance | Cooked meat or poultry reminder displayed |
| USDA recall screening | 50 records retrieved and screened during the test |
| FDA recall screening | 20 records retrieved; 10 potential product-name overlaps identified |
| Spoonacular recommendations | Ranked recipes displayed with ingredient matches |
| Mochi recipe assistance | Recipe suggested with missing ingredients and cooking instructions |

These results document successful prototype tests, not universal support for all ingredients, products, or requests.

Recall counts represent one observed test run and may vary as external recall data changes.

---

## ⚠️ Current Limitations

SmartPantry AI is a functional prototype and continues to undergo refinement.

- **Barcode scanning:** Identification depends on readable barcodes and available product records.
- **Image recognition:** AI-generated food identifications are not guaranteed to be correct.
- **Mochi:** Pantry commands currently work more reliably with specific supported wording.
- **Storage guidance:** Ingredient coverage and matching vary across supported reference sources.
- **Food safety lookup:** The separate lookup interface does not expose every storage rule used elsewhere in the application.
- **Recall screening:** Potential matches require additional verification and do not establish whether a product is safe.
- **Recipe recommendations:** Retrieved recipes may require ingredients that are not currently available.
- **Ingredient matching:** Differences in food names, aliases, and quantities can affect recommendations.
- **External services:** Some features depend on API availability, network connectivity, and valid credentials.

These limitations inform the project's remaining development priorities.

---

## 🔮 Future Development

Remaining development will focus on improving existing features and addressing limitations identified during testing.

Areas for improvement include:

- Expanding barcode and ingredient recognition.
- Improving Mochi's natural-language understanding and pantry interactions.
- Increasing storage guidance coverage and consistency across supported sources.
- Strengthening recall matching and product verification.
- Improving recipe relevance, ingredient matching, and quantity awareness.
- Refining pantry management and the overall user experience.
- Continuing integration, security, and reliability testing.

---

## 👥 Team Responsibilities

| Area | Responsibility |
|---|---|
| Problem & Background Research | Food waste research, user needs, evaluation, and project documentation |
| Barcode & Product Data | Barcode decoding, product identification, and Open Food Facts integration |
| Expiration & Storage | Storage guidance, supported date calculations, and food safety references |
| Food Recalls | FDA/USDA recall integration, screening, and matching |
| AI Recipes & Technical Tools | Image recognition, Mochi AI assistant, recipe recommendations, and related testing |

All team members contribute to integration, testing, documentation, and project decisions.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development and backend logic |
| Streamlit | Web application interface |
| Supabase | Authentication and PostgreSQL database |
| OpenAI API | Image recognition and Mochi AI assistance |
| OpenCV | Barcode image processing |
| Open Food Facts | Product information lookup |
| Spoonacular API | Recipe retrieval |
| USDA FoodKeeper | Food storage reference data |
| FoodSafety.gov | Food storage and safety reference data |
| OSU Extension | Supplementary food storage guidance |
| FDA and USDA data sources | Food recall screening |
| Pytest | Automated testing |
| Git & GitHub | Version control and collaboration |

---

## 🌿 Branch Naming

Branches should describe the work being completed rather than the person completing it.

### Good Examples

```text
feature/recipe-recommendations
feature/barcode-product-data
feature/mochi-pantry-reading
feature/storage-guidance-integration
docs/phase4-readme-update
fix/recipe-scoring
```

Avoid vague branch names such as `test`, `stuff`, `new`, or `changes`.

---

## 🔐 API Keys & Security

**Never commit passwords, API keys, tokens, credentials, or other secrets to GitHub.**

Sensitive credentials must be stored using environment variables or approved secrets-management methods.

A `.env` file containing real credentials must never be committed to the repository.

### Required Environment Variables

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI-powered image recognition and Mochi |
| `SPOONACULAR_API_KEY` | Spoonacular recipe recommendations |
| `SUPABASE_URL` | Supabase project connection |
| `SUPABASE_KEY` | Supabase client authentication |

These names are verified against the application source code.

Use an appropriate client-safe Supabase publishable or anon key. Do not place a Supabase service-role or secret key in the application configuration.

For deployment, configure credentials using the hosting platform's supported secrets-management features.

Supabase Row Level Security policies should remain enabled and be tested whenever database access logic changes.

---

## ▶️ Running SmartPantry Locally

### 1. Clone the Repository

```bash
git clone https://github.com/SmartPantry-AI/smartpantry-ai.git
cd smartpantry-ai
```

### 2. Create and Activate a Virtual Environment

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file into a local `.env` file.

**macOS/Linux:**

```bash
cp .env.example .env
```

**Windows Command Prompt:**

```cmd
copy .env.example .env
```

Alternatively, copy the file using File Explorer.

Configure the following variables using your own credentials:

```dotenv
OPENAI_API_KEY=your_openai_api_key_here
SPOONACULAR_API_KEY=your_spoonacular_api_key_here
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_publishable_or_anon_key_here
```

**Important:** `.env.example` must contain placeholders only. Never commit actual credentials to GitHub.

### 5. Start the Application

```bash
streamlit run app/app.py
```

Open the local Streamlit URL displayed in the terminal.

Some functionality requires valid external API credentials and an active network connection.

---

## 📁 Repository Structure

The following structure reflects the main directories and configuration files currently present in the repository.

```text
smartpantry-ai/
├── .env.example         # Example environment-variable configuration
├── .gitignore           # Git exclusions for local and sensitive files
├── .streamlit/          # Streamlit application configuration
├── app/                 # Main Streamlit application
├── assets/              # Application images and visual assets
├── data/                # Raw and processed reference datasets
├── docs/                # Project documentation
├── modules/             # Application features and integrations
├── notebooks/           # Development and evaluation notebooks
├── test_images/         # Test images and barcode samples
├── tests/               # Automated and manual testing resources
├── README.md            # Project overview and setup instructions
└── requirements.txt     # Python dependencies
```

### Important Application Modules

The `modules/` directory includes:

- `ai_assistant.py` — Mochi AI assistance and pantry command processing.
- `barcode_lookup.py` — Barcode identification and product lookup.
- `image_recognition.py` — AI-assisted food image identification.
- `pantry_database.py` — Earlier local database implementation.
- `pantry_grouping.py` — Pantry item grouping.
- `pantry_manager.py` — Pantry inventory management logic.
- `recall_checker.py` — FDA and USDA recall retrieval and screening.
- `recipe_recommender.py` — Recipe retrieval, matching, and ranking.
- `storage_guidance.py` — Food storage rules and reminder calculations.
- `supabase_auth.py` — Supabase authentication helpers.
- `supabase_client.py` — Supabase client initialization.
- `supabase_pantry.py` — Authenticated pantry database operations.

---

## 📚 Capstone Project

SmartPantry AI is a collaborative academic capstone project.

The repository serves as the team's shared environment for application development, integration, testing, documentation, and project evaluation.

The current prototype demonstrates how AI-powered image recognition, natural-language assistance, external food data sources, and persistent cloud storage can be combined into a household food management application.

Development continues with a focus on improving reliability, usability, and coverage of the existing features.
