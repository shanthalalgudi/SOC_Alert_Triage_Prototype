# SOC Alert Triage Prototype

A lightweight AI-assisted proof-of-concept for prioritizing security alerts using simple, explainable risk scoring logic.

## Features

- **Alert Loading**: Load security alerts from JSON or CSV files
- **Risk Scoring**: Compute risk scores based on severity, asset type, and frequency
- **Interactive Dashboard**: Streamlit UI with real-time filtering
- **HTML Reports**: Generate standalone HTML reports for sharing
- **CLI Output**: Quick text-based reporting for terminal use

## Project Structure

```
├── data_loader.py        # Load and normalize alert data
├── scoring_engine.py     # Risk scoring logic
├── app.py               # CLI pipeline & HTML report generation
├── dashboard.py         # Streamlit interactive dashboard
├── mock_alerts.json     # Sample alert data
├── alert_triage_report.html # Generated HTML report
└── README.md
```

## Alert Schema

Expected fields in alert data:
- `alert_id`: Unique identifier
- `source`: Alert source (IDS, EDR, SIEM, etc.)
- `severity`: Alert severity (low, medium, high)
- `asset_type`: Target asset type (standard, important, critical)
- `frequency`: Number of times alert triggered
- `timestamp`: ISO 8601 timestamp

## Installation

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install streamlit pandas
```

## Usage

### CLI Report
```bash
python app.py
```
Outputs a text report to console and generates `alert_triage_report.html`

### Interactive Dashboard
```bash
streamlit run dashboard.py
```
Opens browser at http://localhost:8501

## Filtering Options

- **Risk Score Threshold**: Slider (0-100)
- **Severity Level**: Multi-select (low, medium, high)
- **Asset Type**: Multi-select (standard, important, critical)
- **Priority Level**: Multi-select (Critical, High, Medium, Low)
- **Alert Source**: Multi-select (IDS, EDR, SIEM, etc.)

## Scoring Logic

**Risk Score Formula:**
```
base_score = (severity_weight + asset_weight) / 2
frequency_boost = frequency * frequency_factor
risk_score = min(100, base_score + frequency_boost)
```

**Default Weights:**
- Severity: low=20, medium=50, high=90
- Asset Type: standard=10, important=50, critical=100
- Frequency Factor: 0.1 per occurrence

**Priority Classification:**
- Critical: risk_score >= 60
- High: risk_score >= 40
- Medium: risk_score >= 20
- Low: risk_score < 20

## Customization

Modify weights and thresholds in `app.py`:

```python
engine = ScoringEngine(
    severity_weights={'low': 20, 'medium': 50, 'high': 90},
    asset_weights={'standard': 10, 'important': 50, 'critical': 100},
    frequency_factor=0.1,
    risk_threshold=60.0
)
```

## Notes

- This is a proof-of-concept, not production-ready code
- Uses mock data only (no external APIs)
- Designed for clarity and simplicity over performance
- All code is Python standard library + Streamlit/Pandas

## Author

Created by Shanth Algudi

## License

MIT
