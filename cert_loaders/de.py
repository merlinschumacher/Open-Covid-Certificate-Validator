import json
from base64 import b64decode

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
from cryptography.hazmat.primitives.asymmetric.utils import \
    encode_dss_signature
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cwt.helpers.hcert import load_pem_hcert_dsc

from cert_loaders.helper import create_chunked_cert

from .certificate_loader import CertificateLoader


class CertificateLoader_DE(CertificateLoader):
    def __init__(self):
        super().__init__()
        self._cert_url = 'https://de.dscg.ubirch.com/trustList/DSC/'
        self._cert_filename = 'de.json'
        self._cert_sign_key = 'https://github.com/Digitaler-Impfnachweis/covpass-ios/raw/main/Certificates/PROD_RKI/CA/pubkey.pem'
        self._build_certlist()

    def _read_certs_from_file(self):
        """
        Try to read the certificates and the signature from a file.
        Returns:
            certs_json: An JSON with certificates.
            signature: A signature of the json data.
        Fails:
            None, None: if any of the files are not found.
        """

        try:
            with open("./data/"+self._cert_filename, "rb") as f:
                certs_str = f.read()
        except FileNotFoundError:
            return None, None

        # Load the saved certificate signature from the filesystem
        try:
            with open("./data/"+self._cert_filename+".sig", "rb") as s:
                signature = bytes(s.read())
        except FileNotFoundError:
            return None, None

        return certs_str, signature

    def _save_certs(self, certs_str, signature):
        """
        Stores the certificates and the signature in a file
        """
        with open("./data/" + self._cert_filename, 'wb') as f:
            f.write(certs_str)
        with open("./data/" + self._cert_filename+".sig", 'wb') as s:
            s.write(signature)

    def _load_certs(self):
        """
        Load the certificates from the filesystem
        or downloads them if they are not present.
        Returns:
            certs_json: An array DSC certificates.
        Fails:
            None: If the certificates cannot be loaded.
        """
        signature = ""
        certs_str = {}
        failed = False

        # Load the saved certificates from the filesystem
        certs_str, signature = self._read_certs_from_file()

        if certs_str is None or signature is None:
            failed = True

        # Validate the signature of the certificate
        if not failed and not self._validate_json(certs_str, signature):
            return None

        # Re-download the certificates if they are not present
        # or can't be verified
        if failed:
            certs_str = self._download_certs()
        return certs_str

    def _validate_json(self, certs_str, signature):
        """
        Validates the json data against the signature with the
        iOS Corona Warn App key stored on GitHub.
        Returns:
            True if the signature is valid
        Raises:
            InvalidSignature: If the signature is invalid.
        """
        resp = requests.get(self._cert_sign_key)
        resp.raise_for_status()
        pubkey_str = resp.content
        pubkey = load_pem_public_key(pubkey_str)
        x = int.from_bytes(
            signature[:len(signature)//2], byteorder="big", signed=False)
        y = int.from_bytes(
            signature[len(signature)//2:], byteorder="big", signed=False)
        signature = encode_dss_signature(x, y)
        try:
            pubkey.verify(signature,
                          certs_str, ECDSA(hashes.SHA256()))
        except InvalidSignature:
            raise InvalidSignature(
                "Could not validate the signature of the DE certificates!")
        return True

    def _download_certs(self):
        """
        Downloads the signed germa certificates from the official
        german servers.

        Returns:
            cert_json: A dictionary containing the certificates.
        """
        resp = requests.get(self._cert_url)
        resp.raise_for_status()

        raw_cert = resp.content
        signature_b64, certs_str = raw_cert.split(b'\n', 1)
        signature = b64decode(signature_b64)
        if self._validate_json(certs_str, signature):
            self._save_certs(certs_str, signature)
            return certs_str
        else:
            raise ValueError("Could not validate the german certificate list.")
            return None

    def _build_certlist(self):
        """
        Builds the list of certificates from json data and stores it.
        """
        certs_str = self._load_certs()
        if certs_str is None:
            raise ValueError("Could not load the certificates.")

        certs_json = json.loads(certs_str)
        certs_json = certs_json["certificates"]

        for cert in certs_json:
            cert_data = create_chunked_cert(cert["rawData"])
            self._certs.append(load_pem_hcert_dsc(cert_data))
