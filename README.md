![REST-light Logo](https://user-images.githubusercontent.com/20238923/148686271-14e32a8b-8ad2-4a8d-9be1-1acbff51b8b9.png)

REST-light is a simple microservice to control 433Mhz wireless sockets over HTTP, e.g. on a RaspberryPi. The main usage is an easy integration of 433Mhz wireless sockets in SmartHome Tools like [openHAB](https://openhab.org) or [ioBroker](https://www.iobroker.net).

The project is an API-Wrapper around the famous [443Utils](https://github.com/ninjablocks/433Utils) project.

## How to Use

1. Install Docker on your RaspberryPi
2. Attach a 433Mhz transmitter to [WiringPi Pin 2](https://pinout.xyz/pinout/pin13_gpio27) of your RaspberryPi
3. Run REST-light and receive the generated API-Key from `docker logs` on first startup. 
4. Try your first request! For an example, see section ["curl request example"](#curl-request-example)

#### GPIO access

For the app to be able to use the Pi's GPIO-PINs, they need to be exposed to the container.
There are multiple options to do this, as explained [here](https://stackoverflow.com/a/48234752/8069229).

From the ones available, i had the best experience using the "device-approach" as stated below.

#### docker run

```ShellSession
docker run -it --device /dev/gpiomem -v <your-path>/rest-light:/etc/rest-light -p 4242:4242 uupascal/rest-light:DEV-latest
```

#### docker-compose
```yaml
version: "3.8"

services:
  rest-light:
    container_name: REST-light
    image: "uupascal/rest-light:latest"
    restart: unless-stopped
    volumes:
        - "<your-path>/rest-light:/etc/rest-light"
    devices:
        - /dev/gpiomem
    ports:
        - 4242

```

## curl request example

```ShellSession
curl http://127.0.0.1:4242/send \
    --data-urlencode "api_key=<key from docker logs>" \
    --data-urlencode "system_code=10000" \
    --data-urlencode "unit_code=2" \
    --data-urlencode "state=0" 
```

## Security considerations

Although this project was developed with current security best-practices in mind, it is still built around software
which was not updated for at least 6 years. I would therefor strongly encourage you to only use this container on private & trusted networks and to never expose it to the internet.
As the license implies, this software is provided without warranty of any kind.

## Versioning & docker tags

Use the docker tag `latest` to always get the latest stable image.

The images are also tagged with the current date, so to pin to a static version, you can for example use the tag `2022.01.09`.

Unstable/Development versions are prefixed with `DEV-` and should only be used for testing purposes.

## Contribution

We love your input! For details see [CONTRIBUTING.md](https://github.com/uupascal/REST-light/blob/main/CONTRIBUTING.md)

## Credits

The project relies on [443Utils](https://github.com/ninjablocks/433Utils).
