"""Writes SYNTHETIC sample data so the project runs end to end.
Replace data/*.csv with real datasets (PhishTank, UCI SMS, Nazario) for real results."""
import csv, random
from pathlib import Path
R = random.Random(0)
D = Path(__file__).resolve().parents[1] / "data"
legit = ["google.com", "github.com", "wikipedia.org", "amazon.in", "hdfcbank.com", "sbi.co.in", "python.org", "bbc.co.uk", "microsoft.com",
         "apple.com", "netflix.com", "stackoverflow.com", "nptel.ac.in", "flipkart.com", "linkedin.com", "paytm.com", "icicibank.com",
         "youtube.com", "medium.com", "coursera.org"]
paths = ["", "/", "/login", "/account", "/help/contact", "/docs/page", "/search?q=ai", "/watch?v=abc123"]
brands = ["paypal", "sbi", "hdfc", "icici", "amazon", "google", "microsoft", "apple", "netflix", "paytm"]
words = ["secure", "verify", "login", "update", "kyc", "account", "support"]
tlds = ["xyz", "top", "click", "live", "icu", "com", "net", "in"]
rows = []
for _ in range(300):
    rows.append((f"https://{R.choice(['www.', '', 'accounts.', 'support.'])}{R.choice(legit)}{R.choice(paths)}", 0))
    k, b, w, t = R.random(), R.choice(brands), R.choice(words), R.choice(tlds)
    tok = "".join(R.choice("abcdefghijkmnpqrstuvwxyz") for _ in range(4))
    if k < .5: u = f"http://{b}-{w}-{tok}.{t}/{w}/index.php"
    elif k < .65: u = f"http://{'.'.join(str(R.randint(1, 250)) for _ in range(4))}/{b}/{w}"
    elif k < .8: u = f"https://{b.replace('a', '4', 1)}{tok}.{w}.{t}/signin?id={R.randint(100, 999)}"
    else: u = f"https://bit.ly/{tok}{R.randint(10, 99)}"
    rows.append((u, 1))
(D / "sample_urls.csv").write_text("url,label\n" + "\n".join(f"{u},{l}" for u, l in rows))
ok = ["Hi, the meeting moved to {t}. Notes are at {u}", "Your order has shipped and will arrive on {d}. Track it at {u}", "Reminder: lab report due {d}. See you in class",
      "Thanks for your help yesterday, shall we catch up at {t}?", "Your invoice for {d} is ready: {u}", "Happy birthday! Dinner at {t} tonight?"]
bad = ["Dear customer, your {b} account will be BLOCKED today. Complete KYC immediately: {u}", "Congratulations! You are the winner of a cashback reward. Claim now: {u}",
       "URGENT: {b} detected a login from a new device. Verify your password within 24 hours: {u}", "Your {b} account is suspended. Confirm your card number and OTP: {u}",
       "Final notice: update your {b} details or face a penalty. {u}", "You won a free gift from {b}! Claim before it expires {u}"]
msgs = []
for _ in range(200):
    d, t, b = R.choice(["Monday", "Friday", "12 Nov"]), R.choice(["4 pm", "noon", "6 pm"]), R.choice(brands).upper()
    msgs.append((R.choice(ok).format(d=d, t=t, u=f"https://{R.choice(legit)}/{R.choice(paths)[1:]}"), 0))
    msgs.append((R.choice(bad).format(b=b, u=f"http://{b.lower()}-{R.choice(words)}.{R.choice(tlds[:5])}/x"), 1))
with open(D / "sample_messages.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["text", "label"]); w.writerows(msgs)
print("sample data written")
