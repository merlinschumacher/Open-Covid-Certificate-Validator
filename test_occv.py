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
        # https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/AT/2DCode/raw/1.json
        test_dcc = "HC1:NCFOXN%TS3DH3ZSUZK+.V0ETD%65NL-AH-R6IOOK.IR9B+9G4G50PHZF0AT4V22F/8X*G3M9JUPY0BX/KR96R/S09T./0LWTKD33236J3TA3M*4VV2 73-E3GG396B-43O058YIB73A*G3W19UEBY5:PI0EGSP4*2DN43U*0CEBQ/GXQFY73CIBC:G 7376BXBJBAJ UNFMJCRN0H3PQN*E33H3OA70M3FMJIJN523.K5QZ4A+2XEN QT QTHC31M3+E32R44$28A9H0D3ZCL4JMYAZ+S-A5$XKX6T2YC 35H/ITX8GL2-LH/CJTK96L6SR9MU9RFGJA6Q3QR$P2OIC0JVLA8J3ET3:H3A+2+33U SAAUOT3TPTO4UBZIC0JKQTL*QDKBO.AI9BVYTOCFOPS4IJCOT0$89NT2V457U8+9W2KQ-7LF9-DF07U$B97JJ1D7WKP/HLIJL8JF8JFHJP7NVDEBU1J*Z222E.GJ457661CFFTWM-8P2IUE7K*SSW613:9/:TT5IYQBTBU16R4I1A/9VRPJ-TS.7ZEM7MSVOCD4RG2L-TQJROXL2J:52J7F0Q10SMAP3CG3KHF0DWIH"
        test_dcc_content = "{4: 1635876000, 6: 1620324000, 1: 'AT', -260: {1: {'v': [{'dn': 1, 'ma': 'ORG-100030215', 'vp': '1119349007', 'dt': '2021-02-18', 'co': 'AT', 'ci': 'URN:UVCI:01:AT:10807843F94AEE0EE5093FBC254BD813#B', 'mp': 'EU/1/20/1528', 'is': 'Ministry of Health, Austria', 'sd': 2, 'tg': '840539006'}], 'nam': {'fnt': 'MUSTERFRAU<GOESSINGER', 'fn': 'Musterfrau-Gößinger', 'gnt': 'GABRIELE', 'gn': 'Gabriele'}, 'ver': '1.0.0', 'dob': '1998-02-26'}}}"
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsInstance(content, dict)
        self.assertTrue(valid)
        self.assertEqual(str(content), test_dcc_content)
    
    def test_dcc_validator_invalid(self):
        """
        Check that the test dcc is invalid.
        """
        dcc_validator = DCCValidator("XX")

        # An EUDCC (EU Digital COVID Certificate) quoted from:
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

        # An EUDCC (EU Digital COVID Certificate) quoted from:
        # https://github.com/eu-digital-green-certificates/dgc-testdata/blob/main/AT/2DCode/raw/1.json
        test_dcc = "HC1:FFFFFFFFFFFFFFFFFFFFFFF"
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsNone(content)
        self.assertFalse(valid)
    
    def test_dcc_validator_real_validity(self):
        """
        Check that the test dcc validates a real DCC.
        """
        dcc_validator = DCCValidator("DE")

        # Get a real DCC from the environment provided by the CI system
        test_dcc = os.getenv("DCC", "")
        valid, content = dcc_validator.validate(test_dcc)
        self.assertIsNone(content)
        self.assertFalse(valid)

if __name__ == '__main__':
    unittest.main()
