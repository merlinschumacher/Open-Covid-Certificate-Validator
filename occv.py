import os
from typing import Union

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from validator import DCCValidator

# get the server country from the environment 
CERT_COUNTRY = os.getenv("CERT_COUNTRY", "XX")

api_description = """
    Open Covid Certificate Validator API

    This API will validate compliant EU Digital Covid Certificates.
    """ 


app = FastAPI(title="Open Covid Certificate Validator", 
              description=api_description, 
              version="0.0.1", 
              )

# initialize the validation server
validator = DCCValidator(CERT_COUNTRY)

# defines the schema for the request
class DCCQuery(BaseModel):
    dcc: str = None
    class Config:
        schema_extra = {
            "example": {
                "dcc": "HC1:NCF0XN%..."
            }
        }


# defines the schema for the request
class DCCData(BaseModel):
    valid: bool = False
    dccdata: dict = None
    class Config:
        schema_extra = {
            "example": {
                    "valid": True,
                    "dccdata": {
                        "1": "AT",
                        "4": 1635876000,
                        "6": 1620324000,
                        "-260": {
                            "1": {
                                "v": [
                                {
                                    "dn": 1,
                                    "ma": "ORG-100030215",
                                    "vp": "1119349007",
                                    "dt": "2021-02-18",
                                    "co": "AT",
                                    "ci": "URN:UVCI:01:AT:10807843F94AEE0EE5093FBC254BD813#B",
                                    "mp": "EU/1/20/1528",
                                    "is": "Ministry of Health, Austria",
                                    "sd": 2,
                                    "tg": "840539006"
                                }
                                ],
                                "nam": {
                                "fnt": "MUSTERFRAU<GOESSINGER",
                                "fn": "Musterfrau-Gößinger",
                                "gnt": "GABRIELE",
                                "gn": "Gabriele"
                                },
                                "ver": "1.0.0",
                                "dob": "1998-02-26"
                            }
                        }
                    }
            }
        }


@app.get("/")
async def read_root():
    """
    Return the root path of the API
    """
    return {}

@app.post("/", response_model=DCCData)
async def validate_dcc(dcc: DCCQuery):
    """
    post call to read validate a received DCC
    """
    dcc = dcc.dcc
    try:
        valid, dcc_data = validator.validate(dcc)
    except Exception as error:
        print(error)
        raise HTTPException(status_code=415, detail=str("Data format incompatible."))
        dcc_data = None
        valid = False


    return  DCCData(valid=valid, dccdata=dcc_data) 