# Claims & Evidence

This document tracks key claims about Gemini Advanced and the evidence supporting or refuting them.

## Evidence Table

| Claim | Evidence Summary | Source/Date | File/Link |
|-------|-----------------|-------------|-----------|
| Performance regression 18-23% | Coding scores dropped from 82.1 (June 2024) to 67.3 (Dec 2024), representing 18% decline. Math scores dropped from 88.3 to 72.4, representing 18% decline. | Benchmark data 2024-06 through 2024-12 | `regression_timeline.csv` |
| Context window fails <2K tokens (despite 1M promise) | Users report context failures well below the advertised 1M token context window. Actual usable context appears limited to <2K tokens in practice. | User reports, 2024-Q4 | [Placeholder for evidence links] |
| Price discrimination ~12x | Israel charged $270/month vs USA $22/month for identical service - 12.27x price difference with no service differentiation. | Billing data, Nov 2024 | `billing_incidents.csv`, `price_comparison.csv` |
| Price-per-1M tokens higher (~$45) | Effective cost per 1M tokens is $45 across all regions despite base price differences, indicating token pricing not competitive with alternatives. | Pricing analysis, 2024-Q4 | `price_comparison.csv` |
| "Most capable" marketing claim vs actual benchmarks | Marketing claims "most capable" model, but benchmarks show GPT-4 Turbo outperforms on HumanEval (87.5 vs 82.1), GSM8K (92.0 vs 88.3), and Claude 3 Opus also leads on most metrics. | Benchmark comparison, 2024-Q4 | `performance_comparison.csv` |

## Data Sources

````
Performance benchmarks collected from:
- HumanEval (code generation)
- GSM8K (mathematical reasoning)
- MMLU (general knowledge)

Pricing data from official subscription tiers as of Q4 2024.
Billing incidents from customer support tickets.
````

## Notes

- All benchmark scores normalized to 0-100 scale
- Price comparisons use USD equivalents as of date recorded
- Regression timeline shows 6-month intervals
- Additional evidence links to be populated as documentation becomes available
