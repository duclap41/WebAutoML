from typing import Tuple, Any

import pandas as pd
from pandas import DataFrame
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


class EDA:
    """Exploratory Data Analysis"""

    def __init__(self, dataframe: DataFrame, name="Data Frame"):
        self._df = dataframe
        self._name = name

    @classmethod
    def drop_obj_bool_cols(cls, dataframe: DataFrame):
        # drop all columns can't check outliers
        rm_cols = [col for col in dataframe.columns if (str(dataframe[col].dtype) in ('object', 'bool'))]
        return dataframe.drop(columns=rm_cols)

    # identify data
    @property
    def columns(self) -> list:
        """Return column list in Dataframe"""
        col_names = [name for name in self._df.columns]
        return col_names

    @property
    def entries(self) -> int:
        """Return number sample in Dataframe"""
        return self._df.shape[0]

    def examine(self) -> DataFrame:
        """Return dtype of all columns in Dataframe"""
        df_info = pd.DataFrame({
            'Column': [col for col in self._df.columns],
            'Dtype': [self._df[col].dtype for col in self._df.columns]
        })
        return df_info

    def correlation(self, targets=[],
                    drops=[],
                    visual=False,
                    rotate=0,
                    size=None,
                    title='Correlation Matrix of Features'):
        """Return correlation of every column\n
        targets is list columns, want to compare with others\n
        drops is list columns, want to ignore\n
        Rotate is the angle of label rotation
        size is figure size\n
        title is title of plot"""

        new_df = EDA.drop_obj_bool_cols(self._df)
        new_df = new_df.drop(columns=drops)
        if len(targets) == 0:
            targets = new_df.columns
        corr_matrix = new_df.corr()
        corr_summary = corr_matrix[targets].sort_values(by=targets[0], ascending=False)

        # Visualize using heat map
        if visual is False:
            return corr_summary, None
        if size is not None:
            plt.figure(figsize=size)
        sns.heatmap(corr_matrix[targets], annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
        plt.xticks(rotation=rotate)
        plt.title(title)

        return corr_summary, plt

    # make clear data
    def check_outliers(self, algo="IQR",
                       coef=1.5,
                       size=None,
                       drop=None,
                       rotate=0,
                       title="Box Plot of Feature Columns") -> tuple[Any, DataFrame, plt]:
        """
        Check outliers in every feature, return columns have outliers, ignoring column has data type is object or bool
        Algo is the algorithm will use to compute outliers
        Coef is IQR coefficient (1.5, 2, 3)
        Size is size of figure
        Drop is list of columns want to ignore
        Rotate is the angle of label rotation
        Title is title of boxplot
        """
        # drop all columns which can't check outliers
        if drop is None:
            drop = []
        rmCols = [col for col in self._df.columns
                  if (str(self._df[col].dtype) in ('object', 'bool'))]
        chk_outliers = self._df.drop(columns=rmCols)
        df_outliers = pd.DataFrame({
            'Columns': [],
            'Outliers': []
        })

        if algo == "IQR":
            # IQR (Interquartile Range)
            for col in chk_outliers:
                q1 = self._df[col].quantile(0.25)  # percentile 25
                q3 = self._df[col].quantile(0.75)  # percentile 70
                iqr = q3 - q1
                lower_bound = q1 - coef * iqr
                upper_bound = q3 + coef * iqr
                temp = chk_outliers[(chk_outliers[col] < lower_bound) | (chk_outliers[col] > upper_bound)]
                df_outliers = pd.concat([df_outliers, pd.DataFrame({
                    'Columns': [col],
                    'Outliers': [int(temp.shape[0])]
                })], ignore_index=True)

        # add zscore algorithm

        # using Boxplot
        if size is not None:
            plt.figure(figsize=size)
        sns.boxplot(data=chk_outliers.drop(columns=drop))
        plt.xticks(rotation=rotate)
        plt.title(title + "\n The dots are outliers")

        return int(df_outliers["Outliers"].sum()), df_outliers, plt

    def check_miss_value(self) -> tuple[int, DataFrame]:
        """Check missing value in every feature, return total missing values and columns have missing values\n
        num_row is number of rows, want to see in missing values Dataframe
        """
        total_missvalues = self._df.isnull().sum().sum()

        df_missval = pd.DataFrame({
            'Columns': [],
            'Missing Values': []
        })
        for col in self._df.columns:
            df_missval = pd.concat([df_missval, pd.DataFrame({
                'Columns': [col],
                'Missing Values': [int(self._df[col].isnull().sum())]
            })], ignore_index=True)

        return int(total_missvalues), df_missval

    def check_duplicate(self):
        """Return total duplicated rows in Dataframe, and rows are duplicated"""
        return self._df.duplicated().sum()

    def check_imbalance(self):
        def is_imbalance(dataframe, col_name, threshold=0.9) -> bool:
            """Check columns is imbalance or not.\n
            Threshold: Ratio threshold between the most common class
            and the least common class to determine imbalance (default is 0.8)"""
            value_counts = dataframe[col_name].value_counts(normalize=True)
            if value_counts.min() == 0:
                return True
            if value_counts.max() / value_counts.min() > (1 / threshold):
                return True
            return False

        df_imblances = pd.DataFrame({
            'Columns': [],
            'Imbalance': []
        })
        for col in self._df.columns:
            df_imblances = pd.concat([df_imblances, pd.DataFrame({
                'Columns': [col],
                'Imbalance': [is_imbalance(self._df, col)]
            })], ignore_index=True)

        total_col_imbalance = sum(1 for i in df_imblances['Imbalance'] if i)

        return total_col_imbalance, df_imblances

    def check_constant_unique(self) -> dict:
        """Return dictionary contain columns have constant or unique value."""
        cons_uni = {
            'Constant': [],
            'Unique Values': []
        }
        for col in self._df.columns:
            if self._df[col].nunique() == 1:
                cons_uni['Constant'].append(col)
            if self._df[col].nunique() == self._df.shape[0]:
                cons_uni['Unique Values'].append(col)

        return cons_uni

    # features
    def distribution(self, column, size=None, kde=True):
        """Visualize distribution of feature using Histogram plot\n
        Size is size of figure\n
        kde is draw kde line or not"""
        if size is not None:
            plt.figure(figsize=size)
        sns.histplot(self._df[column], kde=kde)
        plt.title(f"Distribution of {column}")

        return plt

    def interaction(self, col1, col2, size=None):
        """Visualize interaction between two features, don't use for 'object' or 'bool' columns"""
        if size is not None:
            plt.figure(figsize=size)
        sns.scatterplot(x=col1, y=col2, data=self._df)
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.title(f'Interaction between {col1} and {col2}')

        return plt
