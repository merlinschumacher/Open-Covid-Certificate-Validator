import os
import zlib
from typing import Callable, Dict

import cwt
from base45 import b45decode
from cwt import Claims
from cwt import cbor_processor
import cbor2

from cert_loaders.de import CertificateLoader_DE
from cert_loaders.at import CertificateLoader_AT
from cert_loaders.at_test import CertificateLoader_AT_TEST
from cert_loaders.test import CertificateLoader_XX


class DCCValidator():

    def __init__(self, country, certs=None, dev_mode=False):
        self.CERT_LOADERS: Dict[str, Callable[[], None]] = {
            'DE': CertificateLoader_DE,
            'AT': CertificateLoader_AT,
            'AT_TEST': CertificateLoader_AT_TEST,
            'XX': CertificateLoader_XX
        }
        self.DEV_MODE = dev_mode
        # initiates the certificate loader if no certificate is passed to the object
        # passing the certs to the object will not initiate the certificate loader
        # this is useful for testing
        if certs is None:
            self._cert_loader = self._get_cert_loader(country)()
        # loads the certificates from the loader instance
            self._certs = self._cert_loader()
        else:
            self._certs = certs

        print("Loaded %i certificates from %s certificate service." %
              (len(self._certs), country))

    def validate(self, dcc):
        dcc = self._decode(dcc)
        if dcc is None:
            return [False, None]

        try:
            decoded = cwt.decode(dcc, keys=self._certs)
            claims = Claims.new(decoded)
            return [True, claims.to_dict()]
        except Exception as e:
            try:
                decoded_noverify = cbor2.loads(dcc)
                decoded_noverify = cbor2.loads(decoded_noverify.value[2])
                print("Could not validate certificate.")
            except Exception as e:
                print("Could not decode certificate.")
                return [False, {}]

            return [False, decoded_noverify]

    def _decode(self, dcc):
        dcc = dcc.encode()
        if dcc.startswith(b'HC1:'):
            dcc = dcc[4:]
        try:
            dcc = b45decode(dcc)
        except Exception as e:
            if self.DEV_MODE:
                print(e)
            if (e is ValueError):
                return None

        if dcc.startswith(b'x'):
            try:
                dcc = zlib.decompress(dcc)
            except Exception as e:
                if self.DEV_MODE:
                    print(e)
                return None

        return dcc

    def _get_cert_loader(self, country):
        return self.CERT_LOADERS[country]

    def get_business_rules(self):
        return self._cert_loader.rules

    def get_status(self):
        return "{status]"


def main(dev_mode=False):

    # Retrieve the requrested country for the certificates
    # from env or fall back to DE
    CERT_COUNTRY = os.getenv("CERT_COUNTRY", "AT")
    # Retrieve DCC from env or fall back on empty string
    DCC = os.getenv("DCC", "")

    # Initiate the DSCValidator
    validator = DCCValidator(country=CERT_COUNTRY, dev_mode=dev_mode)
    # Validate the DCC
    print(validator.validate(DCC))


if __name__ == '__main__':
    main(True)
