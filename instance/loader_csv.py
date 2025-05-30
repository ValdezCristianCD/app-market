import pandas as pd

def load_csv(engine, file):
    df = pd.read_csv(file)
    df.to_sql('ifood', con=engine, if_exists='append', index=False)
    return df
