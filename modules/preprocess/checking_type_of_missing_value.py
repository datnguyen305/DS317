from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.imputation import test


class MissingValueAnalyzer:
    """Analyze missing values in DataFrame columns.

    This class provides methods to check and analyze missing values
    (NaN and None) in pandas DataFrames.

    Attributes
    ----------
    df : pd.DataFrame
        The DataFrame to analyze.
    significance_level : float
        Significance level for statistical tests (default: 0.05).
    """

    def __init__(self, df: pd.DataFrame, significance_level: float = 0.05):
        """Initialize the MissingValueAnalyzer.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to analyze for missing values.
        significance_level : float, optional
            The significance level for statistical tests, by default 0.05
        """
        self.df = df
        self.significance_level = significance_level

    def check_columns_exist(self, column_names: List[str]) -> List[str]:
        """Check if specified columns exist in the DataFrame.

        Parameters
        ----------
        column_names : List[str]
            List of column names to check.

        Returns
        -------
        List[str]
            List of columns that don't exist in the DataFrame.
        """
        return [col for col in column_names if col not in self.df.columns]

    def analyze_single_column(self, column_name: str) -> Tuple[float, float, str]:
        """Analyze missing value types in a single column.

        Parameters
        ----------
        column_name : str
            Name of the column to analyze.

        Returns
        -------
        Tuple[float, float, str]
            A tuple containing (chi-square statistic, p-value, result type).
        """
        return test.missing_values_types(self.df[column_name])

    def check_missing_value_types(
        self,
        column_names: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Check missing value types in DataFrame columns.

        Parameters
        ----------
        column_names : List[str], optional
            List of columns to check. If None, checks all columns.

        Returns
        -------
        Dict[str, str]
            Dictionary mapping column names to their missing value types:
            - "NaN": Only NaN values found
            - "None": Only None values found
            - "Both": Both NaN and None found
            - "No Missing Values": No missing values found
            - "Column not found": Column doesn't exist in DataFrame

        Examples
        --------
        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'A': [1, None, pd.NA, 4],
        ...     'B': [1, 2, pd.NA, None]
        ... })
        >>> analyzer = MissingValueAnalyzer(df)
        >>> analyzer.check_missing_value_types(['A', 'B'])
        {'A': 'Both', 'B': 'Both'}
        """
        if column_names is None:
            column_names = list(self.df.columns)

        results = {}
        missing_columns = self.check_columns_exist(column_names)

        for column in column_names:
            if column in missing_columns:
                results[column] = "Column not found"
                continue

            chi2, p_value, result = self.analyze_single_column(column)
            results[column] = result

        return results

    def check_mcar(self, column: str) -> Tuple[bool, float]:
        """Check if missing values in a column are Missing Completely At Random (MCAR).

        Uses Little's MCAR test to determine if missing values are MCAR.

        Parameters
        ----------
        column : str
            Name of the column to test.

        Returns
        -------
        Tuple[bool, float]
            (is_mcar, p_value) where is_mcar is True if missing values are MCAR
            (p_value > significance_level)
        """
        if column not in self.df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")

        # Create indicator column (1 for missing, 0 for non-missing)
        missing_indicator = self.df[column].isna().astype(int)

        # Get other numeric columns
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        numeric_cols = [col for col in num_cols if col != column]

        if not numeric_cols.empty:
            # Perform t-tests between missing and non-missing groups
            t_stats = []
            p_values = []
            for other_col in numeric_cols:
                missing_group = self.df[other_col][missing_indicator == 1]
                non_missing_group = self.df[other_col][missing_indicator == 0]

                if len(missing_group) > 0 and len(non_missing_group) > 0:
                    t_stat, p_val = stats.ttest_ind(
                        missing_group.dropna(), non_missing_group.dropna()
                    )
                    t_stats.append(t_stat)
                    p_values.append(p_val)

            # If any relationship is significant, data is not MCAR
            is_mcar = all(p > self.significance_level for p in p_values)
            min_p_value = min(p_values) if p_values else 1.0

            return is_mcar, min_p_value

        return True, 1.0  # If no numeric columns to compare, assume MCAR

    def analyze_distribution(self, column: str) -> Dict[str, Any]:
        """Analyze value distribution in a column.

        Parameters
        ----------
        column : str
            Name of the column to analyze.

        Returns
        -------
        Dict[str, Any]
            Distribution statistics:
            - skewness: Distribution asymmetry
            - is_normal: If distribution is normal
            - normality_test: Shapiro-Wilk results
            - distribution_type: Data distribution type
        """
        if column not in self.df.columns:
            raise ValueError(f"Column {column} not found in DataFrame")

        data = self.df[column].dropna()
        if not np.issubdtype(data.dtype, np.number):
            return {
                "error": "Column is not numeric",
                "distribution_type": "non-numeric",
            }

        # Calculate skewness and normality
        skewness = stats.skew(data)
        shapiro_result = stats.shapiro(data)
        shapiro_stat, shapiro_p = shapiro_result
        is_normal = shapiro_p > self.significance_level

        # Classify distribution type
        if is_normal:
            dist_type = "normal"
        else:
            if abs(skewness) < 0.5:
                dist_type = "approximately symmetric"
            elif skewness < 0:
                dist_type = "left-skewed"
            else:
                dist_type = "right-skewed"

        return {
            "skewness": skewness,
            "is_normal": is_normal,
            "normality_test": {"statistic": shapiro_stat, "p_value": shapiro_p},
            "distribution_type": dist_type,
        }

    def get_missing_stats(
        self,
        column_names: Optional[List[str]] = None,
    ) -> Dict[str, Dict]:
        """Get simplified missing value analysis for columns.

        Parameters
        ----------
        column_names : List[str], optional
            List of columns to analyze. If None, analyzes all columns.

        Returns
        -------
        Dict[str, Dict]
            Dictionary with binary indicators for each column:
            {'column_name': {'mcar': 0 or 1, 'skewness': 0 or 1}}
            - mcar: 1 if Missing Completely At Random, 0 if not
            - skewness: 1 if data is skewed (|skewness| > 0.5), 0 if not
        """
        if column_names is None:
            column_names = list(self.df.columns)

        stats = {}
        for column in column_names:
            if column not in self.df.columns:
                continue

            column_stats = {}

            # Check MCAR
            is_mcar, _ = self.check_mcar(column)
            column_stats["mcar"] = 1 if is_mcar else 0

            # Check skewness only for numeric columns
            data = self.df[column].dropna()
            if np.issubdtype(data.dtype, np.number):
                skewness = stats.skew(data)
                column_stats["skewness"] = 1 if abs(skewness) > 0.5 else 0
            else:
                column_stats["skewness"] = 0

            stats[column] = column_stats

        return stats
