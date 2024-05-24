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
                    size=None,
                    title='Correlation Matrix of Features'):
        """Return correlation of every column\n
        targets is list columns, want to compare with others\n
        drops is list columns, want to ignore\n
        visual is visualized\n
        size is figure size\n
        title is title of plot"""

        new_df = EDA.drop_obj_bool_cols(self._df)
        new_df = new_df.drop(columns=drops)
        if len(targets) == 0:
            targets = new_df.columns
        corr_matrix = new_df.corr()
        corr_summary = corr_matrix[targets].sort_values(by=targets[0], ascending=False)

        # Visualize using heat map
        plt.figure(figsize=size)
        sns.heatmap(corr_matrix[targets], annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
        #plt.savefig('/imgs/corr.png')
        plt.title(title)
        plt.show()

        return corr_summary

    def corr_2cols(self, col1="", col2=""):
        """Return correlation value between 2 target columns"""
        if col1 == "":
            col1 = self._df.columns[0]
        if col2 == "":
            col2 = self._df.columns[-1]

        corr_matrix = self._df[[col1, col2]].corr()
        return corr_matrix.iloc[0, 1]

    # make clear data
    def checkOutliers(self, algo="IQR",
                      coef=1.5,
                      visual=False,
                      size=None,
                      drop=[],
                      rotate=0,
                      title="Box Plot of Feature Columns") -> tuple[int, DataFrame]:
        """
        Check outliers in every feature, return columns have outliers, ignoring column has data type is object or bool\n
        Algo is the algorithm will use to compute outliers\n
        Coef is IQR coefficient (1.5, 2, 3)\n
        Visual is visualized\n
        Size is size of figure\n
        Drop is list of columns want to ignore\n
        Rotate is the angle of label rotation\n
        Title is title of boxplot
        """
        # drop all columns can't check outliers
        rmCols = [col for col in self._df.columns
                 if (str(self._df[col].dtype) in ('object', 'bool'))]
        chk_outliers = self._df.drop(columns=rmCols)
        outliers = pd.DataFrame({
            'Coulumns':[],
            'Ouliers':[]
        })

        if algo == "IQR":
            # IQR (Interquartile Range)
            for col in chk_outliers:
                q1 = self._df[col].quantile(0.25) # percentile 25
                q3 = self._df[col].quantile(0.75) # percentile 70
                iqr = q3 - q1
                lower_bound = q1 - coef * iqr
                upper_bound = q3 + coef * iqr
                temp = chk_outliers[(chk_outliers[col] < lower_bound) | (chk_outliers[col] > upper_bound)]
                outliers = pd.concat([outliers, pd.DataFrame({
                    'Coulumns': [col],
                    'Ouliers': [int(temp.shape[0])]
                })], ignore_index=True)

        if visual:
            # using Boxplot
            plt.figure(figsize=size)
            sns.boxplot(data=chk_outliers.drop(columns=drop))
            plt.xticks(rotation=rotate)
            plt.title(title+"\n The dots are outliers")
            plt.show()

        total_ouliers = outliers["Ouliers"].sum()
        return total_ouliers, outliers
    def checkMissing(self) -> tuple[int, DataFrame]:
        """Check missing value in every feature, return total missing values and columns have missing values\n
        num_row is number of rows, want to see in missing values Dataframe
        """
        total_missvalues = self._df.isnull().sum().sum()

        missval_cols = pd.DataFrame({
            'Columns':[],
            'Missing Values':[]
        })
        for col in self._df.columns:
            missval_cols = pd.concat([missval_cols, pd.DataFrame({
                'Columns': [col],
                'Missing Values': [self._df[col].isnull().sum()]
            })], ignore_index=True)

        return total_missvalues, missval_cols

    def checkDuplicate(self):
        """Return total duplicated rows in Dataframe"""
        return self._df.duplicated().sum()



    def checkImbalance(self):
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
            'Columns':[],
            'Imbalance':[]
        })
        for col in self._df.columns:
            df_imblances = pd.concat([df_imblances, pd.DataFrame({
                'Columns': [col],
                'Imbalance': [is_imbalance(self._df, col)]
            })], ignore_index=True)

        return df_imblances

    def check_constant_unique(self) -> dict:
        """Return dictionary contain columns have constant or unique value."""
        cons_uni = {
            'Constant':[],
            'Unique Values':[]
        }
        for col in self._df.columns:
            if self._df[col].nunique() == 1:
                cons_uni['Constant'].append(col)
            if self._df[col].nunique() == self._df.shape[0]:
                cons_uni['Unique Values'].append(col)

        return cons_uni

    # features
    def distribution(self, column, size=None, kde=True, title="Distribution"):
        """Visualize distribution of feature using Histogram plot\n
        Size is size of figure\n
        kde is draw kde line or not"""
        plt.figure(figsize=size)
        sns.histplot(self._df[column], kde=kde)
        plt.title(title)
        plt.show()

    def interaction(self, col1, col2, size=None):
        """Visualize interaction between two features, don't use for 'object' or 'bool' columns"""
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=col1, y=col2, data=self._df)
        plt.xlabel(col1)
        plt.ylabel(col2)
        plt.title(f'Interaction between {col1} and {col2}')
        plt.show()


if __name__ == '__main__':
    df = pd.read_csv('../Data/titanic.csv')
    eda = EDA(df)
    print(eda.interaction('VRDeck', 'FoodCourt'))