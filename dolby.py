import os
import time
import json
import shutil
import logging
import argparse
import requests

class enhanceVideo:
    def __init__(self,inputFilename):
        self.inputFilename = inputFilename
    
    def printFile(self):
        print(self.inputFilename)
    

    def main(self):
        dlb_in = "dlb://in/enhance"
        print("Uploading file {} to {}".format(self.inputFilename,dlb_in))