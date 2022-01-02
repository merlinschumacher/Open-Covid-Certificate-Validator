import json

from cwt import load_pem_hcert_dsc


class CertificateLoader:
    """
    A generic class to dowload certificates from a url and store them
    in a file.

    If a file is already present, it will be loaded instead of downloaded.
    Returns:
        A list of certificates.
    """

    def __init__(self):
        self._certs = []
        self._cert_url = None
        self._cert_filename = None
        self.rules = None

    def __call__(self):
        """
        Return the list of certs if the object is called
        """
        return self._certs

    def _save_certs(self, certs_json):
        """
        Stores the certificates in a file
        """
        with open("./data/" + self._cert_filename, 'w') as f:
            json.dump(certs_json, f)

    def _load_certs(self):
        """
        Load the certificates from the filesystem
        or downloads them if they are not present.
        Returns:
            certs_json: An array DSC certificates.
        """
        try:
            with open("./data/"+self._cert_filename) as f:
                certs_json = json.load(f)
                if not certs_json:
                    certs_json = self._download_certs()
                    self._save_certs(certs_json)
        except Exception as e:
            if (e is FileNotFoundError):
                certs_json = self._download_certs()
                self._save_certs(certs_json)
            else:
                raise e
        return certs_json

    def _download_certs(self):
        """
        Downloads the signed germa certificates from the official servers.
        This method needs to be implemented in every subclass and is
        intentionally empty, as every country has a different way of
        providing certificates.
        It must save the certificates in a file.
        Returns:
            cert_json: A dictionary containing the certificates.
        """
        return None

    def _build_certlist(self):
        """
        Builds the list of certificates from json data.
        This method needs to be implemented in every subclass
        for every country.
        """

        certs_json = self._load_certs()
        for certs in certs_json:
            self._certs.append(load_pem_hcert_dsc(certs))

    def update_certs(self):
        """
        Redownloads the certificates and updates the list stored in RAM.
        """
        print("Updating the certificate lists")
        self._download_certs()
        self._build_certlist()

