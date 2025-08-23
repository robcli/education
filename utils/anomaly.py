import scipy
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

def plaw(x, a, b):
    return a*(x**(b))

def linear(x, a, b):
    return a*x+b

def calculate_r2(y_real, y_pred):
    ss_total = np.sum((y_real - np.mean(y_real))**2)
    ss_resid = np.sum((y_real - y_pred)**2)
    return 1 - (ss_resid / ss_total)

def fit(x, y, func):
    popt, pcov = scipy.optimize.curve_fit(func, x, y)
    fitted = func(x, *popt)
    return popt, fitted

def anomaly(scores, separate_years=True, suppress=False):
    def regress(df, func):
        coeffs, pred = fit(df["percent"], df["mean"], func)
        r2 = calculate_r2(df["mean"], pred)
        return coeffs, pred, r2
    
    def plot(df, coeffs, r2, suppress):
        lin_coeffs, plaw_coeffs = coeffs
        lin_r2, plaw_r2 = r2

        fig, ax = plt.subplots()
        sns.scatterplot(data=df,
                        x="percent",
                        y="mean")
        
        x = np.linspace(df["percent"].min(), df["percent"].max(), num=100)
        plt.plot(x, plaw(x, *plaw_coeffs), color="red")
        plt.plot(x, linear(x, *lin_coeffs), color="orange") 

        h = [Line2D([0], [0], color="red", label=f"power law, R^2: {plaw_r2:.4f}"),
             Line2D([0], [0], color="orange", label=f"linear, R^2: {lin_r2:.4f}")]
        ax.legend(handles=h)
        ax.set_ylabel("Average Score")
        ax.set_xlabel("Percentage Participation")
        if suppress:
            plt.close()
        return fig
    
    def apply(df, suppress):
        lin_coeffs, lin_pred, lin_r2 = regress(df, linear)
        plaw_coeffs, plaw_pred, plaw_r2 = regress(df, plaw)
        plot(df, (lin_coeffs, plaw_coeffs), (lin_r2, plaw_r2), suppress=suppress)
        return lin_pred, plaw_pred

    dfs = []
    if separate_years:
        years = scores["year"].unique()
        for year in years:
            yearly_scores = scores.query("year==@year")
            lin_pred, plaw_pred = apply(yearly_scores, suppress=suppress)
            if not suppress:
                plt.ylabel(f"Average Score ({year})")
            new = yearly_scores.assign(lin_pred = lin_pred).assign(plaw_pred=plaw_pred)
            dfs.append(new)
        return pd.concat(dfs)
    
    else:
        lin_pred, plaw_pred = apply(scores, suppress=suppress)
        return scores.assign(lin_pred = lin_pred).assign(plaw_pred=plaw_pred)