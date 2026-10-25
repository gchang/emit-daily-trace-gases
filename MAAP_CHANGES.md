# Changes from upstream

Upstream: https://github.com/emit-sds/daily-trace-gases, tag `v1.0.2` at commit c5b9e9138d80237ac0cdca5630396f4a86f6e919 (2026-10-09, "Release version 1.0.2 support for DiffMF"), by Vít Růžička and the EMIT team at JPL, Apache License 2.0 (`LICENCE`). Paper: Růžička et al. 2026, "Fully automatic trace gas plume detection", Scientific Reports, doi:10.1038/s41598-026-70499-1. The model weights are not in the repository; they come from Hugging Face (`previtus/JPL_TRACE_GASES_MODELS`) under their own license.

This copy starts from upstream's file tree at c5b9e91 without its git history. Nothing was left out (upstream has no `.github` folder). It is unchanged except for the items below. The matched filters, the models, the scoring, the parameter files and the LICENCE are untouched.

## 2026-10-25: `-enable_diffmf` is a real on/off flag

`detect_trace_gas.py` declared `-enable_diffmf` with `default='False'` and no type, so argparse kept the text `'False'`, which Python treats as true. Every command-line run took the DiffMF path even without the flag. For CH4 that meant the V002/DiffMF branch (`pipeline/run_for_ch4.py:20`), which stops with `None of the paths for LUT file exists! ['YOUR_DOWNLOAD_PATH/dataset_ch4_full.hdf5']` (`utils/paths.py`). For NH3, NO2 and CO it made the 3-band `<gas>-cmf_diffmf.tif` instead of the plain CMF. So the README's example commands did not run as written.

The value is now read as a word: `True`, `true`, `1` or `yes` turn DiffMF on, anything else (including no flag) leaves it off. `-enable_diffmf True` works as the README says. The notebook calls `detect_trace_gas()` directly and was never affected. Results are the same as a run with DiffMF off, which is what the README commands are meant to produce.

## 2026-10-25: h5py is declared

`pipeline/A_matched_filter/cmf_emit_ghg/target_generation.py` imports `h5py`, and it is loaded for every gas, but `requirements.txt`, `pyproject.toml` and `uv.lock` did not list it, so a fresh install stopped at `No module named 'h5py'`. It is now in all three (`uv lock` with uv 0.9 added only h5py 3.16.0; every other pin is as it was).

## 2026-10-25: environment.yml

A one-step version of the README's "Option 1 using conda": Python 3.11, GDAL, a CPU build of PyTorch, torchvision and h5py from conda-forge, then `requirements.txt` and `huggingface_hub` (for the `hf` command) through pip. Taking PyTorch from conda-forge first matters on Linux, where `pip install torch` brings several GB of CUDA libraries even without a GPU. The README mentions it next to Option 1:

```sh
conda env create -f environment.yml
conda activate trace_gases_env
```

## 2026-10-25: the code folder is found without git

`utils/paths.py` found the code folder (for `parameters/` and `models/`) by asking GitPython for the working tree around the current directory, so the code only ran from inside a git clone. A copy from a release archive, or a container image built without `.git`, stopped before the run started. It now uses the folder two levels above `utils/paths.py`, which is the same folder for a normal clone, so nothing moves. GitPython is no longer imported but is still listed in the dependency files.

## Known issues, not changed

- **Earthdata login at import time.** `utils/download_utils.py:5` runs `earthaccess.login()` when the module is imported, and the pipeline imports it for every run. A run therefore needs network access and Earthdata credentials (`~/.netrc` or the `EARTHDATA_USERNAME` and `EARTHDATA_PASSWORD` variables) even when all inputs are already on disk. Moving the login into `download_granule` would fix it.
- **Memory.** One CH4 scene peaks at about 12 GB (the scoring step loads the full 285-band radiance cube and makes a copy, `pipeline/C_plume_scoring/run_scoring.py`); one NH3 scene at about 10 GB. 8 GB machines run out of memory.
- **LUT for V002 and DiffMF.** V002 radiance scenes and `-enable_diffmf True` need `dataset_ch4_full.hdf5` (from https://hive.utah.edu/records/d47hd-s1z16), and `utils/paths.py` only looks for it at the placeholder `YOUR_DOWNLOAD_PATH/`. Edit that path after downloading it. V001 scenes without DiffMF do not need it.
- `pyproject.toml` asks for Python 3.12 or newer, while the conda route uses 3.11; both work.
- With the conda route, the pip wheels of rasterio and pyproj carry their own PROJ, and writing the NH3 CMF prints harmless `PROJ: proj_create_from_database` errors. The output CRS is correct.

## Check

On 2026-10-25, from a fresh `git clone` of this repository on Linux (x86_64, 4 cores, 14 GB memory limit), in a new env made with `conda env update -f environment.yml` on an empty Python 3.11 env (Python 3.11.17, PyTorch 2.14.1 CPU, torchvision 0.29.1, GDAL 3.13.3, numpy 2.4.6, rasterio 1.4.4, earthaccess 0.17.0, h5py 3.16.0), after `hf download previtus/JPL_TRACE_GASES_MODELS --local-dir models/JPL_TRACE_GASES_MODELS`:

```sh
python -m detect_trace_gas -gas "ch4" -tile "EMIT_L1B_RAD_001_20260102T143123_2600209_005"
```

It ran to the end in 1 min 26 s, including the 2.0 GB download from LP DAAC, with a peak of 12.2 GB. The 11 scored plume polygons match the output stored in `notebooks/detect_trace_gases.ipynb`: the same pixel counts, the same confidences to 6 decimals, and spectral-fit scores (`D_norm`) within 0.0042, the same as the unchanged code gives with `-enable_diffmf ""`.

The same command on `EMIT_L1B_RAD_001_20240812T213903_2422514_030` (Permian Basin, Texas), run from a copy with no `.git` folder, took 1 min 25 s with a peak of 11.8 GB. Its detections cover all 6 human-reviewed plume complexes of the official EMIT L2B CH4PLM product for that scene (003439 to 003444, confidence 0.88 to 0.99), exactly as with the unchanged code.
