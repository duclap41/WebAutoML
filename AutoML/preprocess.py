import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Preprocess:
    def __init__(self, dataframe:DataFrame):
        self._df = dataframe

    def fill_miss_val(self):...

    def rec_outliers(self) -> list[str]:
        """Return recommend methods to process outliers."""
        pass