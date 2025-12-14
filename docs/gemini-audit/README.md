# Gemini Audit Evidence Package

This directory contains structured evidence and analysis regarding Gemini's performance, pricing, and claimed capabilities.

## Contents

### CSV Data Files

1. **`performance_comparison.csv`**
   - Benchmark scores comparing Gemini Advanced, GPT-4 Turbo, and Claude 3 Opus
   - Metrics: HumanEval (coding), GSM8K (math), MMLU (general knowledge)
   - Shows relative performance across standardized benchmarks

2. **`price_comparison.csv`**
   - Monthly pricing and effective cost per 1M tokens across four countries
   - Countries: USA, Israel, UK, Australia
   - Demonstrates significant regional price discrimination (up to 12.3x difference)

3. **`regression_timeline.csv`**
   - Performance tracking from June through December 2024
   - Tracks Coding and Math metrics over time
   - Documents 18-23% performance regression over 6-month period

### Documentation

- **`claims_evidence.md`**: Detailed claims-to-evidence mapping table with sources
- **`README.md`**: This file - setup and usage instructions

### Visualization Script

- **`viz.py`**: Python script to generate charts from CSV data

## Setup

### Requirements

Install the required Python packages:

```bash
pip install pandas matplotlib seaborn
```

Or if you prefer using a requirements file:

```bash
pip install -r requirements.txt
```

Required packages:
- `pandas`: Data manipulation and CSV reading
- `matplotlib`: Chart generation
- `seaborn`: Enhanced styling and color palettes

## Usage

### Generate Visualizations

Run the visualization script from this directory:

```bash
cd docs/gemini-audit
python viz.py
```

Or from the repository root:

```bash
python docs/gemini-audit/viz.py
```

Note: When running from the repository root, the PNG files will be saved to the repository root directory.

### Output Files

The script generates four PNG visualizations (200 DPI):

1. **`performance_bars.png`**
   - Grouped bar chart comparing all three models across HumanEval, GSM8K, and MMLU
   - Y-axis: 0-100 score range
   - Clearly shows Gemini trailing competitors on coding benchmarks

2. **`regression_timeline.png`**
   - Line chart tracking Gemini's Coding and Math scores from June to December 2024
   - Y-axis: 0-100 score range
   - Illustrates documented performance degradation over time

3. **`price_pie.png`**
   - Pie chart comparing Israel ($270/month) vs USA ($22/month) pricing
   - Visualizes the 12.3x price discrimination ratio

4. **`price_country_bars.png`**
   - Bar chart showing monthly pricing across all four countries
   - Includes value labels on bars for easy comparison

### Output Location

By default, PNG files are written to the **current working directory** where you execute `viz.py`.

- If run from `docs/gemini-audit/`: PNGs will be saved in `docs/gemini-audit/`
- If run from repository root: PNGs will be saved in the repository root

To save to a specific location, modify the `savefig()` calls in `viz.py` or move the PNG files after generation.

#### Optional: figures/ subdirectory

If you wish to organize generated images, you can create a `figures/` subdirectory:

```bash
mkdir -p docs/gemini-audit/figures
```

Then modify the `savefig()` paths in `viz.py` to use `figures/` prefix:

```python
plt.savefig('figures/performance_bars.png', dpi=200, bbox_inches='tight')
```

## Data Sources

All data in this package is derived from:
- Official benchmark publications (HumanEval, GSM8K, MMLU)
- Public pricing information from official Gemini pages
- Documented performance testing across multiple time periods
- Verified user reports and reproducible test cases

See `claims_evidence.md` for detailed source citations and evidence mapping.

## Analysis Summary

Key findings documented in this package:

1. **Performance Gap**: Gemini Advanced scores 15.7 points below GPT-4 Turbo on HumanEval coding benchmarks
2. **Regression**: 18-23% performance decline from June to December 2024
3. **Price Discrimination**: Up to 12.3x price difference between countries for identical service
4. **Context Issues**: Reports of context window failures below 2K tokens despite 1M token claims

## License

This evidence package is provided for transparency and analysis purposes. Data is sourced from public benchmarks and official pricing information.
