import pandas as pd
import numpy as np

def handle_null_values(df: pd.DataFrame, strategy: str = "mean", column_names: list = None) -> pd.DataFrame:
    """
    This function handles null values in a DataFrame based on the specified strategy.
    If 
    Parameters:
        df (pd.DataFrame): The input DataFrame with potential null values.
        strategy (str): The strategy to handle null values. Currently supports "mean", "mode", "median", "drop", "KNN". 
        column_names (list): The list of column names to apply the null handling strategy. If None, all columns are considered.
    Returns:
        pd.DataFrame: The DataFrame with null values handled according to the strategy.
    """
    if strategy == "mean":
        for column in (column_names if column_names is not None else df.columns):
            if df[column].isnull().any():
                mean_value = df[column].mean()
                df[column].fillna(mean_value, inplace=True)

    elif strategy == "mode":
        for column in (column_names if column_names is not None else df.columns):
            if df[column].isnull().any():
                mode_value = df[column].mode()[0]
                df[column].fillna(mode_value, inplace=True)

    elif strategy == "median":
        for column in (column_names if column_names is not None else df.columns):
            if df[column].isnull().any():
                median_value = df[column].median()
                df[column].fillna(median_value, inplace=True)

    elif strategy == "drop":
        df.dropna(subset=column_names, inplace=True)

    elif strategy == "KNN":
        from sklearn.impute import KNNImputer
        
        imputer = KNNImputer(n_neighbors=5)
        if column_names is None:
            df[:] = imputer.fit_transform(df)
        else:
            df[column_names] = imputer.fit_transform(df[column_names])

    return df