import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from .eda import EDA


class SuggestPreprocess:
    def __init__(self, dataframe: DataFrame):
        self._df = dataframe
        self._eda = EDA(self._df)

    def sg_constant_unique(self):
        """Return suggestion script about constant columns or unique values"""
        suggestion = ["Xử lý giá trị trong cột là constant hoặc unique:"]
        dict_chck_cons_uni = self._eda.check_constant_unique()

        if len(dict_chck_cons_uni['Constant']):
            suggestion.append(f"Bỏ các cột Constant: {dict_chck_cons_uni['Constant']}")
        if len(dict_chck_cons_uni['Unique Values']):
            suggestion.append(f"Bỏ các cột Unique Values: {dict_chck_cons_uni['Unique Values']}")

        return suggestion

    def sg_miss_value(self):
        """Return suggestion script about missing values"""
        suggestion = ["Xử lý missing value (tham khảo một trong các cách):"]
        is_miss_value = True if self._eda.check_miss_value()[0] else False
        if is_miss_value:
            suggestion.append(f"Xóa các Dòng hoặc Cột chứa missing value")
            suggestion.append(f"Điền Giá Trị Trung Bình, Trung Vị hoặc Mode vào missing cell")
            suggestion.append(f"Sử Dụng Các Phương Pháp Nội Suy (Interpolation): dùng cho time serís hoặc ordered data")
            suggestion.append(f"Điền Giá Trị Mặc Định:  0, unknown, ...")
            suggestion.append(f"Sử Dụng Các Phương Pháp Thống Kê Cao Cấp: Multiple Imputation, Expectation-Maximization")

        return suggestion

    def sg_imbalance(self):
        """Return suggestion script about imbalance columns"""
        suggestion = ["Xử lý các cột bị imbalance (tham khảo một trong các cách):"]
        is_imbalance = True if self._eda.check_imbalance()[0] else False
        if is_imbalance:
            suggestion.append(f"Thu thập thêm dữ liệu")
            suggestion.append(f"Resampling: Oversampling, Undersampling, Synthetic Minority Over-sampling Technique (SMOTE)")

        return suggestion

    def sg_outlier(self):
        """Return suggestion script about outliers"""
        suggestion = ["Xử lý outliers (tham khảo một trong các cách):"]
        is_outlier = True if self._eda.check_outliers()[0] else False
        if is_outlier:
            suggestion.append(f"Xóa các sample là Outlier")
            suggestion.append(f"Transform Dữ Liệu: log-transform, square-root transform, Robust Scaler")

        return suggestion

    def sg_correlate(self):
        """Return suggestion script about correlation of features"""
        suggestion = ["Xử lý hai đặc trưng có độ tương quan cao (từ 0.6 đến 1 hoặc -0.6 đến -1):"]
        is_corr = False
        try:
            corr_summary, _ = self._eda.correlation()
            for _, row in corr_summary.iterrows():
                for _, corr_value in row.items():
                    if 0.6 <= corr_value <= 1 or -1 <= corr_value <= -0.6:
                        is_corr = True
                        break
        except IndexError or RuntimeError:
            pass

        if is_corr:
            suggestion.append(f"Tìm cách kết hợp hai đặc trưng đó")
            suggestion.append(f"Loại bỏ một trong hai đặc trưng đó")

        return suggestion
