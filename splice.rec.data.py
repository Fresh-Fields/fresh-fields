import pandas as pd


def fill_and_interpolate(file_path):
    # Read CSV into a DataFrame
    df = pd.read_csv(file_path)

    # Convert 'Date' column to datetime format
    df["Price Date"] = pd.to_datetime(df["Price Date"])
    df = df.drop(
        columns=["Min Price (Rs./Quintal)", "Max Price (Rs./Quintal)"], errors="ignore"
    )
    # Sort DataFrame by date
    df = df.sort_values(by="Price Date")

    # Create a new DataFrame with a complete date range
    complete_dates = pd.date_range(
        start=df["Price Date"].min(), end=df["Price Date"].max(), freq="D"
    )
    complete_df = pd.DataFrame({"Price Date": complete_dates})

    # Merge the original DataFrame with the complete DataFrame to fill missing dates
    df = pd.merge(complete_df, df, on="Price Date", how="left")

    # Interpolate missing values
    df["Modal Price (Rs./Quintal)"] = df["Modal Price (Rs./Quintal)"].interpolate()

    return df


for district in ["Bhiwandi", "Nagpur", "Ulhasnagar", "Palghar", "Vasai"]:
    file_path = f"./ml/data/market/{district}.Rice.csv"
    result_df = fill_and_interpolate(file_path)
    result_df.to_csv(f"./ml/data/{district}.Rice.csv", index=False)
