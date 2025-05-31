from coverage_metrics import *
import glob

from constants import VALID_CALLEE_METHODS, VALID_CALLER_METHODS

if __name__ == "__main__":
    for m in VALID_CALLEE_METHODS:
        method_name = m.split(":")[1].split("(")[0]
        fnames = glob.glob(f"Processed Data/T*/P*/processed*{method_name}.csv")
        calculate_coverage_metrics(fnames, m)

    for m in VALID_CALLER_METHODS:
        method_name = m.split(":")[1].split("(")[0]
        fnames = glob.glob(f"Processed Data/T*/P*/processed*{method_name}.csv")
        calculate_coverage_metrics(fnames, m, up=True)