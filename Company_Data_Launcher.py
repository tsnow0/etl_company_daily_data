import sys
from DW_GlobalFunctions_Pkg.DW_Functions import dailyrun
import time
from pathlib import Path

if __name__ == '__main__':
    start_time = time.time()

    cur_dir = Path(__file__).parent

    # run pickle_refresh.py to update oproducts table and update the pickle file
    print('product pickle')
    exec(open(str(cur_dir / 'oproducts.py')).read())
    exec(open(str(cur_dir / 'pickle_refresh.py')).read())

    # run through each table's script and execute
    dailyrun()

    end_time = time.time()
    print(f"Runtime: {(end_time - start_time) / 60} minutes")
    sys.exit()