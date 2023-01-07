![REST-light Logo](https://user-images.githubusercontent.com/20238923/148686271-14e32a8b-8ad2-4a8d-9be1-1acbff51b8b9.png)

REST-light is a simple microservice to control 433Mhz wireless sockets over HTTP, e.g. on a RaspberryPi. The main usage is an easy integration of 433Mhz wireless sockets in SmartHome Tools like [openHAB](https://openhab.org) or [ioBroker](https://www.iobroker.net).

The project is an API-Wrapper around the famous [443Utils](https://github.com/ninjablocks/433Utils) project.


- [How to Use](#how-to-use)
    + [GPIO access](#gpio-access)
    + [docker run](#docker-run)
    + [docker-compose](#docker-compose)
- [curl request example](#curl-request-example)
- [OpenHAB integration example for the `send` binary](#openhab-integration-example-for-the--send--binary)
- [OpenHAB integration example for the `codesend` binary](#openhab-integration-example-for-the--codesend--binary)
- [Security considerations](#security-considerations)
- [Versioning & docker tags](#versioning---docker-tags)
- [Contribution](#contribution)
- [Credits](#credits)

## How to Use

The setup is very simple. There is nothing to configure, except running the container. 
For the app to be able to persist the API-Key, ensure the mounted volume is writeable for UID/GID 33.

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
docker run -d --device /dev/gpiomem -v <your-path>/rest-light:/etc/rest-light -p 4242:4242 uupascal/rest-light:DEV-latest
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

curl http://127.0.0.1:4242/codesend \
    --data-urlencode "api_key=<key from docker logs>" \
    --data-urlencode "decimalcode=500000" \
    --data-urlencode "protocol=optional" \
    --data-urlencode "pulselength=optional" \
    --data-urlencode "bitlength=optional"
```

## OpenHAB integration example for the `send` binary

In this example, new devices can be added by simply adding a switch to the group `gREST_light`, whichs name is in the format
`example_<SYSTEM_CODE>_<UNIT_CODE>`.

The included rule receives the values from the item name, as soon as any item in the group is triggered.

__RESTlight.items__
```
Group:Switch:OR(OFF, ON)    gREST_light                 "REST-light"    <light>                            ["Location"]

Switch                      RESTLight_10000_1           "Light"         <light>   (mygroup, gREST_light)   ["Switch"]
Switch                      RESTLight_01000_3           "Light2"        <light>   (mygroup, gREST_light)   ["Switch"]
Switch                      RESTLight_00100_3           "Light3"        <light>   (mygroup, gREST_light)   ["Switch"]
```

__RESTlight.rules__
```
rule "REST_light"
  when
    Member of gREST_light received command
  then
    logInfo("REST_light", "Member " + triggeringItem.name + " to " + receivedCommand)

    try {
      // receive system & unit code from item name
      val sys_num = triggeringItem.name.toString.split("_").get(1)
      val unit_num = triggeringItem.name.toString.split("_").get(2)

      var String state = ""
      if(receivedCommand == ON) {
        state = "1"
      } if(receivedCommand == OFF) {
        state = "0"
      }

      var String jsonstring = (
              '{"api_key" : "<INSERT KEY HERE>", "system_code" : "' + 
              sys_num + '", "unit_code" : "' + unit_num + '", "state" : "' + state + '"}'
      )

      sendHttpPostRequest("http://<INSERT IP HERE>:4242/send", "application/json", jsonstring.toString, 5000)
      logInfo("REST_light", jsonstring.toString)
      logInfo("REST_light", "Finished command!")

    } catch(Throwable t) {
      logInfo("REST_light", "Caught exception during attempt to contact REST_light API!")
    }
end

```

## OpenHAB integration example for the `codesend` binary

In this example, new devices can be added by simply adding a switch to the group `gREST_light`, whichs name is in the format
`example_<DECIMALCODE FOR ON>_<DECIMALCODE FOR OFF>`.

The included rule receives the values from the item name, as soon as any item in the group is triggered.

__RESTlight.items__
```
Group:Switch:OR(OFF, ON)    gREST_light                 "REST-light"    <light>                            ["Location"]

Switch                      zap_1234567_2345678_key1    "Light"         <light>   (mygroup, gREST_light)   ["Switch"]
Switch                      zap2_1234567_2345678_key1   "Light2"        <light>   (mygroup, gREST_light)   ["Switch"]
```

__RESTlight.rules__
```
rule "REST_light"
  when
    Member of gREST_light received command
  then
    logInfo("REST_light", "Member " + triggeringItem.name + " to " + receivedCommand)

    try {
      // receive decimal codes from item name, e.g. zap_1234567_2345678_key1
      var decimal_code = ""
      if(receivedCommand == ON) {
        decimal_code = triggeringItem.name.toString.split("_").get(1)
      } if(receivedCommand == OFF) {
        decimal_code = triggeringItem.name.toString.split("_").get(2)
      }
      
      var protocol = "1"
      var pulselength = "150"
        
      var String jsonstring = ('{"api_key" : "<INSERT KEY HERE>", "decimalcode" : "' + decimal_code + '", "protocol" : "' + protocol + '", "pulselength" : "' + pulselength + '"}')
	  
      sendHttpPostRequest("http://<INSERT IP HERE>:4242/codesend", "application/json", jsonstring.toString, 5000)
      logInfo("REST_light", jsonstring.toString)
      logInfo("REST_light", "Finished command!")

    } catch(Throwable t) {
      logInfo("REST_light", "Caught exception during attempt to contact REST_light API!")
    }
end

```

## Security considerations

Although this project was developed with current security best-practices in mind, it is still built around software
which was not updated for at least 6 years. I would therefor strongly encourage you to only use this container on private & trusted networks and to never expose it to the internet.
As the license implies, this software is provided without warranty of any kind.

## Versioning & docker tags

Use the docker tag `latest` to always get the latest stable image.

The images are also tagged with the current timestamp, so to pin to a static version, you can for example use the tag `2022.01.09-1746`.

Unstable/Development versions are prefixed with `DEV-` and should only be used for testing purposes.

## Contribution

We love your input! For details see [CONTRIBUTING.md](https://github.com/uupascal/REST-light/blob/main/CONTRIBUTING.md)

## Credits

The project relies on [443Utils](https://github.com/ninjablocks/433Utils).
