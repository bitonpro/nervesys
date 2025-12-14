#!/usr/bin/env python3
"""
Gemini Audit Visualizations - Performance and Pricing Analysis

Generates visualizations from performance_comparison.csv, price_comparison.csv,
and regression_timeline.csv.

Outputs:
- performance_bars.png
- regression_timeline.png
- price_pie.png
- price_country_bars.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_palette("Set2")
plt.rcParams['figure.dpi'] = 200

def load_data():
    """Load all CSV data files."""
    performance = pd.read_csv('performance_comparison.csv')
    prices = pd.read_csv('price_comparison.csv')
    regression = pd.read_csv('regression_timeline.csv')
    return performance, prices, regression

def plot_performance_bars(performance):
    """Create bar chart comparing model performance across benchmarks."""
    plt.figure(figsize=(12, 6))
    
    # Create grouped bar chart
    benchmarks = performance['benchmark'].unique()
    x = range(len(benchmarks))
    width = 0.25
    
    models = performance['model'].unique()
    for i, model in enumerate(models):
        model_data = performance[performance['model'] == model]
        scores = [model_data[model_data['benchmark'] == b]['score'].values[0] 
                 for b in benchmarks]
        plt.bar([xi + i*width for xi in x], scores, width, label=model)
    
    plt.xlabel('Benchmark')
    plt.ylabel('Score')
    plt.title('Performance Comparison Across Models and Benchmarks')
    plt.xticks([xi + width for xi in x], benchmarks)
    plt.ylim(0, 100)
    plt.legend()
    plt.tight_layout()
    plt.savefig('performance_bars.png', dpi=200)
    plt.close()
    print("✓ Generated performance_bars.png")

def plot_regression_timeline(regression):
    """Create line chart showing performance degradation over time."""
    plt.figure(figsize=(10, 6))
    
    metrics = regression['metric'].unique()
    for metric in metrics:
        metric_data = regression[regression['metric'] == metric]
        plt.plot(metric_data['date'], metric_data['score'], 
                marker='o', linewidth=2, label=metric)
    
    plt.xlabel('Date')
    plt.ylabel('Score')
    plt.title('Performance Regression Timeline (June-December 2024)')
    plt.ylim(0, 100)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('regression_timeline.png', dpi=200)
    plt.close()
    print("✓ Generated regression_timeline.png")

def plot_price_pie(prices):
    """Create pie chart highlighting Israel vs USA pricing."""
    plt.figure(figsize=(8, 8))
    
    # Focus on Israel vs USA comparison
    comparison_data = prices[prices['country'].isin(['Israel', 'USA'])]
    
    plt.pie(comparison_data['monthly_price_usd'], 
            labels=comparison_data['country'],
            autopct='$%1.0f',
            startangle=90,
            colors=sns.color_palette("Set2"))
    
    plt.title('Price Discrimination: Israel ($270) vs USA ($22)')
    plt.tight_layout()
    plt.savefig('price_pie.png', dpi=200)
    plt.close()
    print("✓ Generated price_pie.png")

def plot_price_country_bars(prices):
    """Create bar chart showing monthly prices across all countries."""
    plt.figure(figsize=(10, 6))
    
    plt.bar(prices['country'], prices['monthly_price_usd'], 
            color=sns.color_palette("Set2"))
    
    plt.xlabel('Country')
    plt.ylabel('Monthly Price (USD)')
    plt.title('Monthly Subscription Prices by Country')
    plt.ylim(0, max(prices['monthly_price_usd']) * 1.1)
    
    # Add value labels on bars
    for i, (country, price) in enumerate(zip(prices['country'], 
                                             prices['monthly_price_usd'])):
        plt.text(i, price + 5, f'${price}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('price_country_bars.png', dpi=200)
    plt.close()
    print("✓ Generated price_country_bars.png")

def main():
    """Main execution function."""
    print("Loading data...")
    performance, prices, regression = load_data()
    
    print("\nGenerating visualizations...")
    plot_performance_bars(performance)
    plot_regression_timeline(regression)
    plot_price_pie(prices)
    plot_price_country_bars(prices)
    
    print("\n✓ All visualizations generated successfully!")
    print("\nOutput files:")
    print("  - performance_bars.png")
    print("  - regression_timeline.png")
    print("  - price_pie.png")
    print("  - price_country_bars.png")

if __name__ == '__main__':
    main()
