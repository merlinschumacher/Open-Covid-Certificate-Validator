# THIS PROJECT HAS BEEN ARCHIVED.

Most of the certificate validation infrastructure of the participating countries has been shut down. So the validation isn't possible anymore, and this project serves no purpose. 

Nevertheless the EU Digital COVID certificate project showed, that countries are able to implement complex digital services that are open and interoperable in a timely fashion - if they're inclined to do so. It would have been nice to see this develop into a new generation of nation- or even EU-wide digital health servies.

# Open Covid Certificate Validator

![Build badge](https://img.shields.io/github/workflow/status/merlinschumacher/Open-Covid-Certificate-Validator/Publish%20Docker%20images%20to%20GitHub%20Package%20Registry?style=for-the-badge)
![Language badge](https://img.shields.io/github/languages/top/merlinschumacher/Open-Covid-Certificate-Validator?style=for-the-badge)
![License badge](https://img.shields.io/github/license/merlinschumacher/Open-Covid-Certificate-Validator?style=for-the-badge)
![Star count badge](https://img.shields.io/github/stars/merlinschumacher/Open-Covid-Certificate-Validator?style=for-the-badge)

This an open source API to validate [EU Digital COVID Certificates](https://ec.europa.eu/info/live-work-travel-eu/coronavirus-response/safe-covid-19-vaccines-europeans/eu-digital-covid-certificate_en). It receives a COVID certificate and validates it using a list of signing certificates provided by an EU member state.

The server provides a simple JSON-API that returns validation result and the data stored inside a certificate. There is also a simple web frontend to test the service.

There is a basic demo available at

[https://covid.merlinschumacher.de/](https://covid.merlinschumacher.de/)

The demo neither logs IP addresses nor stores any COVID certificate data.

## **NOTICE: THIS IS NOT AN OFFICIAL VALIDATOR! IT COMES WITHOUT ANY WARRANTIES!**

## Getting started

The easiest way to run OCCV is to use a container. An up to date docker image is provided via GitHubs Container Image Registry under `ghcr.io/merlinschumacher/open-covid-certificate-validator:main`.

To start the container you need a recent version of Docker and `docker-compose`. Just execute `docker-compose up` and the server will answer on port 8000 of your server. Modify the compose file to fit your needs. Currently only validation against the [German list of certificates](https://github.com/Digitaler-Impfnachweis/certification-apis) provided by Ubirch and the [Austrian list of certificates](https://github.com/Federal-Ministry-of-Health-AT/green-pass-overview#details-on-trust-listsbusiness-rulesvalue-sets) is supported. But this should be able to validate all certificates issued in the EU. The certificates are updated every 24 hours.

To start the container just with `docker` run:

```
docker run -p 8000:8000 -e CERT_COUNTRY=DE ghcr.io/merlinschumacher/open-covid-certificate-validator:main
```


If you want to start the service manually, you need to set up a virtual envinroment and install the package requirements. Then set the environment variable `CERT_COUNTRY`to either `DE` or `AT` and run `python main.py`. After the service starts it should run on `http://localhost:8000`.

To access the API send a POST request containing the following JSON to `/`:

```json
    {"dcc": "HC1:XXXX..."}
```

Replace the payload with the data of the COVID certificate. The server will then return the following answer, if the certificate is valid:

```json
{
  "valid": true,
  "dccdata": {
    "1": "AT",
    "4": 1635876000,
    "6": 1620324000,
    "-260": {
      "1": {
        "v": [
          {
            "dn": 1,
            "ma": "ORG-100030215",
            "vp": "1119349007",
            "dt": "2021-02-18",
            "co": "AT",
            "ci": "URN:UVCI:01:AT:10807843F94AEE0EE5093FBC254BD813#B",
            "mp": "EU/1/20/1528",
            "is": "Ministry of Health, Austria",
            "sd": 2,
            "tg": "840539006"
          }
        ],
        "nam": {
          "fnt": "MUSTERFRAU<GOESSINGER",
          "fn": "Musterfrau-Gößinger",
          "gnt": "GABRIELE",
          "gn": "Gabriele"
        },
        "ver": "1.0.0",
        "dob": "1998-02-26"
      }
    }
  }
}
```

If it's invalid, the server will simply return

```json
{
    "valid":false, 
    "ddcdata":{}
}
```

The `ddcdata` field contains all the data encoded in the certificate according to the [specification by the EU](https://ec.europa.eu/health/sites/default/files/ehealth/docs/covid-certificate_json_specification_en.pdf)

## Validation rules

The service returns a list of so called [business rules](https://github.com/eu-digital-green-certificates/dgc-business-rules-testdata) on the endpoint `/business_rules`. To check if the validated certificate is currently valid in a given context you must evaluate those rules. The rules are a variant of JsonLogic called CertLogic.

## Contributing

Everyone is invited to contribute to the service and provide pull-requests, ideas and feedback.

Foremost the service needs testing with certificates from all issuing countries and also the implementation of all available validation lists from the EU members. You can contribute with testing your certificate and reporting your success or possible errors.

## Privacy

While the data encoded in the certificate are sent to the server, they are never stored. They will be processed to generate a response and are deleted afterwards. There is no logging of indidivual data of any kind.

## The web service

This container provides a simple web service to test and validate certificates. It uses your webcam or phone camera to scan a QR code for a certificate and sends it to the API.

![An example of a scanned and validated COVID Certificate](demo.jpg)

## Technology

The API service is written in Python and uses [FastAPI](https://github.com/tiangolo/fastapi) to provide the JSON API. The validation is handled by  [python-cwt](https://github.com/dajiaji/python-cwt), a CBOR Web Token library.

The web interface is still very rudimentary and build in Typescript using [jsQR](https://github.com/cozmo/jsQR) to decode the QR codes.
