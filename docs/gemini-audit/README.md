# Gemini Audit Evidence Package

This directory contains a comprehensive audit of Gemini Advanced, including performance benchmarks, pricing analysis, billing incident documentation, and visualization tools.

## Contents

### Data Files (CSV)

- **performance_comparison.csv** - Benchmark scores for Gemini Advanced, GPT-4 Turbo, and Claude 3 Opus across HumanEval, GSM8K, and MMLU tests
- **price_comparison.csv** - Monthly subscription prices and effective cost per 1M tokens across USA, Israel, UK, and Australia
- **regression_timeline.csv** - Performance degradation over time (June-December 2024) for Coding and Math capabilities
- **billing_incidents.csv** - Template/sample billing incident records including regional price discrimination cases

### Documentation (Markdown)

- **claims_evidence.md** - Structured table of claims about Gemini with supporting evidence, sources, and data references
- **billing_analysis.md** - Comprehensive guide for analyzing billing patterns, computing metrics, and documenting findings
- **README.md** - This file; overview and usage instructions

### Visualization Scripts (Python)

- **viz.py** - Generates performance and pricing visualizations from benchmark and price data
- **viz_billing.py** - Generates billing incident analysis visualizations

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install required packages:
```bash
pip install pandas matplotlib seaborn
```

## Usage

### Generate Performance and Pricing Visualizations

```bash
python viz.py
```

**Outputs** (saved to current working directory):
- `performance_bars.png` - Bar chart comparing model performance across benchmarks
- `regression_timeline.png` - Line chart showing performance degradation over time
- `price_pie.png` - Pie chart highlighting price discrimination (Israel vs USA)
- `price_country_bars.png` - Bar chart showing monthly prices across all countries

### Generate Billing Analysis Visualizations

```bash
python viz_billing.py
```

**Outputs** (saved to current working directory):
- `billing_incidents_by_region.png` - Count of incidents per region
- `billing_charge_types.png` - Distribution of charge types
- `billing_dispute_status.png` - Status of billing disputes
- `billing_amounts_by_region.png` - Box plot of charge amounts by region

### Optional: Custom Output Directory

By default, PNG files are saved to the current working directory. To save to a specific location, you can modify the scripts or create a `figures/` subdirectory:

```bash
mkdir figures
# Then edit scripts to save to figures/ path if desired
```

## Visualization Details

All visualizations use:
- **DPI**: 200 (high resolution)
- **Color palette**: Seaborn Set2
- **Layout**: Tight layout for optimal spacing
- **Y-axis limits**: 0-100 for percentage-based metrics where appropriate

## Key Findings Summary

1. **Performance Regression**: 18-23% decline in Coding and Math scores from June to December 2024
2. **Price Discrimination**: Up to 12x price difference between regions (Israel: $270 vs USA: $22)
3. **Benchmark Claims**: Marketing claims of "most capable" not supported by comparative benchmarks
4. **Context Window**: Reports of failures below advertised 1M token capacity
5. **Token Pricing**: Effective cost per 1M tokens consistently ~$45 across regions

## Data Notes

- Benchmark scores normalized to 0-100 scale
- Prices in USD equivalent as of Q4 2024
- Billing incidents are sample/template data for analysis framework
- Additional evidence and documentation to be added as available

## Contributing

To add new data:
1. Update relevant CSV files with new rows
2. Maintain CSV format and column structure
3. Re-run visualization scripts to update charts
4. Update documentation with new findings

## Disclaimer

This package is for analytical and documentation purposes. Data should be verified independently before use in official reports or regulatory filings.
