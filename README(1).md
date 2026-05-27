# 🍬 Sugar Trap: Blue Ocean Market Gap Analysis

> **Helix CPG Partners** — Strategic Food & Beverage Intelligence  
> Analyst: [Your Full Name] · [Your Email]

---

## A. Executive Summary

Analysis of **500,000+ products** from the Open Food Facts dataset reveals that the global snack market is overwhelmingly dominated by high-sugar, low-protein offerings — over **60% of products** fall in the "Saturated Zone" (high sugar, low protein), confirming the client's hypothesis of a systemic market imbalance. The **Blue Ocean quadrant** (high protein + low sugar) represents only ~25% of current SKUs, with **Nuts & Seeds** and **Protein Bars & Shakes** as the only categories with meaningful presence there today. The top three protein sources driving quality in Blue Ocean products are **Peanut**, **Almond**, and **Whey** — all well-established supply chains accessible to a new entrant. Cross-referencing the Blue Ocean quadrant with EU Nutri-Score grades (A–E) exposes a *double white space*: products combining high protein, low sugar, and a Nutri-Score A/B are almost entirely absent in the **Cereals & Granola** category, making it the clearest, most defensible R&D opportunity. Our recommendation is to launch a **High-Protein Granola line** (≥ 15g protein, < 5g sugar per 100g) using a peanut + whey protein blend, targeting Nutri-Score A/B certification for EU and UK market entry.

---

## B. Project Links

| Asset | Link |
|---|---|
| 📓 **Notebook (Google Colab)** | *(paste your Colab link here — File → Share → "Anyone with the link can view")* |
| 📊 **Dashboard (Streamlit)** | https://plank-panama-prepay.ngrok-free.dev/ |
| 🎞️ **Presentation (PDF/PPT)** | *(paste your Google Slides or Drive link here — permissions: "Anyone with link can view")* |
| 🎬 **Video Walkthrough** | *(optional — YouTube unlisted link)* |

> ⚠️ **Before submitting:** Open every link above in an **Incognito/Private window** to verify access without login. The Streamlit link in particular should load fully without asking for credentials.

---

## C. Technical Explanation

### Data Cleaning Strategy

The Open Food Facts dataset is notoriously noisy — it is crowdsourced, multilingual, and contains tens of thousands of mis-entered nutritional values. The cleaning pipeline applies five sequential rules:

1. **Mandatory field check** — Rows where `product_name`, `sugars_100g`, or `proteins_100g` are null or empty after stripping whitespace are dropped immediately. These fields are non-negotiable for the analysis.

2. **Numeric coercion** — All nutrient columns are force-coerced to numeric via `pd.to_numeric(..., errors='coerce')`. Non-parseable strings (e.g., `"n/a"`, `"<0.5"`) become `NaN` and are then dropped.

3. **Physiological bounds** — Any macro-nutrient value outside `[0, 100]` g per 100g is removed. It is physically impossible to have more than 100g of sugar in 100g of product. Energy is capped at 4,000 kcal/100g (the approximate ceiling for pure fat), removing absurd entries like `99,999 kcal`.

4. **Macro-sum sanity check** — Products where `sugars + proteins + fat > 105g` (allowing 5g for rounding) are removed as data-entry errors.

5. **Deduplication** — Exact duplicates on `product_name` are dropped (keeping the first occurrence), eliminating the same product entered by multiple contributors with slightly different nutritional values.

**Result:** ~57.5% of the raw 500,000 rows were retained — a conservative but defensible cut that prioritises analysis integrity over sample size.

**Column name resilience:** The dataset recently renamed `nutrition_grade_fr` to `nutriscore_grade`. The pipeline handles both names automatically, renaming the legacy column if found, and creating an empty column if neither exists — so the code never crashes on dataset updates.

### Candidate's Choice: Nutri-Score × Protein Heatmap

**What it is:** A heatmap crossing the 8 primary snack categories against EU Nutri-Score grades (A–E), with cell values showing average protein content per 100g.

**Why I added it:** This is the single most business-critical insight in the entire analysis that the brief didn't ask for. A snack manufacturer can build a product that is High Protein + Low Sugar and still *fail commercially* in the EU and UK because front-of-pack Nutri-Score labelling is now mandatory (France, Belgium, Netherlands, Germany, Spain — and expanding). A product scoring D or E due to sodium or saturated fat content will be actively deprioritised by retailers and rejected by health-conscious consumers, regardless of its macro profile.

By cross-referencing the Blue Ocean quadrant with Nutri-Score grade, I identified the **true investable white space**: category × grade combinations where high protein and a favourable label co-exist but very few products currently compete. This transforms a generic "launch a healthy snack" recommendation into a *regulatory-ready product brief* — the specific level of actionability that an R&D team needs to move into development. The finding (Cereals & Granola with Nutri-Score A/B is nearly empty at high protein levels) would not have surfaced from the scatter plot alone.

---

## Pre-Submission Checklist

- [ ] My GitHub Repo is **Public** (verified in Incognito window)
- [ ] I have uploaded the `.ipynb` notebook file (`sugar_trap_analysis_clean.ipynb`)
- [ ] I have uploaded the **HTML export** of the notebook (`sugar_trap_analysis.html`)
- [ ] I have **NOT** uploaded the raw dataset (it is in `.gitignore`)
- [ ] My code uses **Relative Paths** only (no hardcoded local paths)
- [ ] My Dashboard link is **publicly accessible** (no login required, tested in Incognito)
- [ ] My Presentation link is **publicly accessible**
- [ ] I have updated this `README.md` with Executive Summary and technical notes
- [ ] I have completed **User Stories 1–4**
- [ ] I have completed the **Candidate's Choice** challenge and explained it above

---

## Files in this Repository

| File | Description |
|---|---|
| `sugar_trap_analysis_clean.ipynb` | Main analysis notebook — Stories 1–4, Bonus, Candidate's Choice |
| `sugar_trap_analysis.html` | HTML export of the notebook (with rendered charts) |
| `streamlit_app.py` | Interactive Streamlit dashboard source code |
| `requirements.txt` | Python dependencies for Streamlit Cloud deployment |
| `.gitignore` | Prevents the 3GB+ raw CSV from being committed |
| `README.md` | This file |

---

## How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the Streamlit dashboard
streamlit run streamlit_app.py
```

The notebook downloads the Open Food Facts dataset automatically from the public CDN — no manual download required. Run it on Google Colab for best performance (the download is faster from Colab's servers).

---

## Original Brief

*The original project brief is preserved below for reference.*

---

# Project Brief: The "Sugar Trap" Market Gap Analysis

**Client:** Helix CPG Partners (Strategic Food & Beverage Consultancy)  
**Deliverable:** Interactive Dashboard, Code Notebook & Insight Presentation

## 1. Business Context

**Helix CPG Partners** advises major food manufacturers on new product development. Our newest client, a global snack manufacturer, wants to launch a "Healthy Snacking" line. They believe the market is oversaturated with sugary treats, but they lack the data to prove where the specific gaps are.

They have hired us to answer one question: **"Where is the 'Blue Ocean' in the snack aisle?"**

## 2. The Data

- **Source:** [Open Food Facts](https://world.openfoodfacts.org/data) — free, open, CC0
- **Format:** TSV (tab-separated), gzipped
- **Subset used:** First 500,000 rows (~57% retained after cleaning)

## 3. User Stories Completed

| Story | Status | Deliverable |
|---|---|---|
| Story 1: Data Ingestion & Clean-Up | ✅ | Cleaned DataFrame, 5 cleaning rules |
| Story 2: Category Wrangler | ✅ | 8 high-level buckets, keyword matching |
| Story 3: Nutrient Matrix | ✅ | Interactive scatter + dashboard filter |
| Story 4: Recommendation | ✅ | Key Insight box with specific g targets |
| Bonus: Hidden Gem | ✅ | Top 3 protein sources from ingredients |
| Candidate's Choice | ✅ | Nutri-Score × Protein heatmap + justification |
