"""
Model diagnostics for Transition Analysis.
"""

from sklearn.metrics import roc_auc_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import (
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    balanced_accuracy_score,
)    
from sklearn.metrics import roc_curve

def predicted_probabilities(model, df):
    """
    Return predicted probabilities from a fitted model.
    """
    return model.predict(df)


def roc_auc(model, df, outcome):
    """
    Calculate ROC AUC for a fitted model.
    """
    y_true = df[outcome]
    y_prob = predicted_probabilities(model, df)

    return roc_auc_score(y_true, y_prob)
    
  

def confusion(model, df, outcome, threshold=0.5):
    """
    Return confusion matrix and accuracy.
    """

    y_true = df[outcome]

    y_prob = model.predict(df)

    y_pred = (y_prob >= threshold).astype(int)

    cm = confusion_matrix(y_true, y_pred)

    acc = accuracy_score(y_true, y_pred)

    return cm, acc    
    
    
def classification_metrics(model, df, outcome, threshold=0.5):
    """
    Return a dictionary of classification metrics.
    """

    y_true = df[outcome]

    y_prob = model.predict(df)

    y_pred = (y_prob >= threshold).astype(int)

    metrics = {
        "Precision": precision_score(y_true, y_pred),
        "Recall": recall_score(y_true, y_pred),
        "F1": f1_score(y_true, y_pred),
        "Balanced Accuracy": balanced_accuracy_score(y_true, y_pred),
    }

    return metrics
    
    
def roc_curve_data(model, df, outcome):
    """
    Return ROC curve data for a fitted model.
    """

    y_true = df[outcome]
    y_prob = model.predict(df)

    fpr, tpr, thresholds = roc_curve(y_true, y_prob)

    return fpr, tpr, thresholds


    