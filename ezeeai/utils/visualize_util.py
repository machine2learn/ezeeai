from scipy import stats
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np


def get_norm_corr(df):
    df_as_json = df.to_json(orient='split')

    for c in df.columns:
        if df[c].dtype == 'object':
            df[c] = df[c].astype('category')
    cat_columns = df.select_dtypes(['category']).columns
    df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)

    norm = {'line': [], 'bins': [], 'counts': []}

    cols_to_drop = []

    for col in df.columns:
        new_df = df[col].dropna()
        mu, sigma = stats.norm.fit(new_df)
        counts, bins, _ = plt.hist(new_df, 30, density=True)
        line = mlab.normpdf(bins, mu, sigma)
        if np.isnan(line).any():
            cols_to_drop.append(col)
            continue

        norm['line'].append(line.tolist())
        norm['bins'].append(bins.tolist())
        norm['counts'].append(counts.tolist())
        plt.close()

    corr = df.drop(columns=cols_to_drop).corr().values.tolist()
    num_rows = df.shape[0]
    norm['ccols'] = df.drop(columns=cols_to_drop).columns.tolist()
    return num_rows, df_as_json, norm, corr
