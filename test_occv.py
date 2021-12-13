import json

from fastapi.testclient import TestClient

from occv import DEV_MODE, app

DEV_MODE = True;

client = TestClient(app)

test_dcc = "HC1:6BF+70790T9WJWG.FKY*4GO0.O1CV2 O5 N2FBBRW1*70HS8WY04AC*WIFN0AHCD8KD97TK0F90KECTHGWJC0FDC:5AIA%G7X+AQB9746HS80:54IBQF60R6$A80X6S1BTYACG6M+9XG8KIAWNA91AY%67092L4WJCT3EHS8XJC$+DXJCCWENF6OF63W5NW6WF6%JC QE/IAYJC5LEW34U3ET7DXC9 QE-ED8%E.JCBECB1A-:8$96646AL60A60S6Q$D.UDRYA 96NF6L/5QW6307KQEPD09WEQDD+Q6TW6FA7C466KCN9E%961A6DL6FA7D46JPCT3E5JDLA7$Q6E464W5TG6..DX%DZJC6/DTZ9 QE5$CB$DA/D JC1/D3Z8WED1ECW.CCWE.Y92OAGY8MY9L+9MPCG/D5 C5IA5N9$PC5$CUZCY$5Y$527B+A4KZNQG5TKOWWD9FL%I8U$F7O2IBM85CWOC%LEZU4R/BXHDAHN 11$CA5MRI:AONFN7091K9FKIGIY%VWSSSU9%01FO2*FTPQ3C3F"

test_response = json.loads("""{
   "dccdata":{
      "-260":{
         "1":{
            "dob":"1964-08-12",
            "nam":{
               "fn":"Mustermann",
               "fnt":"MUSTERMANN",
               "gn":"Erika",
               "gnt":"ERIKA"
            },
            "v":[
               {
                  "ci":"URN:UVCI:01DE/IZ12345A/5CWLU12RNOB9RXSEOP6FG8#W",
                  "co":"DE",
                  "dn":2,
                  "dt":"2021-05-29",
                  "is":"Robert Koch-Institut",
                  "ma":"ORG-100031184",
                  "mp":"EU/1/20/1507",
                  "sd":2,
                  "tg":"840539006",
                  "vp":"1119349007"
               }
            ],
            "ver":"1.0.0"
         }
      },
      "1":"DE",
      "4":1643356073,
      "6":1622316073
   },
   "valid":true
}""")


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200


def test_validate_dcc_valid():
    response = client.post("/",
                           json={"dcc": test_dcc}
                           )
    assert response.status_code == 200
    assert response.json() == test_response


def test_validate_dcc_invalid():
    response = client.post("/",
                           json={"dcc": test_dcc}
                           )
    assert response.status_code == 200


def test_validate_dcc_empty():
    response = client.post("/",
                           json={}
                           )
    assert response.status_code == 415


def test_validate_dcc_none():
    response = client.post("/",
                           json=None
                           )
    assert response.status_code == 422
