import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from eda import EDA


class SuggestPreprocess:
    def __init__(self, dataframe: DataFrame):
        self._df = dataframe
        self._eda = EDA(self._df)

    def run(self):
        pass

    def sg_constant_unique(self):
        suggestion = []
        dict_chck_cons_uni = self._eda.check_constant_unique()

        if len(dict_chck_cons_uni['Constant']):
            suggestion.append(f"Bạn nên bỏ các cột Constant: {dict_chck_cons_uni['Constant']}")
        if len(dict_chck_cons_uni['Unique Values']):
            suggestion.append(f"Bạn nên bỏ các cột Unique Values: {dict_chck_cons_uni['Constant']}")

        return suggestion

    def sg_miss_value(self): ...

    def sg_imbalance(self): ...

    def sg_outlier(self): ...

    def sg_correlate(self): ...

if __name__ == '__main__':
    sg = SuggestPreprocess(pd.read_csv('../Data/vehicle.csv'))
    print(sg.sg_constant_unique())