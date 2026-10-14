# PhishGuard
Phishing detector for messages and links: text model + URL model + rule signals -> score, verdict, reasons, highlights.

## Run
    pip install -r requirements.txt
    python src/make_sample_data.py     # SYNTHETIC data, replace with real datasets
    python src/train.py                # trains models, writes RESULTS.md
    python tests/test_phishguard.py    # or: pytest
    uvicorn app.api:app --reload       # open http://127.0.0.1:8000

## Important
data/sample_*.csv are synthetic and easy, so metrics are meaningless. Put real data in the same CSV
format (url,label / text,label) and re-run train.py. Split by domain is already implemented.

## Notes
- `models/*.joblib` are demo models trained on the synthetic data, saved with scikit-learn 1.8.0 (pinned in `requirements.txt`).
  Re-run `python src/train.py` to rebuild them.
- Model files are pickles, so only load `.joblib` files from sources you trust.
- User feedback is written to `data/feedback.csv` (git-ignored). It contains message text, so treat it as private.

## Not built yet (next phases)
DistilBERT fine-tune, SHAP/LIME explanations, adversarial attack tests, trained fusion model,
second-dataset evaluation, retraining from feedback, report.
