import pandas as pd
import numpy as np

def clean_price_column(series):

    cleaned_series = series.astype(str).copy()
    cleaned_series = cleaned_series.str.replace('US $', '', regex=False).str.replace('$', '', regex=False).str.replace(',', '', regex=False).str.strip()
    cleaned_series.replace(['', 'nan', 'N/A'], np.nan, inplace=True)
    return cleaned_series

def clean_data(input_file, output_file):

    try:
        df = pd.read_csv(input_file, dtype=str)
    except Exception:
        return

    # Step 1: Clean the string columns.
    df['price'] = clean_price_column(df['price'])
    df['original_price'] = clean_price_column(df['original_price'])
    
    # Step 2: Convert 'price' and drop rows where it's invalid.
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.dropna(subset=['price'], inplace=True)

    # Step 3: Convert 'original_price' and fill any invalid entries.
    df['original_price'] = pd.to_numeric(df['original_price'], errors='coerce')
    df['original_price'] = df['original_price'].fillna(df['price'])

    # Step 4: Clean the 'shipping' column.
    df['shipping'] = df['shipping'].fillna("Shipping info unavailable")

    # Step 5: Calculate the discount percentage.
    discount = df['original_price'] - df['price']
    df['discount_percentage'] = np.where(
        (df['original_price'] > 0) & (discount > 0),
        (discount / df['original_price']) * 100,
        0.0
    ).round(2)

    # Step 6: Save the final data.
    try:
        df.to_csv(output_file, index=False)
    except Exception:
        return

if __name__ == "__main__":
    clean_data("ebay_tech_deals.csv", "cleaned_ebay_deals.csv")