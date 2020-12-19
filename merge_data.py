import glob

import pandas as pd
import numpy as np


ts_type = "unnasigned"


assert ts_type in {"real", "synthetic", "unnasigned"}

indices = set()
not_in = set()


for j, files in enumerate(("datapoints", "metadata")):
    path = f"./zip_files_{ts_type}/comp-engine-export-{files}-*.csv"
    
    all_files = glob.glob(path)
    
    data = []
    
    for i, filename in enumerate(all_files):
        print(f"({files})", f"Loading file {i}...")
        cur_data = pd.read_csv(filename, index_col=0, header=0)
        data.append(cur_data)

        cur_inds = cur_data.index.to_list()

        if j == 0:
            indices.update(cur_inds)
    
    print("Done loading all data, now saving to '.csv'...")
    data = pd.concat(data, axis=0, ignore_index=False)
    data.to_csv(f"csv/{ts_type}_{files}.csv")

    if j == 1:
        assert not indices.symmetric_difference(data.index.to_list())

    print("Ok.")

    del data
