import json
import unittest
from cert_loaders.helper import create_cose_key

from validator import DCCValidator
from test_helper import load_fixtures, create_certdata_from_str
from cryptography.x509 import load_pem_x509_certificate


global DEV_MODE
DEV_MODE = True


class DCCTests(unittest.TestCase):

    def test_generator_de(self):
        """
        Generate test cases for DE
        """
        test_country = "DE"
        print("TESTING: " + test_country)
        test_fixtures = load_fixtures(test_country)
        for test_case in test_fixtures:
            with self.subTest(test_case=test_case):
                test_description = test_case["TESTCTX"]["DESCRIPTION"]
                print(test_description)
                test_dcc = test_case["PREFIX"]
                test_json = test_case["JSON"]
                test_verify = test_case["EXPECTEDRESULTS"]["EXPECTEDVERIFY"]
                test_cert_data = create_certdata_from_str(
                    test_case["TESTCTX"]["CERTIFICATE"])
                certs = []
                x509 = load_pem_x509_certificate(test_cert_data)
                certs.append(create_cose_key(x509))

                dcc_validator = DCCValidator("XX", certs)
                valid, content = dcc_validator.validate(test_dcc)

                self.assertIsNotNone(content)
                try:
                    cert_data = content[-260][1]
                except Exception as e:
                    assert False, "Could not find the certificate data."

                if (test_verify):
                    self.assertIsNotNone(content)
                    self.assertTrue(valid)
                else:
                    self.assertIsNone(content)
                    self.assertFalse(valid)
                print("VALID:   " + str(valid))
                print("CONTENT: " + json.dumps(cert_data))
                self.assertEqual(cert_data, test_json)

    def test_generator_at(self):
        """
        Generate test cases for AT
        """
        test_country = "AT"
        print("TESTING: " + test_country)
        test_fixtures = load_fixtures(test_country)
        for test_case in test_fixtures:
            with self.subTest(test_case=test_case):
                test_description = test_case["TESTCTX"]["DESCRIPTION"]
                print(test_description)
                test_dcc = test_case["PREFIX"]
                test_json = test_case["JSON"]
                test_verify = test_case["EXPECTEDRESULTS"]["EXPECTEDVERIFY"]
                test_cert_data = create_certdata_from_str(
                    test_case["TESTCTX"]["CERTIFICATE"])
                certs = []
                x509 = load_pem_x509_certificate(test_cert_data)
                certs.append(create_cose_key(x509))

                dcc_validator = DCCValidator("XX", certs)
                valid, content = dcc_validator.validate(test_dcc)

                self.assertIsNotNone(content)
                try:
                    cert_data = content[-260][1]
                except Exception as e:
                    assert False, "Could not find the certificate data."

                if (test_verify):
                    self.assertIsNotNone(content)
                    self.assertTrue(valid)
                else:
                    self.assertIsNone(content)
                    self.assertFalse(valid)
                print("VALID:   " + str(valid))
                print("CONTENT: " + json.dumps(cert_data))
                self.assertEqual(cert_data, test_json)

    def test_generator_common(self):
        """
        Generate test cases for COMMON
        """
        test_country = "common"
        test_fixtures = load_fixtures(test_country)
        print("TESTING: " + test_country)
        for test_case in test_fixtures:
            with self.subTest(test_case=test_case):
                test_description = test_case["TESTCTX"]["DESCRIPTION"]
                print(test_description)
                test_dcc = test_case["PREFIX"]
                test_json = test_case["JSON"]
                test_verify = test_case["EXPECTEDRESULTS"]["EXPECTEDVERIFY"]
                test_cert_data = create_certdata_from_str(
                    test_case["TESTCTX"]["CERTIFICATE"])
                certs = []
                x509 = load_pem_x509_certificate(test_cert_data)
                certs.append(create_cose_key(x509))

                dcc_validator = DCCValidator("XX", certs)
                valid, content = dcc_validator.validate(test_dcc)

                self.assertIsNotNone(content)
                try:
                    cert_data = content[-260][1]
                except Exception as e:
                    assert False, "Could not find the certificate data."

                if (test_verify):
                    self.assertIsNotNone(content)
                    self.assertTrue(valid)
                else:
                    self.assertIsNone(content)
                    self.assertFalse(valid)
                print("VALID:   " + str(valid))
                print("CONTENT: " + json.dumps(cert_data))
                self.assertEqual(cert_data, test_json)


if __name__ == '__main__':
    unittest.main()
