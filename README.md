# 📊 Enhanced OEE Analysis Dashboard

A Streamlit-powered manufacturing intelligence dashboard for analyzing **Overall Equipment Effectiveness (OEE)** across machine-mold-operator combinations. Upload production data, explore interactive charts, and get AI-driven insights powered by GPT-4o-mini via the Portkey gateway.

---

## ✨ Features

- **OEE Analysis** — Automatically computes average OEE, quality rate, good part percentage, and run counts per machine-mold-operator combination.
- **Interactive Dashboard** — Four Plotly charts: OEE strip chart by operator, grouped bar chart of top combinations, planned vs. unplanned downtime, and good vs. bad parts pie chart.
- **Smart Filters** — Sidebar dropdowns to filter by Machine, Mold, and Operator; automatically shows top 7 machines when no filter is applied.
- **Live KPI Metrics** — Sidebar metrics for Average OEE, Best OEE, Total Combinations, Quality Rate, and Good Parts %.
- **Plastech AI Analysis** — One-click deep analysis covering performance summaries, top/underperforming combinations, pattern recognition, and actionable recommendations.
- **AI Q&A Assistant** — Ask plain-English questions about the dataset and get structured, data-grounded answers from the "Ask Plastech AI" tab.
- **Evaluated Data Table** — Full sortable results table showing all key metrics per combination.

---

## 🗂️ Project Structure

```
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API keys (not committed to repo)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- An OpenAI API key
- A Portkey API key (for LLM gateway/observability)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate        # macOS/Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**

   Create a `.streamlit/secrets.toml` file in the project root:
   ```toml
   OPENAI_API_KEY = "your-openai-api-key"
   PORTKEY_API_KEY = "your-portkey-api-key"
   ```
   > ⚠️ Never commit `secrets.toml` to version control. Add it to `.gitignore`.

5. **Run the app**
   ```bash
   streamlit run app.py
   ```

---

## 📦 Dependencies

```txt
streamlit
pandas
plotly
openai
portkey-ai
httpx
numpy
```

Generate a `requirements.txt` with:
```bash
pip freeze > requirements.txt
```

---

## 📁 Expected CSV Format

The app expects a production/manufacturing CSV with the following columns:

| Column | Description |
|--------|-------------|
| `Machine Name` | Name or ID of the machine |
| `Mold Name` | Name or ID of the mold used |
| `Operator` | Operator name |
| `OEE` | OEE value per production run (%) |
| `Good Part` | Count of good parts produced |
| `Bad Part (nos.)` | Count of defective parts |
| `Total Production` | Total parts produced |
| `Plan D/T` | Planned downtime in minutes |
| `Unplan D/T` | Unplanned downtime in minutes |

> The app automatically converts downtime from minutes to hours for visualization.

---

## 🧠 How It Works

### Data Processing
On CSV upload, `analyze_production_data()` groups the raw data by **Machine × Mold × Operator** and computes:
- Mean, std, and count of OEE per combination
- Summed good parts, bad parts, and total production
- Quality Rate = `(Good Parts / Total Parts) × 100`
- Planned and unplanned downtime totals (converted to hours)

### Visualizations
Four Plotly charts are generated dynamically based on sidebar filter selections:

| Chart | Description |
|-------|-------------|
| OEE Strip Chart | OEE distribution across top 15 operators |
| Grouped Bar Chart | Top 11 machine-operator combinations by average OEE |
| Downtime Bar Chart | Planned vs. unplanned downtime per machine |
| Quality Pie Chart | Overall good vs. bad parts ratio |

When all filters are set to "All", the downtime chart automatically focuses on the **top 7 machines** by total downtime to avoid clutter.

### AI Analysis (Plastech AI)
Two GPT-4o-mini powered endpoints handle AI features:

- **Generate AI Analysis** — Sends the filtered combinations table to the model with a structured prompt covering KPI summaries, top/underperforming combos, pattern recognition, and recommendations.
- **Ask Plastech AI** — Interprets free-text questions using NLP intent understanding, then returns data-grounded answers with tables or bullet points.

Both use `temperature=0.7` and `0.4` respectively, and route through Portkey for observability and gateway management.

---

## 🔒 Security Notes

- API keys are stored in Streamlit secrets and never exposed in the UI or source code.
- All processing is done in-memory — no data is persisted or sent externally beyond the OpenAI API calls.

---

## 🛠️ Customization

**Changing the AI model:** Update the `model` parameter in `get_openai_analysis()` and `get_openai_qa()`. Currently uses `gpt-4o-mini`.

**Adjusting top-N machine display:** Change `nlargest(7)` in `create_visualizations()` to show more or fewer machines when no filter is applied.

**Adding new metrics:** Extend the `.agg()` call in `analyze_production_data()` and add corresponding entries to `display_columns` in `main()`.

**Modifying the AI prompt:** Edit `analysis_prompt` inside `main()` to focus the AI on different aspects of your production data.

**Adding new chart types:** Add new Plotly figures inside `create_visualizations()` and render them in the dashboard tab with `st.plotly_chart()`.

---

## 📸 Screenshots

> Add screenshots of your dashboard, AI analysis output, and Q&A tab here.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

# Streamlit Deployment [link](https://plastech-ai.streamlit.app/)
