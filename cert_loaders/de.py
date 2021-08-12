import json
from base64 import b64decode

import requests
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.x509 import load_der_x509_certificate
from cwt import COSEKey
from cwt.algs.ec2 import EC2Key
from cwt.const import COSE_KEY_TYPES
from typing import Dict, Any
from .certificate_loader import CertificateLoader


class CertificateLoader_DE(CertificateLoader):
    def __init__(self):
        super().__init__()
        self._cert_url = 'https://de.dscg.ubirch.com/trustList/DSC/'
        self._cert_filename = 'de.json'
        self._build_certlist()
        self._start_update_timer()

    def _uint_to_bytes(self, v: int) -> bytes:
        if v < 0:
            raise ValueError("Not a positive number.")
        rem = v
        length = 0
        while rem != 0:
            rem = rem >> 8
            length += 1
        return v.to_bytes(length, "big")

    def _create_cose_key(self, cert):
        """
        Loads DER-formatted DSC (Digital Signing Certificate) issued by CSCA
        (Certificate Signing Certificate Authority) as a COSEKey. At this time,
        the kid of the COSE key will be generated as a 8-byte truncated SHA256
        fingerprint of the DSC complient with `Electronic Health Certificate
        Specification <https://github.com/ehn-dcc-development/hcert-spec/blob/main/hcert_spec.md>`_.
        Modified from python-cwt to fit the german DSC format.
        Returns:
            COSEKeyInterface: A DSC's public key as a COSE key.
        """

        k = cert.public_key()
        params: Dict[int, Any] = {}
        params[2] = cert.fingerprint(SHA256())[0:8]
        if isinstance(k, RSAPublicKey):
            alg = -37  # "PS256"
            params[1] = COSE_KEY_TYPES["RSA"]
            params[3] = alg
            pub_nums = k.public_numbers()
            params[-1] = self._uint_to_bytes(pub_nums.n)
            params[-2] = self._uint_to_bytes(pub_nums.e)
        elif isinstance(k, EllipticCurvePublicKey):
            alg = -7  # "ES256"
            params[3] = alg
            params.update(EC2Key.to_cose_key(k))
        else:
            raise ValueError(f"Unsupported or unknown key type: {type(k)}.")
        return COSEKey.new(params)

    def _download_certs(self):
        """
        Downloads the signed germa certificates from the official german servers.
        Returns:
            cert_json: A dictionary containing the certificates.
        """
        resp = requests.get(self._cert_url)

        resp.raise_for_status()
        raw_cert = resp.content
        cert_sig_b64, cert_str = raw_cert.split(b'\n', 1)
        cert_json = json.loads(cert_str)
        return cert_json["certificates"]

    def _build_certlist(self):
        """
        Builds the list of certificates from json data and stores it.
        TODO: Validation for the downloaded certificates.
        """
        certs_json = self._load_certs()
        # resp = requests.get(
        #     'https://github.com/Digitaler-Impfnachweis/covpass-ios/raw/main/Certificates/DEMO/CA/pubkey.pem')
        # pubkey_str = resp.content
        # pubkey = load_pem_public_key(pubkey_str)
        for cert in certs_json:
            raw_data = b64decode(cert["rawData"])
            x509 = load_der_x509_certificate(raw_data)
            # sign = b64decode(cert_sig_b64)
            # r = int.from_bytes(sign[:len(sign)//2], byteorder="big", signed=False)
            # s = int.from_bytes(sign[len(sign)//2:], byteorder="big", signed=False)
            # sign = encode_dss_signature(x, y)
            # pubkey.verify(sign, cert_str, ECDSA(hashes.SHA256()))
            self._certs.append(self._create_cose_key(x509))
