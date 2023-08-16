import pandas as pd

data = [["Jose","Melgarejo",28]]
colums = ["name","lastname","age"]

df = pd.DataFrame(data,columns=colums)
df.to_csv("data.csv",mode="a",header=False,index=False)
