"""PhishGuard pipeline: text model + URL model + signals -> one explained score."""
import re, joblib
from pathlib import Path
from signals import clean, find_signals
from url_features import reasons, vector

ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r'(https?://[^\s<>"]+|www\.[^\s<>"]+|\b(?:bit\.ly|tinyurl\.com|rb\.gy|cutt\.ly)/[^\s<>"]+)', re.I)

class PhishGuard:
    def __init__(self):
        self.url_model = joblib.load(ROOT / "models/url_model.joblib")
        self.text_model = joblib.load(ROOT / "models/text_model.joblib")

    def _top_words(self, text, n=5):
        vec, clf = self.text_model.steps[0][1], self.text_model.steps[1][1]
        x = vec.transform([clean(text)])
        names = vec.get_feature_names_out()
        contrib = sorted(((x[0, i] * clf.coef_[0][i], names[i]) for i in x.nonzero()[1]), reverse=True)
        return [w for c, w in contrib[:n] if c > 0 and " " not in w and w not in ("urltoken", "numtoken")]

    def check(self, text):
        text = text.strip()
        urls = [u.rstrip(".,;)") for u in URL_RE.findall(text)]
        bare = not urls and " " not in text and "." in text
        if bare:
            urls = [text]  # a bare link was pasted
        flagged = []
        for u in urls:
            p = self.url_model.predict_proba([vector(u)])[0][1]
            flagged.append({"url": u, "score": round(p * 100), "reasons": reasons(u)})
        url_s = max((f["score"] for f in flagged), default=0)
        text_p = 0.0 if bare else self.text_model.predict_proba([clean(text)])[0][1] * 100
        sigs = find_signals(text)
        sig_s = min(100, sum(s["weight"] for s in sigs) * 2)
        w = (0.0, 0.9, 0.1) if bare else (0.35, 0.4, 0.25) if urls else (0.7, 0.0, 0.3)
        score = round(min(100, w[0] * text_p + w[1] * url_s + w[2] * sig_s))
        verdict = "safe" if score < 30 else "suspicious" if score < 60 else "phishing"
        why = [s["reason"] for s in sigs]
        if text_p >= 60: why.append(f"Wording is similar to known phishing messages ({round(text_p)}% match)")
        if url_s >= 50: why.append(f"Link scored {url_s}/100 on its own")
        words = ([] if bare else self._top_words(text)) + [s["matched_text"] for s in sigs]
        return {"score": score, "verdict": verdict, "reasons": why, "highlighted_words": sorted(set(words)), "flagged_urls": flagged}
