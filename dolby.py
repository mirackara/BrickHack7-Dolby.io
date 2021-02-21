import os
import time
import json
import shutil
import logging
import argparse
import requests


class enhanceVideo:
    def __init__(self, inputFilename, APIKey):
        self.inputFilename = inputFilename
        self.APIKey = APIKey
        self.bodyLink = ""
        self.headers = {}

    def setbodyLink(self, link):
        self.bodyLink = link

    def printFile(self):
        print(self.inputFilename)

    def dolbyURL(self, path):
        return "https://api.dolby.com/" + path

    def dolbyHeaders(self):
        self.headers = {
            "x-api-key": self.APIKey,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def dolbyBody(self):
        return {
            "url": self.bodyLink
        }

    def uploadToDolby(self):
        url = self.dolbyURL("/media/input")
        self.dolbyHeaders()
        body = self.dolbyBody()
        response = requests.post(url, json=body, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        presignedURL = data["url"]
        logging.info("Uploading {0} to {1}".format(self.inputFilename, presignedURL))
        with open(self.inputFilename, "rb") as fileToUpload:
            requests.put(presignedURL, data=fileToUpload)
        fileToUpload.close()

    def enhanceMedia(self, dlbIn, dlbOut):
        url = self.dolbyURL("/media/enhance")
        body = {"input": dlbIn, "output": dlbOut}
        response = requests.post(url, json=body, headers=self.headers)
        response.raise_for_status()
        return response.json()["job_id"]

    def checkStatus(self, job_id):
        url = self.dolbyURL("/media/enhance")
        params = {"job_id": job_id}
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        if data["status"] not in {"Pending", "Running"}:
            return data
        logging.debug(data["status"])
        print("Converting...")
        time.sleep(6)
        return self.checkStatus(job_id)

    def downloadEnhancedClip(self, dlb_out, outfileName):
        url = self.dolbyURL("/media/output")
        params = {"url": dlb_out}
        with requests.get(url, params=params, headers=self.headers, stream=True) as response:
            response.raise_for_status()
            response.raw.decode_content = True
            with open(outfileName, "wb") as outfileName:
                shutil.copyfileobj(response.raw, outfileName)

    def main(self):
        dlb_in = "dlb://in/enhance"
        self.setbodyLink(dlb_in)
        print("Uploading file {} to {}".format(self.inputFilename, dlb_in))
        self.uploadToDolby()
        print("Done uploading file {} to {}".format(self.inputFilename, dlb_in))
        print("Enhancing clip...")
        dlb_out = "dlb://out/enhance"
        job_id = self.enhanceMedia(dlb_in, dlb_out)
        print("Enhancing with job ID: {}".format(job_id))

        print("Checking status...")
        results = self.checkStatus(job_id)

        print("Enhancing completed with results: {}".format(json.dumps(results, indent=4, sort_keys=True)))

        print("Downloading file to directory..")
        self.downloadEnhancedClip(dlb_out, "outfile.mp4")
        print("File downloaded!")
