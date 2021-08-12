from cwt import load_pem_hcert_dsc

from .certificate_loader import CertificateLoader


class CertificateLoader_XX(CertificateLoader):
    """
    A generic class to dowload certificates from a url and store them in a file.
    If a file is already present, it will be loaded instead of downloaded.
    Returns:
        A list of certificates.
    """

    def __init__(self):
        self._certs = []
        self._build_certlist()
        pass

    def _build_certlist(self):
        """
        Builds the list of certificates from json data.
        This method needs to be implemented in every subclass for every country.
        """

        # A DSC(Document Signing Certificate) issued by a CSCA
        # (Certificate Signing Certificate Authority) quoted from:
        # https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/AT/2DCode/raw/1.json
        dsc = "-----BEGIN CERTIFICATE-----\nMIIBvTCCAWOgAwIBAgIKAXk8i88OleLsuTAKBggqhkjOPQQDAjA2MRYwFAYDVQQDDA1BVCBER0MgQ1NDQSAxMQswCQYDVQQGEwJBVDEPMA0GA1UECgwGQk1TR1BLMB4XDTIxMDUwNTEyNDEwNloXDTIzMDUwNTEyNDEwNlowPTERMA8GA1UEAwwIQVQgRFNDIDExCzAJBgNVBAYTAkFUMQ8wDQYDVQQKDAZCTVNHUEsxCjAIBgNVBAUTATEwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAASt1Vz1rRuW1HqObUE9MDe7RzIk1gq4XW5GTyHuHTj5cFEn2Rge37+hINfCZZcozpwQKdyaporPUP1TE7UWl0F3o1IwUDAOBgNVHQ8BAf8EBAMCB4AwHQYDVR0OBBYEFO49y1ISb6cvXshLcp8UUp9VoGLQMB8GA1UdIwQYMBaAFP7JKEOflGEvef2iMdtopsetwGGeMAoGCCqGSM49BAMCA0gAMEUCIQDG2opotWG8tJXN84ZZqT6wUBz9KF8D+z9NukYvnUEQ3QIgdBLFSTSiDt0UJaDF6St2bkUQuVHW6fQbONd731/M4nc=\n-----END CERTIFICATE-----"
        self._certs.append(load_pem_hcert_dsc(dsc))
