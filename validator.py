import os
import zlib
from typing import Callable, Dict

import cwt
from base45 import b45decode
from cwt import COSE, Claims

from cert_loaders.de import CertificateLoader_DE
from cert_loaders.nl import CertificateLoader_NL
from cert_loaders.test import CertificateLoader_XX


class DCCValidator():

    def __init__(self, country):
        self.CERT_LOADERS: Dict[str, Callable[[], None]] = {
            'DE': CertificateLoader_DE,
            'NL': CertificateLoader_NL,
            'XX': CertificateLoader_XX
        }
        # initiates the certificate loader
        cert_loader = self._get_cert_loader(country)()
        # loads the certificates from the loader instance
        self._certs = cert_loader()
        self._cose = COSE(
            kid_auto_inclusion=True, alg_auto_inclusion=True, verify_kid=False
        )

    def validate(self, dcc):

        dcc = self._decode(dcc)
        if dcc is None:
            return [False, None]

        try:
            decoded = cwt.decode(dcc, self._certs)
            claims = Claims.new(decoded)
            return [True, claims.to_dict()]
        except Exception as error:
            print("Could not validate certificate.")
            return [False,  {}]

    def _decode(self, dcc):
        if dcc.startswith("HC1:"):
            dcc = dcc[4:]
        try:
            dcc = b45decode(dcc)
        except ValueError:
            return None

        if dcc.startswith(b'x'):
            dcc = zlib.decompress(dcc)
        return dcc

    def _get_cert_loader(self, country):
        return self.CERT_LOADERS[country]


def main():

    # Retrieve the requrested country for the certificates
    # from env or fall back to DE
    CERT_COUNTRY = os.getenv("CERT_COUNTRY", "DE")
    # Retrieve DCC from env or fall back on empty string
    DCC = os.getenv("DCC", "")

    # Initiate the DSCValidator
    validator = DCCValidator(CERT_COUNTRY)
    # Validate the DCC
    print(validator.validate(DCC))


if __name__ == '__main__':
    main()
