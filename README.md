# 🥫 SmartPantry AI

**AI-Powered Food Management & Safety Assistant**

SmartPantry AI is a capstone project designed to help users manage household food more effectively. The system will combine pantry inventory tracking, expiration and storage monitoring, food recall information, and AI-assisted recipe recommendations in one application.

> **Project Status:** Phase 1 — Planning, Research, and Initial Development

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
2. 🌿 Create a new branch for the task you are working on.
3. 💻 Make your changes **only on that branch**.
4. 🧪 Test your work.
5. 💾 Commit your changes with a descriptive commit message.
6. ⬆️ Push your branch to GitHub.
7. 🔀 Open a Pull Request into `main`.
8. 👀 Review the Pull Request and confirm the changes are ready to merge.
9. ✅ Merge the Pull Request into `main`..

> ### ⚠️ Why This Matters
>
> Multiple team members will be working in the same repository. Working directly on `main` increases the risk of overwritten code, merge conflicts, broken features, and lost work.
>
> **When in doubt, stop and ask the team before merging or pushing to `main`.**

### Quick Rule

```text
❌ DO NOT:
Your Computer → main → Push

✅ DO:
Your Computer → Feature Branch → Push → Pull Request → Review → main
```

### 🛑 Before You Start Coding

**If you are currently on `main`, create or switch to a feature branch BEFORE editing project files.**

---

## 🎯 Project Goal

SmartPantry AI aims to reduce food waste, improve food safety, and make it easier for users to decide what to cook with the food they already have.

Our core workflow is:

**Scan Foods → Track Inventory → Monitor Expiration & Storage → Check Recalls → Recommend Recipes**

---

## 🚀 Planned MVP Features

The Minimum Viable Product (MVP) is planned to include:

- **Pantry Inventory:** Add and manage food items.
- **Barcode & Product Data:** Retrieve product information using barcode/product data sources.
- **Expiration & Storage:** Track expiration dates and provide storage guidance.
- **Food Recall Checks:** Compare pantry products against available food recall information.
- **AI Recipe Recommendations:** Recommend recipes based on available and expiring ingredients.
- **User-Friendly Interface:** Provide access to SmartPantry features through a Streamlit application.

Features listed above are currently under development and may change as the project progresses.

---

## 👥 Team Responsibilities

| Area | Responsibility |
|---|---|
| Problem & Background Research | Food waste research, user needs, project background, and supporting documentation |
| Barcode & Product Data | Barcode lookup, product identification, API/data integration, and JSON parsing |
| Expiration & Storage | Expiration tracking, storage rules, date handling, and food-storage guidance |
| Food Recalls | Recall data integration and product/recall matching |
| AI Recipes & Technical Tools | Recipe recommendation logic, AI/LLM integration, substitutions, constraints, and technical tool evaluation |

All team members contribute to integration, testing, documentation, and project decisions.

---

## 🛠️ Technology

SmartPantry AI is expected to use technologies including:

- **Python**
- **Streamlit**
- **Git & GitHub**
- **External food/product APIs and datasets**
- **Food recall data sources**
- **OpenAI / LLM tools where appropriate**
- **JSON for API data exchange**

The final technology stack may evolve during development.

---

## 🌿 Branch Naming

Branches should describe the work being completed rather than the person completing it.

### Good examples

```text
feature/recipe-recommendations
feature/barcode-product-data
feature/expiration-tracking
feature/recall-checker
docs/background-research
fix/recipe-scoring
```

Avoid vague branch names such as:

```text
test
stuff
new
changes
```

---

## 🔐 API Keys & Security

**Never commit passwords, API keys, tokens, credentials, or other secrets to GitHub.**

Sensitive credentials should be stored using environment variables or approved secrets-management methods.

A `.env` file containing real credentials must never be committed to the repository.

---

## 📁 Repository Structure

The repository structure will be expanded as development begins.

```text
smartpantry-ai/
├── app/
├── data/
├── docs/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

Additional folders and files may be added as the project architecture develops.

---

## 📚 Capstone Project

SmartPantry AI is being developed as a collaborative academic capstone project. This repository serves as the team's shared environment for source code, documentation, testing, and project integration.
