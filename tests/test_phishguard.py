import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from signals import find_signals
from url_features import extract, reasons
from pipeline import PhishGuard

def test_url_features():
    assert extract("http://192.168.1.5/login")["ip_host"] == 1
    assert extract("http://paypal-verify.xyz/a")["brand_mismatch"] == 1
    assert extract("https://www.paypal.com/")["brand_mismatch"] == 0
    assert reasons("https://bit.ly/abc")

def test_signals():
    assert any(s["name"] == "credentials" for s in find_signals("share your OTP now"))
    assert find_signals("see you at lunch") == []

def test_pipeline_ranks_phishing_higher():
    pg = PhishGuard()
    bad = pg.check("Your SBI account is BLOCKED. Complete KYC immediately: http://sbi-kyc-update.xyz/login")
    ok = pg.check("Hi, the meeting moved to 4 pm. Notes: https://docs.google.com/document")
    assert bad["score"] > ok["score"] and bad["verdict"] != "safe" and ok["verdict"] == "safe"
    assert set(bad) == {"score", "verdict", "reasons", "highlighted_words", "flagged_urls"}

if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"): f(); print("pass", n)
