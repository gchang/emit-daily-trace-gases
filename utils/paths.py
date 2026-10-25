import os.path
from utils.rio_utils import file_exists

def codebase_folder():
    # the folder that holds utils/ (this file's parent's parent), so it works without a .git folder too
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def models_storage():
    codebase = codebase_folder()
    return os.path.join(codebase,"models","JPL_TRACE_GASES_MODELS")

def lut_file_path():
    # Source for the LUT file:
    # paper: Impact of scene-specific enhancement spectra on matched filter greenhouse gas retrievals from imaging spectroscopy
    # URL (on The Hive: University of Utah Research Data Repository): https://hive.utah.edu/records/d47hd-s1z16 / dataset_ch4_full.hdf5
    # URL Mirror also available via https://github.com/AlFe23/hygas
    special_paths = [
        "YOUR_DOWNLOAD_PATH/dataset_ch4_full.hdf5",
    ]
    for special_path in special_paths:
        if file_exists(special_path):
            # at least one found:
            return special_path

    print("None of the paths for LUT file exists!", special_paths)
    assert False
