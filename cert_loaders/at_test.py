from typing import Any, Dict

import cbor2
import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.x509 import load_der_x509_certificate
from cwt import COSE, load_pem_hcert_dsc
from .helper import create_cose_key

from .certificate_loader import CertificateLoader

## This is the AT Test Certificate
root_certificate = """-----BEGIN CERTIFICATE-----
MIIB6zCCAZGgAwIBAgIKAXmEuohlRbR2qzAKBggqhkjOPQQDAjBQMQswCQYDVQQG
EwJBVDEPMA0GA1UECgwGQk1TR1BLMQowCAYDVQQLDAFRMQwwCgYDVQQFEwMwMDEx
FjAUBgNVBAMMDUFUIERHQyBDU0NBIDEwHhcNMjEwNTE5MTMwNDQ3WhcNMjIwNjE5
MTMwNDQ3WjBRMQswCQYDVQQGEwJBVDEPMA0GA1UECgwGQk1TR1BLMQowCAYDVQQL
DAFRMQ8wDQYDVQQFEwYwMDEwMDExFDASBgNVBAMMC0FUIERHQyBUTCAxMFkwEwYH
KoZIzj0CAQYIKoZIzj0DAQcDQgAE29KpT1eIKsy5Jx3J0xpPLW+fEBF7ma9943/j
4Z+o1TytLVok9cWjsdasWCS/zcRyAh7HBL+oyMWdFBOWENCQ76NSMFAwDgYDVR0P
AQH/BAQDAgeAMB0GA1UdDgQWBBQYmsL5sXTdMCyW4UtP5BMxq+UAVzAfBgNVHSME
GDAWgBR2sKi2xkUpGC1Cr5ehwL0hniIsJzAKBggqhkjOPQQDAgNIADBFAiBse17k
F5F43q9mRGettRDLprASrxsDO9XxUUp3ObjcWQIhALfUWnserGEPiD7Pa25tg9lj
wkrqDrMdZHZ39qb+Jf/E
-----END CERTIFICATE-----"""


class CertificateLoader_AT_TEST(CertificateLoader):
    def __init__(self):
        super().__init__()
        self._cert_url = 'https://dgc-trusttest.qr.gv.at/trustlist'
        self._cert_filename = 'at_test_trustlist'
        self._signature_url = 'https://dgc-trusttest.qr.gv.at/trustlistsig'
        self._business_rules_url = 'https://dgc-trusttest.qr.gv.at/rules'
        self._business_rules_filename = 'at_test_rules'
        self._business_rules_sig = 'https://dgc-trusttest.qr.gv.at/rulessig'
        self._build_certlist()
        self._load_rules()
        self._start_update_timer()

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
                certs = f.read()
        except FileNotFoundError:
            return None, None

        # Load the saved certificate signature from the filesystem
        try:
            with open("./data/"+self._cert_filename+".sig", "rb") as s:
                signature = bytes(s.read())
        except FileNotFoundError:
            return None, None

        return certs, signature

    def _read_rules_from_file(self):
        """
        Try to read the certificates and the signature from a file.
        Returns:
            certs_json: An JSON with certificates.
            signature: A signature of the json data.
        Fails:
            None, None: if any of the files are not found.
        """

        try:
            with open("./data/"+self._business_rules_filename, "rb") as f:
                rules = f.read()
        except FileNotFoundError:
            return None, None

        # Load the saved certificate signature from the filesystem
        try:
            with open("./data/"+self._business_rules_filename+".sig", "rb") as s:
                signature = bytes(s.read())
        except FileNotFoundError:
            return None, None

        return rules, signature

    def _save_certs(self, certs_str, signature):
        """
        Stores the certificates and the signature in a file
        """
        with open("./data/" + self._cert_filename, 'wb') as f:
            f.write(certs_str)
        with open("./data/" + self._cert_filename+".sig", 'wb') as s:
            s.write(signature)

    def _save_rules(self, rules_str, signature):
        """
        Stores the certificates and the signature in a file
        """
        with open("./data/" + self._business_rules_filename, 'wb') as f:
            f.write(rules_str)
        with open("./data/" + self._business_rules_filename+".sig", 'wb') as s:
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
        certs = {}
        failed = False

        # Load the saved certificates from the filesystem
        certs, signature = self._read_certs_from_file()

        if certs is None or signature is None:
            failed = True

        # Validate the signature of the certificate
        if not failed and not self._validate_certs(certs, signature):
            failed = True

        # Re-download the certificates if they are not present
        # or can't be verified
        if failed:
            certs = self._download_certs()
        return certs

    def _load_rules(self):
        """
        Load the rules from the filesystem
        or downloads them if they are not present.
        Returns:
            rules_json: An array DSC certificates.
        Fails:
            None: If the certificates cannot be loaded.
        """
        signature = ""
        rules = {}
        failed = False

        # Load the saved certificates from the filesystem
        rules, signature = self._read_rules_from_file()

        if rules is None or signature is None:
            failed = True

        # Validate the signature of the certificate
        if not failed and not self._validate_rules(rules, signature):
            failed = True

        # Re-download the certificates if they are not present
        # or can't be verified
        if failed:
            rules = self._download_rules()
        rules = cbor2.loads(rules)
        self.rules = rules

    def _validate_certs(self, certs, signature):
        """
        Validates the json data against the signature
        Returns:
            True if the signature is valid
        Raises:
            InvalidSignature: If the signature is invalid.
        """
        hash_digest = hashes.Hash(hashes.SHA256())
        hash_digest.update(certs)
        hash_digest = hash_digest.finalize()
        try:
            ctx = COSE.new()
            cosekey = load_pem_hcert_dsc(root_certificate)
            signature_decoded = ctx.decode(signature, cosekey)
            cert_sigature = cbor2.loads(signature_decoded)[2]

            if cert_sigature != hash_digest:
                raise InvalidSignature("The certificate signature is invalid.")

        except InvalidSignature:
            raise InvalidSignature(
                "Could not validate the signature of the AT certificates!")
        return True

    def _validate_rules(self, rules, signature):
        """
        Validates the json data against the signature
        Returns:
            True if the signature is valid
        Raises:
            InvalidSignature: If the signature is invalid.
        """
        hash_digest = hashes.Hash(hashes.SHA256())
        hash_digest.update(rules)
        hash_digest = hash_digest.finalize()
        try:
            ctx = COSE.new()
            cosekey = load_pem_hcert_dsc(root_certificate)
            signature_decoded = ctx.decode(signature, cosekey)
            cert_sigature = cbor2.loads(signature_decoded)[2]

            if cert_sigature != hash_digest:
                raise InvalidSignature("The rules signature is invalid.")

        except InvalidSignature:
            raise InvalidSignature(
                "Could not validate the signature of the AT rules!")
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
        certs = resp.content

        resp = requests.get(self._signature_url)
        resp.raise_for_status()
        signature = resp.content

        if self._validate_certs(certs, signature):
            self._save_certs(certs, signature)
            return certs
        else:
            raise ValueError(
                "Could not validate the Austrian certificate list.")
            return None

    def _download_rules(self):
        """
        Downloads the signed germa certificates from the official
        german servers.

        Returns:
            cert_json: A dictionary containing the certificates.
        """
        resp = requests.get(self._business_rules_url)
        resp.raise_for_status()
        rules = resp.content

        resp = requests.get(self._business_rules_sig)
        resp.raise_for_status()
        signature = resp.content

        if self._validate_rules(rules, signature):
            self._save_rules(rules, signature)
            return rules
        else:
            raise ValueError(
                "Could not validate the Austrian certificate list.")
            return None

    def _build_certlist(self):
        """
        Builds the list of certificates from json data and stores it.
        """
        certs_str = self._load_certs()
        if certs_str is None:
            raise ValueError("Could not load the certificates.")

        certs_cbor = cbor2.loads(certs_str)

        for cert in certs_cbor['c']:
            x509 = load_der_x509_certificate(cert['c'])
            self._certs.append(create_cose_key(x509))
