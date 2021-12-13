from datetime import datetime
import json
import unittest
import dateutil
from cert_loaders.helper import create_cose_key

from validator import DCCValidator
from test_helper import load_fixtures, create_certdata_from_str
from cryptography.x509 import load_pem_x509_certificate
from freezegun import freeze_time


class DCCTests(unittest.TestCase):

    def test_generator(self):
        """
        Generate test cases
        """
        test_countries = ["AE", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "FI",
                          "GB", "GR", "HR", "IE", "IT", "LU", "LV", "MT", "NL",
                          "PL", "PT", "RO", "SI", "SK", "SM", "common"]
        for test_country in test_countries:
            test_fixtures = load_fixtures(test_country)
            for test_case in test_fixtures:
                print("TESTING: " + test_country)
                test_description = test_case["TESTCTX"].get(
                    "DESCRIPTION",
                    "DESCRIPTION MISSING")
                test_time = test_case["TESTCTX"].get("VALIDATIONCLOCK")
                test_time = dateutil.parser.parse(test_time)

                test_expected_results = test_case.get("EXPECTEDRESULTS")
                test_title = test_country + ": " + test_description
                with self.subTest(test_title, test_case=test_case):
                    with freeze_time(test_time):
                        self.maxDiff = None
                        test_dcc = test_case.get("PREFIX")
                        test_verify = test_expected_results.get(
                            "EXPECTEDVERIFY",
                            False)
                        print("Expected to verify: " + str(test_verify))
                        print("Simulated time: " + datetime.now().isoformat())
                        if (not test_verify):
                            continue
                        test_cert_data = create_certdata_from_str(
                            test_case["TESTCTX"]["CERTIFICATE"])
                        certs = []
                        x509 = load_pem_x509_certificate(test_cert_data)
                        certs.append(create_cose_key(x509))

                        dcc_validator = DCCValidator(
                            country="XX", certs=certs, dev_mode=False)
                        valid = False
                        content = None
                        cert_data = None
                        valid, content = dcc_validator.validate(test_dcc)
                        self.assertIsNotNone(content)

                        if (test_verify):
                            self.assertTrue(valid)
                            test_json = test_case.get("JSON")
                            cert_data = content[-260][1]
                            self.assertEqual(cert_data, test_json)
                        else:
                            self.assertFalse(valid)

                        print("VALID:   " + str(valid))
                        print("CONTENT: " + json.dumps(content))
                        print("CERT: " + json.dumps(cert_data))
                        print("JSON: " + json.dumps(test_json))


if __name__ == '__main__':
    unittest.main()
