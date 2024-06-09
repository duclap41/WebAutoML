import base64
import io
import os
import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pycaret import classification, regression


class Model:
    def __init__(self, dataframe: DataFrame):
        self._df = dataframe

    def check_type(self, target_col):
        column = self._df[target_col]
        if str(column.dtype) in ['bool', 'object']:
            return "Categorical"

        elif pd.api.types.is_numeric_dtype(column):
            if column.nunique() / len(column) < 0.01:
                return "Discrete"
            else:
                return "Continuous"

    def classify_models(self, target_col, drop_features=[], save_model=False, save_path=any):
        """Compare all classifier models in pycaret, take model give best result"""
        data = self._df.drop(columns=drop_features)
        if data[target_col].isnull().any():
            if str(data[target_col].dtype) in ['bool', 'object']:
                unique_values = data[target_col].dropna().unique()
                data[target_col] = data[target_col].fillna(np.random.choice(unique_values))
            else:
                data[target_col] = data[target_col].fillna(data[target_col].mean())
        classification.setup(data=data,
                             target=target_col,
                             remove_outliers=True,
                             imputation_type='simple',
                             numeric_imputation='mean',
                             categorical_imputation='mode',
                             use_gpu=False)
        df_preprocess_info = classification.pull()
        best_model = classification.compare_models()
        df_compare = classification.pull()

        if save_model:
            classification.save_model(best_model, os.path.join(save_path, 'best_model'))

        return df_preprocess_info, df_compare

    def regressor_models(self, target_col, drop_features=[], save_model=False, save_path=any):
        """Compare all classifier models in pycaret, take model give best result"""
        data = self._df.drop(columns=drop_features)
        data[target_col] = data[target_col].fillna(data[target_col].mean())
        regression.setup(data=data,
                         target=target_col,
                         remove_outliers=True,
                         imputation_type='simple',
                         numeric_imputation='mean',
                         categorical_imputation='mode',
                         use_gpu=False)
        df_preprocess_info = regression.pull()
        best_model = regression.compare_models()
        df_compare = regression.pull()

        if save_model:
            regression.save_model(best_model, os.path.join(save_path, 'best_model'))

        return df_preprocess_info, df_compare
