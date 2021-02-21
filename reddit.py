import os
import time
import json
import shutil
import logging
import argparse
import requests
import praw
from redvid import Downloader
from glob import glob
from dolby import *

os.environ["DOLBYIO_API_KEY"] = "laPVb2EPkdXSBayHQDHCj4IbkqQAhFKH"
class App:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="sample dolby.io app for enhancing media file")
        self.parser.add_argument("input_file", help="local file path for an input file")
        self.parser.add_argument("output_file", help="local file path for writing output file")
        self.parser.add_argument("--info", help="INFO debugging output", action="store_true")
        self.parser.add_argument("--debug", help="DEBUG output", action="store_true")
        self.parser.add_argument("--key", help="Dolby.io Media Processingn API Key", default="")
        self.parser.add_argument("--wait", help="Seconds to wait in between status checks", default=6)

        self.args = self.parser.parse_args()

        if self.args.info:
            logging.basicConfig(level=logging.INFO)

        if self.args.debug:
            logging.basicConfig(level=logging.DEBUG)

        self.args.key = self.args.key or os.environ.get("DOLBYIO_API_KEY")
        if not self.args.key:
            raise ValueError("Use --key or set environment variable DOLBYIO_API_KEY")

    def _get_url(self, path):
        return "https://api.dolby.com/" + path

    def _get_headers(self):
        return {
            "x-api-key": self.args.key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def post_media_input(self, input_path, name):
        url = self._get_url("/media/input")
        headers = self._get_headers()
        body = {
            "url": name,
        }
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        presigned_url = data["url"]
        logging.info("Uploading {0} to {1}".format(input_path, presigned_url))
        with open(input_path, "rb") as input_file:
            requests.put(presigned_url, data=input_file)

    def post_media_enhance(self, input_url, output_url):
        url = self._get_url("/media/enhance")
        headers = self._get_headers()
        # Customization
        #
        # If you want to change the behavior of the enhance process you
        # can add parameters found in the API reference to this body.
        # https://dolby.io/developers/media-processing/api-reference/enhance
        body = {"input": input_url, "output": output_url}

        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()["job_id"]

    def get_media_enhance(self, job_id):
        url = self._get_url("/media/enhance")
        headers = self._get_headers()
        params = {"job_id": job_id}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data["status"] not in {"Pending", "Running"}:
            return data
        # Keep on retrying untill job is complete
        logging.debug(data["status"])
        print(".")
        time.sleep(self.args.wait)
        return self.get_media_enhance(job_id)

    def get_media_output(self, dlb_out, output_path):
        url = self._get_url("/media/output")
        headers = self._get_headers()
        params = {"url": dlb_out}

        with requests.get(url, params=params, headers=headers, stream=True) as response:
            response.raise_for_status()
            response.raw.decode_content = True
            logging.info("Downloading from {0} into {1}".format(response.url, output_path))
            with open(output_path, "wb") as output_file:
                shutil.copyfileobj(response.raw, output_file)

    def upload(self):
        # First we upload the input file to /media/input
        dlb_in = "dlb://in/enhance"
        print("Uploading file to location: {}".format(dlb_in))
        self.post_media_input(self.args.input_file, dlb_in)
        print("Uploaded file to location: {}".format(dlb_in))

        # Next, we start /media/enhance to begin enhancing
        dlb_out = "dlb://out/enhance"
        job_id = self.post_media_enhance(dlb_in, dlb_out)
        print("Job running with job_id: {}".format(job_id))

        # We need to check for results of the enhance process and display results
        # to the terminal.
        results = self.get_media_enhance(job_id)
        print("Job complete: {}".format(json.dumps(results, indent=4, sort_keys=True)))

        # When complete, we can download the result and save it locally
        print("Downloading file from location: {}".format(dlb_out))
        self.get_media_output(dlb_out, self.args.output_file)
        print("File available: {}".format(self.args.output_file))

    def main(self):
        # First we upload the input file to /media/input
        dlb_in = "dlb://in/enhance"
        print("Uploading file to location: {}".format(dlb_in))
        self.post_media_input(self.args.input_file, dlb_in)
        print("Uploaded file to location: {}".format(dlb_in))

        # Next, we start /media/enhance to begin enhancing
        dlb_out = "dlb://out/enhance"
        job_id = self.post_media_enhance(dlb_in, dlb_out)
        print("Job running with job_id: {}".format(job_id))

        # We need to check for results of the enhance process and display results
        # to the terminal.
        results = self.get_media_enhance(job_id)
        print("Job complete: {}".format(json.dumps(results, indent=4, sort_keys=True)))

        # When complete, we can download the result and save it locally
        print("Downloading file from location: {}".format(dlb_out))
        self.get_media_output(dlb_out, self.args.output_file)
        print("File available: {}".format(self.args.output_file))


reddit = praw.Reddit(username='enhancebot_BH', password='password', client_id='aF9EuE9d4zWsCg', client_secret='dsNKHJMFYbRzztvR7DrBZuUD8QnGLw', user_agent='enhancebot')

# Phrase to activate bot
keyphrase = '!enhancebot'

# Sub to live on
subreddit = reddit.subreddit('Bot_Test_I2R')
for comment in subreddit.stream.comments():
    if keyphrase in comment.body:
        # If the keyphrase is found, respond to it with code here...
        temp = str(comment.link_id).split('_', 1)
        link = temp[1]
        url = "https://www.reddit.com/r/" + str(comment.subreddit) + "/comments/" + link
        print(url)
        # comment.reply('Test!')
        submission = reddit.submission(link)
        print(submission.url)
        if str(submission.url).find("https://v.redd.it/") != -1:
            redditVid = Downloader(max_q=True)
            redditVid.url = str(submission.url)
            redditVid.download()
            path = str(os.path.dirname(__file__))
            pathList = str(os.listdir(os.path.dirname(__file__)))
            print(path)
            inputFile = glob(pathList + "*.mp4")[0]
            dolbyEnhancment = enhanceVideo(inputFile)
            dolbyEnhancment.printFile()
            dolbyEnhancment.main()
            exit(-1)


