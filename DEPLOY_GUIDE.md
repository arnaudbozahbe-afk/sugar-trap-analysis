# 🚀 Deployment Guide — Sugar Trap Project

## Step 1 · GitHub Setup (5 min)

```bash
# Fork the original repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Copy in the files from this package
cp sugar_trap_analysis.ipynb .
cp dashboard.py .
cp requirements.txt .
cp README.md .        # replace existing README
cp .gitignore .

git add sugar_trap_analysis.ipynb dashboard.py requirements.txt README.md .gitignore
git commit -m "feat: complete Sugar Trap analysis — all stories + candidate's choice"
git push origin main
```

---

## Step 2 · Google Colab (get notebook link)

1. Go to https://colab.research.google.com
2. File → Upload notebook → select `sugar_trap_analysis.ipynb`
3. Run all cells (Runtime → Run all) — takes ~5–10 min for 500k rows
4. File → Share → "Anyone with the link can view" → Copy link
5. **Paste this link** into your README.md under "Link to Notebook"

> 💡 Colab tip: the dataset downloads directly from Open Food Facts CDN — no manual upload needed.

---

## Step 3 · Streamlit Cloud (get dashboard link)

1. Push your code to GitHub (Step 1 must be done first)
2. Go to https://share.streamlit.io → "New app"
3. Connect your GitHub repo
4. Set **Main file path** to: `dashboard.py`
5. Click **Deploy** — takes 2–3 minutes
6. Copy the public URL → paste into README.md

> ⚠️ Make sure `requirements.txt` is in the root of the repo.

---

## Step 4 · Export Notebook as HTML (for submission)

In Google Colab:
- File → Download → Download .ipynb  (upload to GitHub)
- File → Print → Save as PDF  (upload to GitHub as `sugar_trap_analysis.pdf`)

Or locally:
```bash
pip install nbconvert
jupyter nbconvert --to html sugar_trap_analysis.ipynb
# → produces sugar_trap_analysis.html — upload this to GitHub
```

---

## Step 5 · Final Submission

1. Fill all links in README.md
2. Test EVERY link in Incognito window
3. Submit the form: https://forms.cloud.microsoft/e/CeQN2mCyUr

---

## File Checklist

| File | Status | Purpose |
|------|--------|---------|
| `sugar_trap_analysis.ipynb` | ✅ Ready | Main analysis notebook |
| `dashboard.py` | ✅ Ready | Streamlit dashboard |
| `requirements.txt` | ✅ Ready | Python dependencies |
| `README.md` | ⚠️ Fill links | Final README |
| `.gitignore` | ✅ Ready | Prevents dataset upload |
| `sugar_trap_analysis.html` | ❌ Export from Colab | Notebook HTML export |
