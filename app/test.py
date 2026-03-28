import pandas as pd
d = pd.read_csv('../data/deliveries.csv')
top = d.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(5)
print(top)