
#### Victoria-lite

Minimal WMS based on victoria-maps. 

This is a beta version building on a custom build of victoria, once changes are merged into victoria we can build on the victoria release images.

Many caveats here, the demo setup uses a file on lustre. If you want you can copy the file locally and update the path in `config/model_config.json`.

## Quickstart

- Clone the repository.
- If using the default setup with a file on lustre we need to make sure the lustre mount is initialised before starting the docker container, it's enough to do 

```
ls /lustre/storeB
```

- Then, to start the server, run:

```
docker compose up
```

The capabilities will then be available at:

```
http://localhost:8000/wms?service=WMS&request=GetCapabilities
```

- Paste this link into Geoweb's layer select, click "Save". Change service name if you like.
- In the layer select window, select the new pill with the name of the service you just added (default: "Victoria WMS").
- You should see a list of four parameters, select the ones you wish to look at, the model domain covers Malawi, so make sure you zoom to the right area to see the data.




- To remove everything so you can start from fresh, run:

```
docker compose down --volumes
```

Many more instructions on making config files and adapting the setup coming soon...