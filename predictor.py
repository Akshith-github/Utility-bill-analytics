import json
import time
import pandas as pd
from requests import get, post
import datetime as dt


def extract_value(value):
    """
    Helper Method to Extract Cell Value from Response
    """
    if value['type'] == 'number':
        return value['text']
    elif value['type'] == 'string':
        return value['valueString']
    elif value['type'] == 'date':
        return value['valueDate']            
    elif value['type'] == 'time':
        return value['valueTime']
    elif value['type'] == 'phoneNumber':
        return value['valuePhoneNumber']
    elif value['type'] == 'object':
        objectKeys = value['valueObject'].keys();
        item_info = "" 
        for ok in objectKeys:
            item_info += ok + ":" + extract_value(value['valueObject'][ok]) + " "
        return item_info
    elif value['type'] == 'array':
        itemInfo = ""
        for item in value["valueArray"]:
            itemInfo += extract_value(item) + "; "
        return itemInfo[:-3] # ; 
    else:
        print("Skipping Unsupported Type")

def recognizer2DF(post_url, apim_key, headers, data_bytes, return_json=False,confidence_threshold = 0, query_interval=5):
    """
    Submits Table or Form to recognizer asyncronously and processes the response
    queryInterval amount of time to wait between checking whether a job is done
    Optional confidence_threshold to deterimine whether to process a extracted feild 
    @param return_json: if true, return the json response from the recognizer [Default: False]
    """
    print("requesting",post_url)
    try:
        # Submit Async Table Job to Form Recognizer Endpoint 
        resp = post(url = post_url, data = data_bytes, headers = headers)
        if resp.status_code == 202:
            # Query Submit Table Job
            get_url = resp.headers["operation-location"]
            resp = get(url = resp.headers["operation-location"], headers = {"Ocp-Apim-Subscription-Key": apim_key})
            resp_json = json.loads(resp.text)
            while resp_json["status"] == "running":
                resp = get(url = get_url, headers = {"Ocp-Apim-Subscription-Key": apim_key})
                resp_json = json.loads(resp.text)
                with open('log.json', 'a') as f:
                    # add time stamp to log
                    f.write(
                        json.dumps(
                            {"time": dt.datetime.now().isoformat(), "status": resp_json["status"]}) + "\n")
                    f.write(json.dumps(resp_json) + "\n\n\n")
                    # f.write(resp.text + "\n")
                time.sleep(query_interval)
            if resp_json["status"] == "succeeded":
                # Process Documents 
                if return_json:
                    return resp_json
                docResults = resp_json['analyzeResult']['documentResults']
                docs = []
                for doc in docResults:
                    fields = doc['fields']
                    docs.append({key:extract_value(fields[key]) for key in fields.keys() \
                                 if 'confidence' in fields[key] and fields[key]['confidence'] > confidence_threshold}) 
                return pd.DataFrame(docs)
            elif resp_json["status"] == "failed":
                print("Layout analyze failed:\n%s" % resp_json)
        else:
            print("POST analyze failed:\n%s" % resp.text)     
    except Exception as e:
        print("Code Failed analyze failed:\n%s" % str(e))

# Endpoint URL
apim_key = "9afc86c23f3a42ed82b86e0da93249e4"#r"<Subscription Key>"
endpoint =  "https://utilitybillanalyticsaisr.cognitiveservices.azure.com//formrecognizer/v2.1/prebuilt/receipt/analyze?includeTextDetails=true&locale=en-US"#r"<endpoint>"
# source = "/workspace/Utility-bill-analytics/sample_bills/test.jpeg"#r"<Image or PDF Source path>"
# /formrecognizer/v2.1/prebuilt/receipt/analyze?includeTextDetails=true&locale=en-US
headers = {
    # Request headers
    'Content-Type': "image/jpeg", #r'<form file type - application/pdf, image/jpeg, image/png, or image/tiff>',
    'Ocp-Apim-Subscription-Key': apim_key,
}

# with open(source, "rb") as f:
#     data_bytes = f.read()

def jsonPredictionFromImage(imgfilename=None,data_bytes=None):
    """
    Use recognizer2DF to return json response from recognizer
    """
    # Endpoint URL
    apim_key = "9afc86c23f3a42ed82b86e0da93249e4"#r"<Subscription Key>"
    endpoint =  "https://utilitybillanalyticsaisr.cognitiveservices.azure.com//formrecognizer/v2.1/prebuilt/receipt/analyze?includeTextDetails=true&locale=en-US"#r"<endpoint>"
    # source = "/workspace/Utility-bill-analytics/sample_bills/test.jpeg"#r"<Image or PDF Source path>"
    # /formrecognizer/v2.1/prebuilt/receipt/analyze?includeTextDetails=true&locale=en-US
    headers = {
        # Request headers
        'Content-Type': "image/jpeg", #r'<form file type - application/pdf, image/jpeg, image/png, or image/tiff>',
        'Ocp-Apim-Subscription-Key': apim_key,
    }
    if imgfilename:
        with open(imgfilename, "rb") as f:
            data_bytes = f.read()
    else:
        if not data_bytes:
            raise Exception("No Image or Data Bytes Provided")
    return recognizer2DF(endpoint, apim_key, headers, data_bytes, True)

# df = recognizer2DF(endpoint, apim_key, headers, data_bytes)
# df.to_csv("form_data.csv") # can now be processed with excel