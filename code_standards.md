# Coding Standards — M1 Pie DCA Allocator

This document defines the coding standards for the **M1 Pie DCA Allocator** project.
These standards extend best practices established in the Lookout project, adapted for
financial portfolio modeling and GPT-powered workflows. Code should be modular,
notebook-friendly, and production-ready for future Streamlit UI deployment.

## General Standards

- **Flake8**: All code must pass flake8 linting.
- **Black**: Use Black for code formatting.
- **80-char lines**: Soft wrap markdown and comments.
- **Naming**: Use consistent, descriptive names for all objects.
- **Docstrings**: Use `:param`/`:return` style for all public functions.
- **Imports**: Group as stdlib, third-party, then local.

## Python Libraries

- **Pandas/NumPy**: For future analysis and vectorized operations.
- **OpenAI API**: Used for image parsing and screenshot extraction via GPT-4o.
- **Streamlit**: Target UI framework for interactive DCA adjustments.
- **Matplotlib**: Display input images and diagnostics in notebooks.
- **PIL/Base64**: Used for pre-processing image inputs to the OpenAI API.

## Data Handling

- **Portfolio JSON**: Canonical format for storing portfolio hierarchy.
- **Pie nodes**: Each pie item is typed as `"ticker"` or `"pie"`.
- **Unique IDs**: Each pie or ticker must have a unique `id` within its scope.
- **Decimal**: Use `Decimal` over `float` when precision matters.

## Module Design

- **Modular Architecture**: Group functionality into focused, reusable modules.
- **Isolation**: Avoid side effects in module code—use pure functions when possible.
- **Reusability**: Keep utility logic in `scripts/`, and avoid hardcoded paths.

## Notebook Conventions

- **Function-First**: All logic must be encapsulated in functions.
- **Globals**: Minimize use of global variables.
- **Logging**: Use `logging`, not `print`, with module-level logger setup.
- **Image Display**: Always render input screenshots using `matplotlib`.

## Project Layout

```
/notebooks       # Prototypes and screenshot parsing
/scripts         # Modular helper functions
/data            # Input screenshots or persistent data
/portfolio.json  # Canonical sample portfolio data
README.md        # Project description and usage
code_standards.md# This file
```

## Logging and Error Handling

- **Try/Except**: Required for file and API operations.
- **Logger**: Use `logging.getLogger("m1pie")` for all modules.
- **Log Level**: Set at INFO or DEBUG as appropriate per environment.

## Streamlit & Deployment Notes

- **Secrets**: Store OpenAI key in `.streamlit/secrets.toml` under `[openai]`.
- **Persistence**: Use Storj S3-compatible bucket (see README for setup).
- **Future API**: Consider separating data model and UI interaction for maintainability.

```python
# Logger pattern for all modules
import logging

logger = logging.getLogger("m1pie")
```
