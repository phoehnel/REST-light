# rest-light
Simple Microservice to control 433Mhz wireless sockets over HTTP, e.g. on a RaspberryPi



## How to Use

For the app to be able to use the Pi's GPIO-PINs, they need to be exposed to the container.
There are multiple options to do this, as explained [here](https://stackoverflow.com/a/48234752/8069229).

From the ones available, i had the best experience using the "device-approach" as stated below.

#### docker run

```ShellSession
docker run -it --device /dev/gpiomem -p 4242:4242 uupascal/rest-light:DEV-latest
```

#### docker-compose
```yaml
version: "3.8"

services:
  rest-light:
    container_name: rest-light
    image: "uupascal/rest-light:latest"
    restart: unless-stopped
    volumes:
        - "%APP_DATA_PATH/rest-light:/etc/rest-light"
    devices:
        - /dev/gpiomem
    ports:
        - 4242

```


## Credits

The project relies on [443Utils](https://github.com/ninjablocks/433Utils)