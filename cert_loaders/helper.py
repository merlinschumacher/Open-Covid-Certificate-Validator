from typing import Any, Dict

from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.hashes import SHA256
from cwt import COSEKey
from cwt.algs.ec2 import EC2Key
from cwt.const import COSE_KEY_TYPES


def uint_to_bytes(v: int) -> bytes:
    if v < 0:
        raise ValueError("Not a positive number.")
    rem = v
    length = 0
    while rem != 0:
        rem = rem >> 8
        length += 1
    return v.to_bytes(length, "big")


def create_cose_key(cert):
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
        params[-1] = uint_to_bytes(pub_nums.n)
        params[-2] = uint_to_bytes(pub_nums.e)
    elif isinstance(k, EllipticCurvePublicKey):
        alg = -7  # "ES256"
        params[3] = alg
        params.update(EC2Key.to_cose_key(k))
    else:
        raise ValueError(f"Unsupported or unknown key type: {type(k)}.")
    return COSEKey.new(params)
