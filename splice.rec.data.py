import pandas as pd

df = pd.read_csv("ml/data/crop.rec.csv")

df = df.groupby('label').nth(1)

df.to_json("vite/src/sample.crop.rec.json", orient="index")