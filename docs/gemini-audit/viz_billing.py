#!/usr/bin/env python3
"""
Gemini Audit Visualizations - Billing Incident Analysis

Generates visualizations from billing_incidents.csv.

Outputs:
- billing_incidents_by_region.png
- billing_charge_types.png
- billing_dispute_status.png
- billing_amounts_by_region.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_palette("Set2")
plt.rcParams['figure.dpi'] = 200

def load_billing_data():
    """Load billing incidents CSV data."""
    return pd.read_csv('billing_incidents.csv')

def plot_incidents_by_region(billing):
    """Create count plot of incidents by region."""
    plt.figure(figsize=(10, 6))
    
    sns.countplot(data=billing, x='region', palette='Set2')
    
    plt.xlabel('Region')
    plt.ylabel('Number of Incidents')
    plt.title('Billing Incidents by Region')
    plt.tight_layout()
    plt.savefig('billing_incidents_by_region.png', dpi=200)
    plt.close()
    print("✓ Generated billing_incidents_by_region.png")

def plot_charge_types(billing):
    """Create count plot of charge types."""
    plt.figure(figsize=(10, 6))
    
    sns.countplot(data=billing, x='charge_type', palette='Set2')
    
    plt.xlabel('Charge Type')
    plt.ylabel('Count')
    plt.title('Distribution of Billing Charge Types')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('billing_charge_types.png', dpi=200)
    plt.close()
    print("✓ Generated billing_charge_types.png")

def plot_dispute_status(billing):
    """Create count plot of dispute statuses."""
    plt.figure(figsize=(10, 6))
    
    sns.countplot(data=billing, x='dispute_status', palette='Set2')
    
    plt.xlabel('Dispute Status')
    plt.ylabel('Count')
    plt.title('Billing Dispute Status Distribution')
    plt.tight_layout()
    plt.savefig('billing_dispute_status.png', dpi=200)
    plt.close()
    print("✓ Generated billing_dispute_status.png")

def plot_amounts_by_region(billing):
    """Create box plot of charge amounts by region."""
    plt.figure(figsize=(10, 6))
    
    sns.boxplot(data=billing, x='region', y='amount_usd', palette='Set2')
    
    plt.xlabel('Region')
    plt.ylabel('Amount (USD)')
    plt.title('Billing Amounts by Region')
    plt.tight_layout()
    plt.savefig('billing_amounts_by_region.png', dpi=200)
    plt.close()
    print("✓ Generated billing_amounts_by_region.png")

def main():
    """Main execution function."""
    print("Loading billing data...")
    billing = load_billing_data()
    
    print(f"Loaded {len(billing)} billing incidents\n")
    
    print("Generating visualizations...")
    plot_incidents_by_region(billing)
    plot_charge_types(billing)
    plot_dispute_status(billing)
    plot_amounts_by_region(billing)
    
    print("\n✓ All billing visualizations generated successfully!")
    print("\nOutput files:")
    print("  - billing_incidents_by_region.png")
    print("  - billing_charge_types.png")
    print("  - billing_dispute_status.png")
    print("  - billing_amounts_by_region.png")

if __name__ == '__main__':
    main()
