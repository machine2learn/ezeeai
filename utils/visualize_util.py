from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab


def get_norm_corr(df):
    df_as_json = df.to_json(orient='split')

    for c in df.columns:
        if df[c].dtype == 'object':
            df[c] = df[c].astype('category')
    cat_columns = df.select_dtypes(['category']).columns
    df[cat_columns] = df[cat_columns].apply(lambda x: x.cat.codes)

    norm = {'line': [], 'bins': [], 'counts': []}

    for col in df.columns:
        new_df = df[col].dropna()
        mu, sigma = stats.norm.fit(new_df)
        counts, bins, _ = plt.hist(new_df, 30, density=True)
        line = mlab.normpdf(bins, mu, sigma)
        norm['line'].append(line.tolist())
        norm['bins'].append(bins.tolist())
        norm['counts'].append(counts.tolist())

    corr = df.corr().values.tolist()

    return df_as_json, norm, corr
