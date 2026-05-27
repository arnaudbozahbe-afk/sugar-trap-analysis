# 🍬 Sugar Trap — Blue Ocean Market Gap Analysis
### Helix CPG Partners · Strategic Food & Beverage Intelligence

---

## A. Executive Summary

We analysed over **500,000 snack products** from the Open Food Facts database to answer one question: *where is the white space in the snack aisle?*

The answer is clear. More than **60% of products** sit in what we call the "Saturated Zone" — high sugar, low protein — exactly what the market already has too much of. The **Blue Ocean quadrant** (high protein + low sugar) accounts for only ~25% of current products, and even within that space, most categories are thinly populated.

The biggest gap we found isn't in the obvious places. **Cereals & Granola** — a large, high-visibility category — is almost entirely empty at the intersection of high protein and a strong EU Nutri-Score (A or B). That's the double white space: a product that is nutritionally superior *and* carries a front-of-pack label that drives purchase intent in European markets.

Our recommendation is a **High-Protein Granola line** targeting **≥ 15g protein and < 5g sugar per 100g**, built around a **peanut + whey protein blend** — the two most common protein sources in Blue Ocean products today — and engineered for **Nutri-Score A/B** certification for EU and UK market entry.

---

## B. Project Links

| Asset | Link |
|---|---|
| 📓 Notebook (Google Colab) | *https://colab.research.google.com/drive/1E5u2DW3I9I7S6o3eCLjkSk7_D19dpLHA?usp=sharing* |
| 📊 Dashboard (Streamlit) | *https://sugar-trap-analysis-hbsybea2ap7kc9v3jeajmb.streamlit.app/* |
| 🎞️ Presentation | *[paste your Google Slides or PDF link here]* |


---

## C. Technical Notes

### Data Cleaning

The Open Food Facts dataset is crowdsourced and notoriously noisy — products entered in dozens of languages, many with missing or impossible nutritional values. The cleaning pipeline applies five rules in order:

1. **Mandatory fields** — rows missing `product_name`, `sugars_100g`, or `proteins_100g` are dropped immediately.
2. **Numeric coercion** — all nutrient columns are force-cast to numeric. Unparseable strings become `NaN` and are dropped.
3. **Physiological bounds** — any macro value outside `[0, 100]` g per 100g is removed. Energy is capped at 4,000 kcal/100g.
4. **Macro-sum check** — products where `sugars + proteins + fat > 105g` are removed as data-entry errors (the 5g buffer accounts for rounding).
5. **Deduplication** — exact duplicates on `product_name` are dropped, keeping the first occurrence.

**Result:** ~57.5% of the 500,000 rows were retained. Conservative, but it keeps the analysis honest.

One practical detail worth noting: the dataset recently renamed the `nutrition_grade_fr` column to `nutriscore_grade`. The pipeline handles both names automatically so the code won't break if you run it against an older or newer version of the dataset.

### Candidate's Choice — Nutri-Score × Protein Heatmap

The scatter plot tells you *where* the Blue Ocean is. The heatmap tells you *which part of it is actually winnable*.

A product can have great macros (high protein, low sugar) and still fail in the EU and UK if it scores D or E on Nutri-Score — front-of-pack labelling is now mandatory in France, Belgium, the Netherlands, Germany, and Spain, and retailers actively deprioritise low-scoring products. Building a product without this dimension in mind is building for a market that doesn't exist.

The heatmap crosses the 8 snack categories against Nutri-Score grades (A–E) and shows average protein content per cell. It makes one thing immediately visible: **Cereals & Granola with Nutri-Score A/B has almost no high-protein products**. That's a gap the scatter plot alone doesn't reveal — and it's the specific level of detail an R&D team needs to move from "launch a healthy snack" to an actual product brief.

---

## Files in this Repository

| File | Description |
|---|---|
| `sugar_trap_analysis.ipynb` | Main analysis notebook — Stories 1–4, Bonus, Candidate's Choice |
| `sugar_trap_analysis.html` | HTML export with all rendered charts |
| `streamlit_app.py` | Interactive dashboard source code |
| `requirements.txt` | Python dependencies for Streamlit Cloud |
| `.gitignore` | Keeps the 3GB+ raw CSV out of the repo |

---

## Running Locally

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The notebook downloads the Open Food Facts dataset directly from the public CDN — no manual file download needed. Running it on Google Colab is faster since the CDN download is quicker from Colab's servers.

