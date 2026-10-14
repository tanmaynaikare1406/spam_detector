"""URL feature extraction. Text analysis only: URLs are never opened."""
import math
from urllib.parse import urlparse

BRANDS = {"paypal": ["paypal.com"], "sbi": ["sbi.co.in", "onlinesbi.sbi"], "hdfc": ["hdfcbank.com"],
          "icici": ["icicibank.com"], "amazon": ["amazon.com", "amazon.in"], "google": ["google.com"],
          "microsoft": ["microsoft.com"], "apple": ["apple.com"], "netflix": ["netflix.com"], "paytm": ["paytm.com"]}
BAD_TLD = ("xyz", "top", "click", "live", "support", "icu", "tk", "buzz", "work")
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "rb.gy", "cutt.ly"}

def _parse(url):
    return urlparse(url if "://" in url else "http://" + url)

def host_of(url):
    return (_parse(url).hostname or "").lower()

def reg_domain(host):
    p = host.split(".")
    if len(p) <= 2:
        return host
    if len(p[-1]) == 2 and p[-2] in ("co", "com", "org", "gov", "ac", "net"):
        return ".".join(p[-3:])
    return ".".join(p[-2:])

def entropy(s):
    return -sum(s.count(c) / len(s) * math.log2(s.count(c) / len(s)) for c in set(s)) if s else 0.0

def extract(url):
    """Return a dict of numeric features for one URL."""
    h, reg, u = host_of(url), reg_domain(host_of(url)), _parse(url)
    digits = sum(c.isdigit() for c in url)
    name = reg.split(".")[0]
    return {
        "url_len": len(url), "host_len": len(h), "dots": h.count("."), "hyphens": h.count("-"),
        "digit_ratio": digits / max(1, len(url)), "has_at": int("@" in url),
        "ip_host": int(h.replace(".", "").isdigit() and h.count(".") == 3),
        "subdomains": max(0, len(h.split(".")) - len(reg.split("."))), "https": int(url.lower().startswith("https")),
        "bad_tld": int(h.rsplit(".", 1)[-1] in BAD_TLD), "shortener": int(h in SHORTENERS),
        "path_depth": u.path.count("/"), "n_params": u.query.count("&") + int(bool(u.query)),
        "host_entropy": entropy(h),
        "brand_mismatch": int(any(b in h and reg not in ok for b, ok in BRANDS.items())),
        "digit_in_name": int(any(a.isalpha() and b.isdigit() and c.isalpha() for a, b, c in zip(name, name[1:], name[2:]))),
    }

FEATURES = list(extract("http://example.com").keys())

def vector(url):
    f = extract(url)
    return [f[k] for k in FEATURES]

def reasons(url):
    """Plain-language reasons a URL looks risky."""
    f, h = extract(url), host_of(url)
    out = []
    if f["ip_host"]: out.append("Uses an IP address instead of a domain name")
    if f["has_at"]: out.append("Contains an @ symbol that can hide the real host")
    if not f["https"]: out.append("Does not use HTTPS")
    if f["url_len"] > 75: out.append("Very long link")
    if f["hyphens"] >= 2: out.append("Many hyphens in the domain")
    if f["subdomains"] >= 2: out.append("Many subdomains")
    if f["bad_tld"]: out.append("Suspicious domain ending")
    if f["shortener"]: out.append("Shortened link hides the real destination")
    if f["brand_mismatch"]: out.append("Mentions a known brand but the real domain is " + reg_domain(h))
    if f["digit_in_name"]: out.append("A digit is swapped in for a letter in the domain name")
    return out
