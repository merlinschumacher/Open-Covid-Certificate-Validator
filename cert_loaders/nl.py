import json
import logging
from base64 import b64decode
from typing import Any, Dict

import requests
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl.backend import \
    backend
from cryptography.hazmat.bindings._openssl import ffi, lib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA, EllipticCurvePublicKey)
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.utils import \
    encode_dss_signature
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.x509 import load_der_x509_certificate, load_pem_x509_certificate
from cwt import COSEKey
from cwt.algs.ec2 import EC2Key
from cwt.const import COSE_KEY_TYPES
from asn1crypto import cms

from .certificate_loader import CertificateLoader


def __ascii_armor(payload: str, header: str) -> str:
    """Add ascii armour for the specified header type to an ascii payload
    Will not add if the correct header is already present
    Will remove any trailing newlines
    """
    try:
        begin = "-----BEGIN {}-----".format(header)
        end = "-----END {}-----".format(header)

        lines = payload.split("\n")

        # Remove blank training lines
        while lines[-1] == "":
            lines.pop()

        # Add armour if missing
        if not lines[0] == begin:
            lines.insert(0, begin)
            lines.append(end)

        return "\n".join(lines)
    except IndexError:
        raise IndexError(f"Unable to ascii armor {header}") from None


def verify_signature(certs, signature: str, root_cert: str) -> bool:
    """Verify a detached signature
    Parameters
    ----------
    document : str
        The document to be verified
    signature : str
        The signature to verify. The signature may inculde the PKCS7 ascii armor
    certificate : str
        The certificate of the signer. The certificate must include the CERTIFICATE ascii armor
    """

    asn1_struct = cms.ContentInfo.load(signature)
    asn1_content = asn1_struct['content']['certificates']
    cert_list = []

    for cert in asn1_content:
        cert_list.append(cert.parse())

    print(cert_list)

    # chang

    # cert_list = None
    # certs = json.loads(certs)
    # for cert in certs:
    #     print(cert)

    # try:
    # pkcs7 = __ascii_armor(signature, "PKCS7")
    # pkcs7 = signature
    # logger.debug(pkcs7)

    # # Load the string into a bio
    # bio = backend._bytes_to_bio(pkcs7)  # pylint: disable=W0212

    # # Create the pkcs7 object
    # pkcs7_object = lib.PEM_read_bio_PKCS7(
    #     bio.bio, ffi.NULL, ffi.NULL, ffi.NULL)

    # # Load the specified certificate
    # # certificate = __ascii_armor(certificate, 'CERTIFICATE')
    # other_cert = backend.load_der_x509_certificate(certificate)
    # stack = lib.sk_X509_new_null()
    # lib.sk_X509_push(stack, other_cert._x509)  # pylint: disable=W0212

    # # We need a CA store, even though we don't use it
    # store = lib.X509_STORE_new()

    # # Load the document into a bio
    # content = backend._bytes_to_bio(
    #     root_cert)  # pylint: disable=W0212

    # # Flags
    # flags = lib.PKCS7_NOVERIFY

    # # https://www.openssl.org/docs/man1.0.2/crypto/PKCS7_verify.html
    # if lib.PKCS7_verify(pkcs7_object, stack, store, content.bio, ffi.NULL, flags) == 1:
    #     return True
    # # except Exception as error:
    # #     logger.error("verify_detached_signature exception=%s", str(error))
    # #     return False
    # return False


class CertificateLoader_NL(CertificateLoader):
    def __init__(self):
        super().__init__()
        self._cert_url = 'https://verifier-api.coronacheck.nl/v4/verifier/public_keys'
        self._cert_filename = 'nl.json'
        self._root_cert_url = 'http://cert.pkioverheid.nl/EVRootCA.cer'
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

    def _validate_json(self, certs_data, signature, root_cert):
        """
        Validates the json data against the signature with the
        iOS Corona Warn App key stored on GitHub.
        Returns:
            True if the signature is valid
        Raises:
            InvalidSignature: If the signature is invalid.
        """
        # try:
        #     # verify_pkcs7_detached_signature(certs_data, signature, root_cert)
        # except InvalidSignature:
        #     raise InvalidSignature(
        #         "Could not validate the signature of the NL certificates!")
        return True

    def _download_root_cert(self):
        """
        Downloads the root certificate from the NL server.

        """
        resp = requests.get(self._cert_url)
        resp.raise_for_status()
        return resp.content

    def _download_certs(self):
        """
        Downloads the signed NL certificates from the official
        german servers.

        Returns:
            cert_json: A dictionary containing the certificates.
        """
        resp = requests.get(self._cert_url)
        resp.raise_for_status()

        certs_data = json.loads(resp.content)
        signature = b64decode(certs_data["signature"])
        certs_data = b64decode(certs_data["payload"])

        resp = requests.get(self._root_cert_url)
        resp.raise_for_status()
        verify_signature(certs_data, signature, resp.content)
        try:
            verify_signature(certs_data, signature, resp.content)
            root_cert = load_der_x509_certificate(resp.content)
        except Exception as error:
            print('Could not download NL root certificate')

        # if self._validate_json(certs_data, signature, root_cert):
        #     self._save_certs(certs_data, signature)
        #     return certs_data
        # else:
        #     raise ValueError("Could not validate the NL certificate list.")
        #     return None

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

            raw_data = b64decode(cert["rawData"])
            x509 = load_der_x509_certificate(raw_data)
            self._certs.append(self._create_cose_key(x509))
