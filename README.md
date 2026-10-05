
## Victoria-lite

Minimal WMS based on [victoria-maps](https://gitlab.met.no/met/proj/magellan/victoria-maps).

This is a beta version based on a custom Victoria build. Once these changes are merged into Victoria, we can use the Victoria release images.


### Prerequisites

To run this, you will need:
- Docker and Docker Compose installed ([set up instuctions for MET internal laptops](https://it.brukerdok.met.no/klienter/linux/noble/50-installer-programvare.html#docker-og-docker-compose))

### Quickstart

- Clone the repository.

```
git clone https://github.com/metno/victoria-lite.git
```

If you are working in a country which has a preconfigured setup you need to checkout the branch for your country (we currently have setups for malawi, tanzania and vietnam):

```
git checkout <country-name>
```

If you do not have a preconfigured setup, you will have to read the instructions under "How to configure data sources" and create a configuration before proceeding.

If you want to use your own local data directory, set `VICTORIA_DATA_PATH`, e.g.

```
export VICTORIA_DATA_PATH=/absolute/path/to/your/data
```

Alternatively, you can place data in a folder `data` under victoria-lite, which will automatically be mounted into the image.

- Then, to start the server, run:

```
docker compose up
```

Or set the environment variable inline (this means it is not persisted in your local environment):

```
VICTORIA_DATA_PATH=/absolute/path/to/your/data docker compose up
```

The capabilities will then be available at:

```
http://localhost:8000/wms?service=WMS&request=GetCapabilities
```

- Paste this link into GeoWeb's layer select and click "Save". Change the service name if you like.
- In the layer select window, select the new pill with the name of the service you just added (default: "Victoria WMS").
- You should see a list of four parameters. Select the ones you want to view. The example model domain covers Malawi, so make sure you zoom to the right area to see the data.
- You can also use the `i` icon to get values at a point (currently not supported for vector layers), and use the legend to check that the style is correct.

- To remove everything so you can start from fresh, run:

```
docker compose down --volumes
```

It is a good tip to run `docker compose down --volumes` whenever your configuration or datafiles change.

### How to configure data sources

The main place to set up a new model is `config/model_config.json`. The configuration file can contain as many different models as you like, e.g.

```
{
    "model_1": {
        ....
    },
    "model_2": {
        ....
    },
    "model_3": {
        ....
    }        
}
```

Each model can then be set up as follows.

The model key (in this case `bris-malawi`) is the name Victoria uses to identify the model, and it will be visible in GeoWeb.
```
{
    "bris-malawi": {
```
The format should be either `nc-static` for NetCDF files or `zarr-static` for Zarr stores (note that Zarr on S3 requires additional setup).
```
        "format": "nc-static",
```
`path` is the path to the data _inside the Docker container_. If the data is on your local PC or a connected network drive, you can either place it in a folder called `data/` in the directory you run `docker compose up` from, or set the `VICTORIA_DATA_PATH` environment variable to point to the folder containing the file. In both cases, the file will then be available at `/data/<my-file.nc>`.
```
        "path": "/data/20260105T00-0_025.nc",
```

The time config currently requires you to set the model start time, time step (in hours) and length of the model run (in hours). This will be removed in later versions.
```
        "time_config": {
            "start_time": "2026-01-05T00:00:00Z",
            "interval_hours": 6,
            "duration_hours": 240
        },
```
Under `variables`, list the scalar variable names you would like to view from the NetCDF file.
```
        "variables": [
            "air_temperature_2m",
            "air_pressure_at_sea_level",
            "precipitation_amount_acc"
        ],
```
Vector fields (i.e., arrows or wind barbs, which have two components) have a slightly more complex setup. The key, in this case `wind_10m_vector`, is the layer name used in requests. `long_name` is used as the display name in GeoWeb. Set the `x` and `y` components to the NetCDF parameter names. You can also set unit conversion (currently scaling and offset). Here, values are scaled by `1.94384` to convert from m/s to knots.
```
        "vector_fields": {
            "wind_10m_vector": {
                "x": "x_wind_10m",
                "y": "y_wind_10m",
                "long_name": "Wind vector at 10m",
                "unit_conversion": {
                    "scale": 1.94384,
                    "offset": 0
                }
            }
        },
```
Victoria attempts to match a style to a parameter based on parameter units. This works in some cases, but in others the chosen styles may not be what you want. For more control, use the `style_config` section. Here, list each variable you defined above and explicitly set a style category (from `unit_palette_config.json`). You can also override the layer title and set unit conversion by scaling and offset. Setting `"deaccumulate": true` calculates the difference between timesteps, primarily for precipitation fields that are often accumulated in NetCDF files.

```
        "style_config": {
            "air_temperature_2m": {
                "title": "Air temperature at 2m",
                "style_category": "temperature_C",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": -273.15
                }
            },
            "air_pressure_at_sea_level": {
                "title": "Air pressure at sea level",
                "style_category": "pressure",
                "unit_conversion": {
                    "scale": 0.01,
                    "offset": 0.0
                }
            },
            "precipitation_amount_acc": {
                "title": "Deaccumulated precipitation amount",
                "style_category": "amount",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": 0.0,
                    "deaccumulate": true
                }
            }
        },
```
Keywords can help when searching for layers in GeoWeb, but they are not particularly important. This can also be set to an empty list: `"keywords": []`. (This will most likely be made optional in future versions.)
```
        "keywords": [
            "bris",
            "malawi",
            "weather",
            "forecast"
        ]
    }
}
```

The full config for one model then looks something like:


```
{
    "bris-malawi": {
        "format": "nc-static",
        "path": "/data/20260105T00-0_025.nc",
        "time_config": {
            "start_time": "2026-01-05T00:00:00Z",
            "interval_hours": 6,
            "duration_hours": 240
        },
        "variables": [
            "air_temperature_2m",
            "air_pressure_at_sea_level",
            "precipitation_amount_acc"
        ],
        "vector_fields": {
            "wind_10m_vector": {
                "x": "x_wind_10m",
                "y": "y_wind_10m",
                "long_name": "Wind vector at 10m",
                "unit_conversion": {
                    "scale": 1.94384,
                    "offset": 0
                }
            }
        },
        "style_config": {
            "air_temperature_2m": {
                "title": "Air temperature at 2m",
                "style_category": "temperature_C",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": -273.15
                }
            },
            "air_pressure_at_sea_level": {
                "title": "Air pressure at sea level",
                "style_category": "pressure",
                "unit_conversion": {
                    "scale": 0.01,
                    "offset": 0.0
                }
            },
            "precipitation_amount_acc": {
                "title": "Deaccumulated precipitation amount",
                "style_category": "amount",
                "unit_conversion": {
                    "scale": 1.0,
                    "offset": 0.0,
                    "deaccumulate": true
                }
            }
        },
        "keywords": [
            "bris",
            "malawi",
            "weather",
            "forecast"
        ]
    }
}
```

### WRF NetCDF files

The NetCDF files output by the WRF model do not follow the NetCDF-CF convention, which is what Victoria currently expects. The simplest solution for now is to convert the WRF output files to CF convention. A simple conversion script is included in the repository for this purpose. To use it, you will need a Python environment with `xarray` and `xwrf` installed. To do this with conda, you could run:
```
$ conda create -n wrf2cf python=3.12 xarray pyproj xwrf netcdf4 dask
$ conda activate wrf2cf
```

In this environment, you can then run the Python script. WRF output is usually one NetCDF file per timestep, so you can use a wildcard `*` to select all files you wish to combine. It is important to use quotation marks when using the wildcard.
```
$ python convert_wrf_to_cf.py "wrfout_d01*" "<out-file-name>.nc"
```

You can then use the output NetCDF file as normal with the Victoria configuration.

Depending on the size of the model files, conversion can take some time and storage space. If you want to save time and/or disk space, you can adapt the conversion script to select or drop variables from the xarray dataset as needed. If you do this, make sure all relevant coordinate variables and grid mappings are kept in the resulting xarray dataset.

### Adding new styles and customising existing styles

The currently available colour palettes are defined in `palettes.json`. These are used by style definitions in `unit_palette_config.json`. The `unit_palette_config.json` file starts with a list of style categories that work with different units. Victoria uses this to automatically add a style based on the unit defined in the NetCDF file if you do not define a specific parameter under `style_config` in `model_config.json`; however, this is not particularly smart and it just picks the first matching style category in the list, so it may be necessary to choose a style category explicitly. Each style category contains a list of styles that are available for the layer (selectable from the style dropdown in GeoWeb).

Each style name either matches a palette name, or contains a reference to which colour palette it uses, e.g. `"palette": "Yellow-orange"`. It then defines a list of intervals that match the number of colours in the selected palette, and options for specifying whether the style should be discrete colours or a gradient.

The simplest way to add a new style is to add it under an existing category. If you want to create your own category, you must define it at the top of the `unit_palette_config.json` file with relevant units. Then add the category definition under `category` with the desired style configurations.

Try copying and adapting existing styles to see if you can get what you want. If you have problems, contact a member of the Victoria team.

### Troubleshooting

#### Layers visible in capabilities/layer select, but no data shown in GeoWeb when a layer is selected

- Check that the time step is within the model range.
- Check for any errors in the terminal log
- There may be an issue reading the projection. In that case, try adding a projection parameter in the model config, e.g. `projection: "EPSG:4326"`, where you can specify an EPSG code or proj string (use an EPSG code rather than a proj string if possible). This attempts to override the model projection. If this works, check that the projection is correctly defined in the NetCDF file.
- Check that the data values are within the ranges specified by the style palette. The legend and the `i` icon can be useful in GeoWeb for check this.
