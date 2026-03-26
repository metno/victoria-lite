"""
Simple script for converting WRF output to CF-compliant NetCDF files.

You need a python environment with xarray and xwrf installed.

$ conda create -n wrf2cf python=3.12 xarray pyproj xwrf netcdf4 dask
$ conda activate wrf2cf
$ python convert_wrf_to_cf.py "wrfout_d01*" "out.nc"  # quotation marks are important

"""

import argparse
import numpy as np
import xarray as xr
import xwrf  # noqa: F401


def convert_wrf_to_cf(wrf_files_pattern: str, output_file: str):
    """
    Convert WRF output files to a single CF-compliant NetCDF file.

    Parameters:
    - wrf_files_pattern: A glob pattern to match the WRF output files (e.g., "wrfout_d01*").
    - output_file: The name of the output NetCDF file (e.g., "wrfout_cf_all_times.nc").
    """
    print(
        f"Converting WRF files matching pattern '{wrf_files_pattern}' to CF-compliant NetCDF file '{output_file}'. \n"
        "This may take a while depending on the size of the WRF output files..."
    )

    ds = xr.open_mfdataset(
        wrf_files_pattern,
        engine="netcdf4",
        concat_dim="Time",
        combine="nested",
    ).xwrf.postprocess()

    ds["wrf_projection"].data = np.full(ds["wrf_projection"].shape, np.nan)

    ds.to_netcdf(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert WRF output to CF-compliant NetCDF."
    )
    parser.add_argument(
        "wrf_files_pattern",
        type=str,
        help="A glob pattern to match the WRF output files (e.g., 'wrfout_d01*').",
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="The name of the output NetCDF file (e.g., 'wrfout_cf_all_times.nc').",
    )
    args = parser.parse_args()

    convert_wrf_to_cf(args.wrf_files_pattern, args.output_file)
