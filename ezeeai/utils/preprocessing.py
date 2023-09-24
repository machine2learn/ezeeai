import pandas as pd
import csv


def clean_field_names(filename):
    args = {}
    if not has_header(filename):
        args['header'] = None

    df = pd.read_csv(filename, sep=None, engine='python', **args)

    df.columns = df.columns.astype(str)
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    df.columns = df.columns.str.replace('(', '').str.replace(')', '').str.replace('.', '_')
    df.columns = df.columns.str.replace('=', '_').str.replace(':', '-')

    # if columns duplicated change
    cols = pd.Series(df.columns)
    #dups = df.columns.get_duplicates()
    dups = df.columns[df.columns.duplicated()].unique() 
    for dup in dups:
        cols[df.columns.get_loc(dup)] = [dup + '_' + str(d_idx) if d_idx != 0 else dup for d_idx in
                                         range(df.columns.get_loc(dup).sum())]

    df.columns = cols

    for c in df.columns:
        try:
            df[c] = df[c].astype(str).str.replace(',', '')
        except:
            pass

    df.to_csv(filename, index=False)
    return df


def check_train(train_file, targets):
    if len(targets) > 1:
        return True
    df = pd.read_csv(train_file)
    if df[targets[0]].dtype == 'object':
        if len(df[targets[0]].unique()) < 2:
            return False
    return True


def has_header(csvfile, close=True):
    if isinstance(csvfile, str):
        csvfile = open(csvfile, 'r')
    sniffer = csv.Sniffer()
    sample_bytes = 50

    try:
        has_header = sniffer.has_header(csvfile.read(sample_bytes))
    except:
        #csvfile.seek(0)
        #has_header = sniffer.has_header(csvfile.read(sample_bytes + 50))  # TODO it does not work!!
        has_header = True

    if close:
        csvfile.close()
    else:
        csvfile.seek(0)
    print(str(csvfile) + ' has header: ' + str(has_header))
    return has_header
