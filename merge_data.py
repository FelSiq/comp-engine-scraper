import glob
import argparse
import zipfile
import os

import pandas as pd
import numpy as np


parser = argparse.ArgumentParser(
    description="Merge collected time-series '.zip' files."
)

parser.add_argument(
    "data_type",
    type=str,
    help="Type of time-series to retrieve. Must be in {'real', 'synthetic', 'unassigned'}.",
)

parser.add_argument(
    "--no-unzip",
    action="store_true",
    help=(
        "If given, does not unzip data before merging. In this case, it is "
        "expected that the user unzipped the data manually before executing "
        "this script."
    ),
)

parser.add_argument(
    "--no-clean",
    action="store_true",
    help="If given, does not remove '.csv' pieces from '.zip' files after merging.",
)

args = parser.parse_args()

data_type = args.data_type
unzip = not args.no_unzip
clean = not args.no_clean

VALID_DATA_TYPE = {"synthetic", "real", "unassigned"}

assert (
    data_type in VALID_DATA_TYPE
), f"Given 'data_type' ('{data_type}') is invalid. Pick one from {VALID_DATA_TYPE}."

indices = set()
not_in = set()

base_dir_path = os.path.dirname(os.path.realpath(__file__))
input_dir = os.path.join(base_dir_path, f"zip_files_{data_type}")
output_dir = os.path.join(base_dir_path, "csv")

try:
    os.mkdir(output_dir)
    print("Created output directory for .zip files.")

except FileExistsError:
    print("Output directory found.")


if unzip:
    zpath = os.path.join(input_dir, f"*.zip")
    all_zfiles = glob.glob(zpath)

    for zipf_path in all_zfiles:
        with zipfile.ZipFile(zipf_path, "r") as zipf:
            zipf.extractall(input_dir)


for j, files in enumerate(("datapoints", "metadata")):
    path = os.path.join(input_dir, f"comp-engine-export-{files}-*.csv")
    all_files = glob.glob(path)

    if not all_files:
        raise RuntimeError(
            f"No data found. Did you ran 'scrape.py' for '{data_type}' data already?"
        )

    data = []

    for i, filename in enumerate(all_files):
        print(f"({files})", f"Loading file {i}...")
        cur_data = pd.read_csv(filename, index_col=0, header=0)
        data.append(cur_data)

        cur_inds = cur_data.index.to_list()

        if j == 0:
            indices.update(cur_inds)

    print("Done loading all data, now saving to '.csv'...")
    data = pd.concat(data, axis=0, ignore_index=False).drop_duplicates()
    data.to_csv(os.path.join(output_dir, f"{data_type}_{files}.csv"))

    if j == 1:
        assert not indices.symmetric_difference(data.index.to_list())

    print("Ok.")

    del data

if clean:
    tpath = os.path.join(input_dir, f"*.csv")
    all_tfiles = glob.glob(tpath)

    for tfile_path in all_tfiles:
        os.remove(tfile_path)
