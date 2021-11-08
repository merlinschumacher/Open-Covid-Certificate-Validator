import os
import unittest

from occv import DCCValidator


class check_test_dcc(unittest.TestCase):

    def test_dcc_validator_success(self):
        """
        Check that the test dcc is valid.
        """
        dcc_validator = DCCValidator("XX")

        # An EUDCC (EU Digital COVID Certificate) quoted from:
        # https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/DE/2DCode/raw/1.json
        test_dcc = "HC1:6BF+70790T9WJWG.FKY*4GO0.O1CV2 O5 N2FBBRW1*70HS8WY04AC*WIFN0AHCD8KD97TK0F90KECTHGWJC0FDC:5AIA%G7X+AQB9746HS80:54IBQF60R6$A80X6S1BTYACG6M+9XG8KIAWNA91AY%67092L4WJCT3EHS8XJC$+DXJCCWENF6OF63W5NW6WF6%JC QE/IAYJC5LEW34U3ET7DXC9 QE-ED8%E.JCBECB1A-:8$96646AL60A60S6Q$D.UDRYA 96NF6L/5QW6307KQEPD09WEQDD+Q6TW6FA7C466KCN9E%961A6DL6FA7D46JPCT3E5JDLA7$Q6E464W5TG6..DX%DZJC6/DTZ9 QE5$CB$DA/D JC1/D3Z8WED1ECW.CCWE.Y92OAGY8MY9L+9MPCG/D5 C5IA5N9$PC5$CUZCY$5Y$527B+A4KZNQG5TKOWWD9FL%I8U$F7O2IBM85CWOC%LEZU4R/BXHDAHN 11$CA5MRI:AONFN7091K9FKIGIY%VWSSSU9%01FO2*FTPQ3C3F"
        test_dcc_content = "{1: 'DE', 6: 1622316073, 4: 1643356073, -260: {1: {'v': [{'ci': 'URN:UVCI:01DE/IZ12345A/5CWLU12RNOB9RXSEOP6FG8#W', 'co': 'DE', 'dn': 2, 'dt': '2021-05-29', 'is': 'Robert Koch-Institut', 'ma': 'ORG-100031184', 'mp': 'EU/1/20/1507', 'sd': 2, 'tg': '840539006', 'vp': '1119349007'}], 'dob': '1964-08-12', 'nam': {'fn': 'Mustermann', 'gn': 'Erika', 'fnt': 'MUSTERMANN', 'gnt': 'ERIKA'}, 'ver': '1.0.0'}}}"
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsInstance(content, dict)
        self.assertTrue(valid)
        self.assertEqual(str(content), test_dcc_content)

    def test_dcc_validator_invalid(self):
        """
        Check that the test dcc is invalid.
        """
        dcc_validator = DCCValidator("XX")

        # An EUDCC (EU Digital COVID Certificate) quoted from, that is not valid for the test cert:
        # https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/AT/2DCode/raw/1.json
        test_dcc = "HC1:NCFOXN%TS3DH3ZSUZK+.V0ETD%65NL-AH-R6IOOK.IR9B+9G4G50PHZF0AT4V22F/8X*G3M9JUPY0BX/KR96R/S09T./0LWTKD33236J3TA3M*4VV2 73-E3GG396B-43O058YIB73A*G3W19UEBY5:PI0EGSP4*2DN43U*0CEBQ/GXQFY73CIBC:G 7376BXBJBAJ UNFMJCRN0H3PQN*E33H3OA70M3FMJIJN523.K5QZ4A+2XEN QT QTHC31M3+E32R44$28A9H0D3ZCL4JMYAZ+S-A5$XKX6T2YC 35H/ITX8GL2-LH/CJTK96L6SR9MU9RFGJA6Q3QR$P2OIC0JVLA8J3ET3:H3A+2+33U SAAUOT3TPTO4UBZIC0JKQTL*QDKBO.AI9BVYTOCFOPS4IJCOT0$89NT2V457U8+9W2KQ-7LF9-DF07U$B97JJ1D7WKP/HLIJL8JF8JFHJP7NVDEBU1J*Z222E.GJ457661CFFTWM-8P2IUE7K*SSW613:9/:TT5IYQBTBU16R4I1A/9VRPJ-TS.7ZEM7MSVOCD4RG2L-TQJROXL2J:52J7F0Q10SMAP3CGfKHF0DWIH"
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsNone(content)
        self.assertFalse(valid)

    def test_dcc_validator_failure(self):
        """
        Check that the test dcc is broken.
        """
        dcc_validator = DCCValidator("XX")

        # An useless string that starts with the correct prefix but is not a valid dcc.
        test_dcc = "HC1:FFFFFFFFFFFFFFFFFFFFFFF"
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsNone(content)
        self.assertFalse(valid)

    def test_dcc_validator_de_signature_check(self):
        """
        Check that the test dcc validates a real DCC.
        """
        # Initialize the DCCValidator to download the certs
        # and check their signature
        dcc_validator = DCCValidator("DE")
        self.assertIsInstance(dcc_validator, DCCValidator)
        # Destroy the DCCValidator to recreate it
        del dcc_validator
        # Create a new DCCValidator that will read the local certs
        # and check their signature
        dcc_validator = DCCValidator("DE")
        self.assertIsInstance(dcc_validator, DCCValidator)

    def test_dcc_validator_real_validity(self):
        """
        Check that the test dcc validates a real DCC.
        """
        dcc_validator = DCCValidator("DE")

        # Get a real DCC from the environment provided by the CI system
        test_dcc = os.getenv("VALID_DCC", "")
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsNotNone(content)
        self.assertFalse(valid)


if __name__ == '__main__':
    unittest.main()
