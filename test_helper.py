import json
import glob
import os


def load_fixtures(test_case):
    tests = []
    fixture_path = 'testdata/' + test_case + "/2DCode/raw/*.json"
    print("Loading test data from: " + fixture_path)
    for filename in glob.glob(fixture_path):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            tests.append(json.load(f))

    return tests


def create_certdata_from_str(string):
    every = 64
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    data = '\n'.join(lines)
    data = "-----BEGIN CERTIFICATE-----\n" + data + "\n-----END CERTIFICATE-----"
    return data.encode()
