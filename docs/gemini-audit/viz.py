#!/usr/bin/env python3
"""
Visualization script for Gemini audit evidence package.
Reads CSV files and generates PNG charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style and color palette
sns.set_style("whitegrid")
sns.set_palette("Set2")

def create_performance_bars():
    """Generate performance comparison bar chart."""
    df = pd.read_csv('performance_comparison.csv')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Reshape data for grouped bar chart
    x = range(len(df))
    width = 0.25
    
    ax.bar([i - width for i in x], df['HumanEval'], width, label='HumanEval', alpha=0.8)
    ax.bar([i for i in x], df['GSM8K'], width, label='GSM8K', alpha=0.8)
    ax.bar([i + width for i in x], df['MMLU'], width, label='MMLU', alpha=0.8)
    
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Performance Comparison: Gemini Advanced vs GPT-4 Turbo vs Claude 3 Opus', 
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(df['Model'])
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('performance_bars.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("✓ Generated performance_bars.png")

def create_regression_timeline():
    """Generate regression timeline chart."""
    df = pd.read_csv('regression_timeline.csv')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(df['Month'], df['Coding'], marker='o', linewidth=2.5, 
            markersize=8, label='Coding', alpha=0.8)
    ax.plot(df['Month'], df['Math'], marker='s', linewidth=2.5, 
            markersize=8, label='Math', alpha=0.8)
    
    ax.set_xlabel('Month (2024)', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Gemini Performance Regression Timeline (June-December 2024)', 
                 fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('regression_timeline.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("✓ Generated regression_timeline.png")

def create_price_pie():
    """Generate price comparison pie chart (Israel vs USA)."""
    # Focus on Israel vs USA comparison
    countries = ['Israel', 'USA']
    prices = [270, 22]
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    colors = sns.color_palette("Set2", 2)
    wedges, texts, autotexts = ax.pie(prices, labels=countries, autopct='%1.1f%%',
                                        startangle=90, colors=colors,
                                        textprops={'fontsize': 12})
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)
    
    ax.set_title('Gemini Pricing Distribution: Israel ($270) vs USA ($22)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('price_pie.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("✓ Generated price_pie.png")

def create_price_country_bars():
    """Generate price comparison bar chart by country."""
    df = pd.read_csv('price_comparison.csv')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = sns.color_palette("Set2", len(df))
    bars = ax.bar(df['Country'], df['Monthly Price (USD)'], color=colors, alpha=0.8)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    ax.set_xlabel('Country', fontsize=12)
    ax.set_ylabel('Monthly Price (USD)', fontsize=12)
    ax.set_title('Gemini Advanced Monthly Pricing by Country', 
                 fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('price_country_bars.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("✓ Generated price_country_bars.png")

def main():
    """Main execution function."""
    print("=" * 60)
    print("Gemini Audit Visualization Generator")
    print("=" * 60)
    print("\nGenerating visualizations from CSV data...\n")
    
    try:
        create_performance_bars()
        create_regression_timeline()
        create_price_pie()
        create_price_country_bars()
        
        print("\n" + "=" * 60)
        print("All visualizations generated successfully!")
        print("=" * 60)
        print("\nOutput files:")
        print("  • performance_bars.png")
        print("  • regression_timeline.png")
        print("  • price_pie.png")
        print("  • price_country_bars.png")
        print("\nNote: PNGs are saved in the current working directory.")
        
    except FileNotFoundError as e:
        print(f"\n✗ Error: Could not find required CSV file: {e}")
        print("Please ensure you're running this script from the docs/gemini-audit/ directory.")
    except Exception as e:
        print(f"\n✗ Error generating visualizations: {e}")
        raise

if __name__ == "__main__":
    main()
