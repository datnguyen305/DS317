import pandas as pd

from .checking_type_of_missing_value import MissingValueAnalyzer


def handle_null_values(
    df: pd.DataFrame,
    strategy: str = "mean",
    column_names: list = None,
) -> pd.DataFrame:
    """Handle null values in a DataFrame based on the specified strategy.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame with potential null values.
    strategy : str
        The strategy to handle null values.
        Supports "mean", "mode", "median", "drop", "KNN", "auto".
        If "auto" is selected:
        - For MCAR columns: drop rows with missing values
        - For skewed columns: use mode imputation
        - For non-skewed columns: use mean imputation
    column_names : list, optional
        The list of column names to apply the null handling strategy.
        If None, all columns are considered.

    Returns
    -------
    pd.DataFrame
        The DataFrame with null values handled according to the strategy.
    """
    columns_to_process = column_names if column_names is not None else df.columns

    if strategy == "mean":
        for col in columns_to_process:
            if df[col].isnull().any():
                mean_val = df[col].mean()
                df[col].fillna(mean_val, inplace=True)

    elif strategy == "mode":
        for column in columns_to_process:
            if df[column].isnull().any():
                mode_value = df[column].mode()[0]
                df[column].fillna(mode_value, inplace=True)

    elif strategy == "median":
        for column in columns_to_process:
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
            cols_subset = df[column_names]
            df[column_names] = imputer.fit_transform(cols_subset)

    elif strategy == "auto":
        # Initialize MissingValueAnalyzer
        analyzer = MissingValueAnalyzer(df)

        # Get analysis for columns
        analyze_cols = column_names if column_names is not None else df.columns
        missing_stats = analyzer.get_missing_stats(analyze_cols)

        # Create a copy to avoid modifying the original while iterating
        df_copy = df.copy()

        for column, stats in missing_stats.items():
            if stats["mcar"] == 1:
                # For MCAR, drop rows with missing values in this column
                df_copy.dropna(subset=[column], inplace=True)
            else:
                # For non-MCAR, use mode if skewed, mean if not skewed
                if df[column].isnull().any():
                    if stats["skewness"] == 1:
                        # Skewed distribution: use mode
                        mode_value = df[column].mode()[0]
                        df_copy[column].fillna(mode_value, inplace=True)
                    else:
                        # Not skewed: use mean
                        mean_value = df[column].mean()
                        df_copy[column].fillna(mean_value, inplace=True)

        return df_copy

    return df
