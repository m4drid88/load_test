import pandas as pd

initial_df = pd.read_csv("data.csv")
scrap_df = pd.DataFrame({"age":[24,24],"name":["Jose","Daemon"]})

df = pd.concat([initial_df,scrap_df],axis=0)
df = df.drop_duplicates(subset="name")
df.to_csv("data.csv",index=False,mode="w")