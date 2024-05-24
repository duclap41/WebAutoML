import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class EDA:
    """Exploratory Data Analysis"""
    def __init__(self, dataFrame:DataFrame, name="Data Frame"):
        self._df = dataFrame
        self._name = name

    # identify data
    def columns(self)->list:
        """Return column list in Dataframe"""
        lstColName = [name for name in self._df.columns]
        return lstColName
    def entries(self)->int:
        """Return number sample in Dataframe"""
        return self._df.shape[0]
    def examine(self)->DataFrame:
        """Return dtype of all columns in Dataframe"""
        df_info = pd.DataFrame({
            'Column': [col for col in self._df.columns],
            'Dtype': [self._df[col].dtype for col in self._df.columns]
        })

        return df_info

    # make clear data
    def checkOutliers(self, algo="IQR",
                      coef=1.5,
                      visual=False,
                      size=(12, 8),
                      drop=[],
                      rotate=0,
                      title="Box Plot of Feature Columns")->DataFrame:
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
                if (temp.shape[0] > 0):
                    outliers = outliers._append(pd.DataFrame({
                        'Coulumns': [col],
                        'Ouliers': [int(temp.shape[0])]
                    }))

        if visual == True:
            # using Boxplot
            plt.figure(figsize=size)
            sns.boxplot(data=chk_outliers.drop(columns=drop))
            plt.xticks(rotation=rotate)
            plt.title(title+"\n The dots are outliers")
            plt.show()

        return outliers
    def clear(self):...

    # features
    def features(self):...


if __name__ == '__main__':
    df = pd.read_csv('../Data/titanic.csv')
    eda = EDA(df)
    print(eda.checkOutliers(algo="IQR", coef=1.5))