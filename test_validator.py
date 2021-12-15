import json
import unittest
from datetime import datetime

import dateutil
from cwt.helpers.hcert import load_pem_hcert_dsc
from freezegun import freeze_time

from cert_loaders.helper import create_chunked_cert
from test_helper import load_fixtures
from validator import DCCValidator


class DCCTests(unittest.TestCase):

    def test_generator(self):
        """
        Generate test cases
        """
        test_countries = ["AE", "BE", "BG", "CH", "CY", "CZ", "DE", "DK", "EE", "ES", "FI", "FR", "GE",  "GB", "GR", "HR", "HU", "IE",
                          "IS", "IT", "LI", "LT", "LU", "LV", "MA", "MT", "NL", "NO", "PL", "PT", "RO", "SE", "SG", "SI", "SK", "SM", "UA", "VA", "common"]
        for test_country in test_countries:
            test_fixtures = load_fixtures(test_country)
            for test_case in test_fixtures:
                test_filename = test_case[0]
                test_data = test_case[1]
                test_description = test_data["TESTCTX"].get(
                    "DESCRIPTION",
                    "DESCRIPTION MISSING")

                try:
                    test_title = test_filename + "\nDESCRIPTION: " + test_description
                except:
                    test_title = test_filename
                with self.subTest(test_title, test_data=test_data):
                    test_time = test_data["TESTCTX"].get("VALIDATIONCLOCK")
                    test_time = dateutil.parser.parse(test_time)
                    with freeze_time(test_time):
                        self.maxDiff = None
                        print("TESTING: " + test_title)
                        print("TESTTIME: " + str(datetime.now()))
                        test_expected_results = test_data.get(
                            "EXPECTEDRESULTS")
                        test_dcc = test_data.get("PREFIX")
                        test_verify = test_expected_results.get(
                            "EXPECTEDVERIFY"
                            )
                        test_decode = test_expected_results.get(
                            "EXPECTEDDECODE"                            )
                        print("Expected to verify: " + str(test_verify))
                        print("Expected to decode: " + str(test_decode))
                        print("Simulated time: " + datetime.now().isoformat())
                        certs = []
                        cert_data = create_chunked_cert(
                            test_data["TESTCTX"]["CERTIFICATE"])
                        certs.append(load_pem_hcert_dsc(cert_data))

                        dcc_validator = DCCValidator(
                            country="XX", certs=certs, dev_mode=False)
                        valid = None
                        content = None
                        hcert = None
                        valid, content = dcc_validator.validate(test_dcc)
                        self.assertIsNotNone(content)
                        if (test_verify is not None):
                            if (test_verify):
                                self.assertTrue(valid)
                            else:
                                self.assertFalse(valid)

                        if (test_decode is not None):
                            if (test_decode):
                                test_json = test_data.get("JSON")
                                hcert = content[-260][1]
                                self.assertEqual(hcert, test_json)

                        print("VALID:   " + str(valid))
                        print("CONTENT: " + json.dumps(content))
                        print("CERT: " + json.dumps(hcert))
                        print("JSON: " + json.dumps(test_json))


if __name__ == '__main__':
    unittest.main()
