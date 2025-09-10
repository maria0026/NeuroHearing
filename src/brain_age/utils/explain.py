import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import RANSACRegressor, HuberRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_squared_error
from statsmodels.stats.diagnostic import het_white
from statsmodels.tools.tools import add_constant
from scipy.stats import skew, kurtosis
from scipy import stats

def calculate_trends(df, column, X_feature_name):

    X = df[X_feature_name].values
    huber = HuberRegressor()
    degree = 2
    model = make_pipeline(PolynomialFeatures(degree), huber)
    
    y = df[column].values
    model.fit(X, y)

    coefficients = huber.coef_
    intercept = huber.intercept_

    return model, coefficients, intercept


def white_test(df, column, X_feature_name, model):

    X = df[X_feature_name].values
    y = df[column].values
    #sort y by x
    L = sorted(zip(X,y))
    new_x, new_y = zip(*L)
    
    #white test
    residuals = new_y - model.predict(new_x)
    #add column of ones
    X_with_constant = add_constant(new_x)
    white_test = het_white(residuals,  X_with_constant)

    labels = ['Test Statistic', 'Test Statistic p-value', 'F-Statistic', 'F-Test p-value']
    white_test = dict(zip(labels, white_test))

    return white_test['F-Test p-value']


def scores(df, column, X_feature_name, model):

    X = df[X_feature_name].values
    y = df[column].values
    #sort y by x
    L = sorted(zip(X,y))
    new_x, new_y = zip(*L)

    new_y = new_y - model.predict(new_x)
    mean = np.mean(new_y)
    std = np.std(new_y, ddof=1)
    skewness = skew(new_y)
    kurt = kurtosis(new_y)

    mad = stats.median_abs_deviation(new_y)
    median = np.median(new_y)

    q1 = np.quantile(new_y, 0.25)
    q3 = np.quantile(new_y, 0.75)
    iqr = q3 - q1
    min_value = np.min(new_y)
    max_value = np.max(new_y)

    return mean, std, skewness, kurt, mad, median, iqr, min_value, max_value


def calculate_quantiles(df, column, X_feature_name, quantiles, model):
    X = df[X_feature_name].values
    y = df[column].values
    #sort y by x
    L = sorted(zip(X,y))
    new_x, new_y = zip(*L)
    new_y = new_y - model.predict(new_x)
    quantiles_array = []
    indices_array = []

    for quantile in quantiles:
        lower_quantile=np.quantile(new_y, quantile)
        upper_quantile=np.quantile(new_y, 1-quantile)
        quantiles_array.append(lower_quantile)
        quantiles_array.append(upper_quantile)
        indices_array.append(f'{quantile} quantile')
        indices_array.append(f'{1-quantile} quantile')

    return quantiles_array, indices_array

        
def calculate_normality(df, column, X_feature_name, df_scores):

    df_abnormalities = pd.DataFrame()
    X = df[X_feature_name].values
    y = df[column].values
    function_value = np.squeeze(df_scores.loc[column, 'intercept'] +df_scores.loc[column, '1']+ df_scores.loc[column, 'x']*X + df_scores.loc[column, 'x^2']*X**2)
    new_y = y - function_value
    #plt.plot(X, new_y, 'o', color='b', alpha=0.5, label='Predicted')
    #plt.show()
    for i in range(len(new_y)):
        if (new_y[i] >= df_scores.loc[column, '0.05 quantile'] and new_y[i] <= df_scores.loc[column, '0.95 quantile']):
            df_abnormalities.loc[i, column]=1
        elif (new_y[i] < df_scores.loc[column, '0.005 quantile'] or new_y[i] > df_scores.loc[column, '0.995 quantile']):
            df_abnormalities.loc[i, column]=0.005
            #print(new_y[i], df_scores.loc[column, '0.005 quantile'], df_scores.loc[column, '0.995 quantile'])
        elif (new_y[i] < df_scores.loc[column, '0.01 quantile'] or new_y[i] > df_scores.loc[column, '0.99 quantile']):
            df_abnormalities.loc[i, column]=0.01
        elif (new_y[i] < df_scores.loc[column, '0.02 quantile'] or new_y[i] > df_scores.loc[column, '0.98 quantile']):
            df_abnormalities.loc[i, column]=0.02
        elif (new_y[i] < df_scores.loc[column, '0.05 quantile'] or new_y[i] > df_scores.loc[column, '0.95 quantile']):
            df_abnormalities.loc[i, column]=0.05
        else:
            df_abnormalities.loc[i, column]=0

    return df_abnormalities


def create_features_results(df_abnormalities_all):
    df_features_results = pd.DataFrame()

    for ind, row in df_abnormalities_all.iterrows():
        for column in df_abnormalities_all.columns:
            if column not in ['identifier', 'lower', 'male']:
                if row[column] <= 0.01:
                    df_features_results = pd.concat([df_features_results, pd.DataFrame({'identifier': [ind], 'feature': [column], 'lower': [df_abnormalities_all.loc[ind, 'lower']], 'male': [df_abnormalities_all.loc[ind, 'male']]})])
    
    return df_features_results
