# TTB Alcohol Label Verification Prototype

A Streamlit prototype for AI-assisted alcohol beverage label review. The application helps Treasury/TTB reviewers compare label text against expected application data and flags missing, inconsistent, or questionable fields.

## Assignment Fit

This project addresses the Treasury take-home prompt for an AI-powered alcohol label verification app. The prototype focuses on the core reviewer workflow: checking whether information shown on an alcohol label matches the application record.

The app verifies common TTB label elements including:

- Brand name
- Class/type designation
- Alcohol content
- Net contents
- Producer/bottler name and address
- Country of origin, if applicable
- Government Health Warning Statement

## Features

- Simple reviewer-friendly Streamlit interface
- Paste label text or upload a `.txt` label file
- Enter expected application fields
- Fuzzy matching to account for capitalization and minor wording differences
- Strict check for the mandatory Government Health Warning heading and text
- Pass / Review / Fail output for each field
- JSON report download for audit or testing
- Unit tests for core verification logic

## Repository Structure

```text
ttb-label-verification-app/
├── app.py
├── verifier.py
├── requirements.txt
├── README.md
├── samples/
│   └── sample_label.txt
└── tests/
    └── test_verifier.py
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Run Tests

```bash
pytest
```

## Deployment

This app can be deployed to Streamlit Community Cloud for prototype review:

1. Push this repository to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set the main file path to `app.py`.
5. Deploy and copy the generated public URL.

For a production Treasury environment, this prototype could be containerized and deployed in Azure Government or AWS GovCloud with agency identity management, logging, retention controls, and approved storage policies.

## Approach

The prototype uses a lightweight verification pipeline:

1. Reviewer provides label text.
2. Reviewer enters expected application data.
3. The verification engine normalizes capitalization, punctuation, and spacing.
4. The engine uses fuzzy text comparison to identify exact and near matches.
5. Required fields are classified as `Pass`, `Review`, or `Fail`.
6. The Government Health Warning Statement receives a dedicated rule-based check because the wording is mandatory and less tolerant of variation.

This approach prioritizes fast response time, transparent results, and ease of use for reviewers.

## Tools Used

- Python
- Streamlit
- pandas
- pytest
- Python standard library text matching utilities

## Assumptions and Trade-offs

- The prototype is text-based. It assumes label text is pasted in or provided as a `.txt` file.
- OCR/image extraction is intentionally excluded from the first version to keep the prototype reliable, fast, and deployable without external services.
- Fuzzy matching is used for fields where minor formatting differences should not automatically cause rejection.
- The government warning check is stricter because the required wording is mandatory.
- The prototype does not store uploaded files or verification results.
- It does not integrate with COLA or any Treasury internal system.

## Future Improvements

- Add OCR for images and PDFs.
- Add batch upload support for multiple labels.
- Add beverage-specific validation rules for wine, beer, and distilled spirits.
- Add visual highlighting of matched label text.
- Add authenticated deployment in a government cloud environment.
