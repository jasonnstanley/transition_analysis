"""
Model result collection and export.
"""

import pandas as pd

import python.models as models
import python.diagnostics as diagnostics


class Results:
    def __init__(self, df, outcome):
        self.df = df
        self.outcome = outcome
        self.models = []

    def add_model(self, name, model):
        self.models.append((name, model))

    def model_comparison(self):
        rows = []

        for name, model in self.models:
            row = models.model_summary(model, name)
            row["ROC AUC"] = diagnostics.roc_auc(
                model,
                self.df,
                self.outcome
            )
            rows.append(row)

        return pd.concat(rows, ignore_index=True)

    def classification_metrics(self):
        rows = []

        for name, model in self.models:
            row = diagnostics.classification_metrics(
                model,
                self.df,
                self.outcome
            )
            row["Model"] = name
            rows.append(row)

        return pd.DataFrame(rows)
        
        
    def roc_auc(self, model):
        return diagnostics.roc_auc(
            model,
            self.df,
            self.outcome
        )

    def roc_curve_data(self, model):
        return diagnostics.roc_curve_data(
            model,
            self.df,
            self.outcome
        )


        