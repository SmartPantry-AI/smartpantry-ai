# SmartPantry AI: Tests

This folder contains automated tests for SmartPantry AI. Tests help us check that individual modules behave as expected before connecting them in the full application.

## Current tests

- `test_storage.py`: Checks storage rules, cooked leftovers, FoodKeeper spinach guidance, and `UNKNOWN` results when information or supported rules are missing.
- `test_ai_assistant.py`: Checks Mochi's responses, error handling, and instructions using mocked OpenAI calls.
- `results/`: Stores test evidence or results when the team documents a test run.

Other modules can add their own `test_*.py` files here as integration progresses.

## Run the tests

From the **project root folder**, activate your virtual environment and install dependencies from `requirements.txt` if needed.

Run the full test suite:

```bash
python -m pytest tests -v
```

Run only the storage tests:

```bash
python -m pytest tests/test_storage.py -v
```

You can also run the storage tests with Python's built-in `unittest`:

```bash
python -m unittest tests/test_storage.py -v
```

## Before a pull request

1. Run the relevant tests and confirm the results.
2. Add tests for any new or changed behavior.
3. Record the test command, results, and any known limitations in the pull request.
4. Do not include API keys, passwords, or other secrets in test files or results.

**Important:** Storage reminders are guidance, not a guarantee of food safety. Tests that use mocks do not prove that live external APIs are available.
