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
                            categorical_imputation='mode')
        df_preprocess_info = classification.pull()
        best_model = classification.compare_models()
        df_compare = classification.pull()
        if save_model:
            classification.save_model(best_model, os.path.join(save_path, 'best_model'))

        return df_preprocess_info, df_compare

if __name__ == '__main__':
    m = Model(pd.read_csv('../Data/vehicle.csv'))
    pre, df = m.classify_models(target_col="Vehicle_Mass")
    print(pre)