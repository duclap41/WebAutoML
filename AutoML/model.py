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
    def __init__(self, dataframe:DataFrame):
        self._df = dataframe

    def classify_models(self, target_col, save_model=False, save_path=any):
        """Compare all classifier models in pycaret, take model give best result"""
        classification.setup(data=self._df, target=target_col,
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

    def regressor_models(self, target_col, save_model=False, save_path=any):
        """Compare all classifier models in pycaret, take model give best result"""
        regression.setup(data=self._df, target=target_col,
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
