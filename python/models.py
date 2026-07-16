"""
Predictive models for Transition Analysis.
"""

import statsmodels.formula.api as smf
import numpy as np
import pandas as pd

def logistic_pass_model(df):
    """
    Logistic regression predicting Pass 33130.
    """

    model = smf.logit(
        formula="""
        Q("Pass 33130")
        ~
        Q("Has 35010")
        + Q("Previous 33130 Fail")
        """,
        data=df
    )

    return model.fit(disp=False)
    
def odds_ratios(model):
    """
    Return odds ratios with 95% confidence intervals.
    """

    params = model.params

    conf = model.conf_int()

    table = pd.DataFrame({
        "Odds Ratio": np.exp(params),
        "Lower 95%": np.exp(conf[0]),
        "Upper 95%": np.exp(conf[1]),
        "P-value": model.pvalues
    })

    return table.round(3)


def logistic_pass_model2(df):
    """
    Logistic regression including SOS Level.
    """

    model = smf.logit(
        formula="""
        Q("Pass 33130")
        ~
        Q("Has 35010")
        + Q("Previous 33130 Fail")
        + C(Q("SOS Level"))
        """,
        data=df
    )

    return model.fit(disp=False)    
    
def model_summary(model, name):
    """
    Return a one-row summary of a fitted model.
    """

    return pd.DataFrame({
        "Model": [name],
        "Pseudo R²": [model.prsquared],
        "AIC": [model.aic],
        "BIC": [model.bic],
        "LogLik": [model.llf]
    })    
    
    
def fit_model(df, formula):
    """
    Fit any logistic regression model.
    """

    model = smf.logit(
        formula=formula,
        data=df
    )

    return model.fit(disp=False)    