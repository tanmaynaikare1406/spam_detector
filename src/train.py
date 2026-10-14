"""Train URL and text models. Usage: python src/train.py"""
import joblib, pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.pipeline import make_pipeline
from signals import clean
from url_features import host_of, reg_domain, vector

ROOT = Path(__file__).resolve().parents[1]

def report(name, y, p):
    tn, fp, fn, tp = confusion_matrix(y, p).ravel()
    line = f"{name}: precision={precision_score(y, p):.3f} recall={recall_score(y, p):.3f} f1={f1_score(y, p):.3f} fpr={fp / max(1, fp + tn):.3f}"
    print(line)
    return line

def main():
    lines = ["# Results (sample data is synthetic, so these numbers are NOT meaningful)"]
    u = pd.read_csv(ROOT / "data/sample_urls.csv")
    X, y, g = [vector(x) for x in u.url], u.label.values, [reg_domain(host_of(x)) for x in u.url]
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=0).split(X, y, g))  # split by domain
    rf = RandomForestClassifier(300, random_state=0).fit([X[i] for i in tr], y[tr])
    lines.append(report("URL RandomForest", y[te], rf.predict([X[i] for i in te])))
    joblib.dump(rf, ROOT / "models/url_model.joblib")
    m = pd.read_csv(ROOT / "data/sample_messages.csv")
    xtr, xte, ytr, yte = train_test_split([clean(t) for t in m.text], m.label, test_size=0.25, stratify=m.label, random_state=0)
    tm = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=2), LogisticRegression(max_iter=1000)).fit(xtr, ytr)
    lines.append(report("Text TF-IDF+LogReg", yte, tm.predict(xte)))
    joblib.dump(tm, ROOT / "models/text_model.joblib")
    (ROOT / "RESULTS.md").write_text("\n\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
