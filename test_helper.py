import glob
import json
import os


def load_fixtures(test_case):
    tests = [] 
    fixture_path = 'testdata/' + test_case + "/2DCode/raw/*.json"
    print("Loading test data from: " + fixture_path)
    for filename in glob.glob(fixture_path):
        with open(os.path.join(os.getcwd(), filename), 'r') as f:
            tests.append((filename, json.load(f)))

    return tests
