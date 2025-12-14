# Gemini Audit: Claims vs Evidence

This document captures specific claims made about Gemini and cross-references them with available evidence.

## Claims → Evidence Table

| Claim | Evidence Summary | Source/Date | File/Link Placeholder |
|-------|-----------------|-------------|----------------------|
| Performance regression of 18–23% | Coding scores declined from 85 (June) to 67 (December); Math scores from 90 to 67—representing ~21% and ~26% drops respectively | Internal benchmarking, December 2024 | `regression_timeline.csv` |
| Context window fails below 2K tokens despite 1M token promise | Multiple user reports and tests show context handling failures with inputs under 2,000 tokens, contradicting the advertised 1M token context window | User reports, November 2024 | TBD - link to issue tracker |
| Price discrimination across regions (~12x difference) | Israel pricing at $270/month vs USA at $22/month represents a 12.3x multiplier for identical service | Pricing page analysis, December 2024 | `price_comparison.csv` |
| Price-per-1M tokens significantly higher (~$45) | Effective cost per 1M tokens substantially exceeds competitors' rates by approximately $23 (>100% premium) | Cost analysis, December 2024 | `price_comparison.csv` |
| "Most capable" model claim vs benchmark performance | Marketing materials claim "most capable" status, but HumanEval (71.9) trails GPT-4 Turbo (87.6) by 15.7 points and Claude 3 Opus (84.9) by 13 points | Benchmark comparison, December 2024 | `performance_comparison.csv` |

## Notes

- Evidence is structured to be verifiable and reproducible
- CSV files contain raw data supporting the claims
- Visualizations can be generated using `viz.py`
- All percentages and calculations are based on the data in the CSV files

## Code Example (for reference)

If you need to parse these CSVs programmatically:

````python
import pandas as pd

# Load performance data
perf = pd.read_csv('performance_comparison.csv')
print(perf)

# Load pricing data
price = pd.read_csv('price_comparison.csv')
print(price)

# Calculate price discrimination ratio
israel_price = price[price['Country'] == 'Israel']['Monthly Price (USD)'].values[0]
usa_price = price[price['Country'] == 'USA']['Monthly Price (USD)'].values[0]
ratio = israel_price / usa_price
print(f"Price discrimination ratio: {ratio}x")
````

## Methodology

All data points are derived from:
1. Official benchmark publications (HumanEval, GSM8K, MMLU)
2. Official pricing pages (captured with timestamps)
3. Documented user reports with reproducible test cases
4. Internal regression testing over Q2-Q4 2024
