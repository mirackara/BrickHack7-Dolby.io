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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reddit bot that enhances a post if it is a video hosted on Reddit")
    parser.add_argument("--key", help="Dolby.io Media Processing API Key", default="")
    parser.add_argument("--user", help="Username to reddit bot")
    parser.add_argument("--passw", help="Password to reddit bot")
    parser.add_argument("--id", help="Client id")
    parser.add_argument("--secret", help="Client secret")
    parser.add_argument("--name", help="Name of the bot")

    args = parser.parse_args()

    if not args.key:
        raise ValueError("Use --key to input a Dolby.io API Key")

    if not args.user:
        raise ValueError("Use --user to input username to Reddit bot account")

    if not args.passw:
        raise ValueError("Use --passw to input password to Reddit bot account")

    if not args.id:
        raise ValueError("Use --id to input client_id")

    if not args.secret:
        raise ValueError("Use --secret to input client_secret")

    if not args.name:
        raise ValueError("Use --name to input bot name")

    reddit = praw.Reddit(username=args.user, password=args.passw, client_id=args.id, client_secret=args.secret, user_agent=args.name)

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
                inputFile = glob(pathList + "*.mp4")[0]
                dolbyEnhancement = enhanceVideo(inputFile, args.key)
                dolbyEnhancement.main()




                path = str(os.path.dirname(__file__))
                pathList = str(os.listdir(os.path.dirname(__file__)))
                for file in glob(pathList + "*.mp4"):
                    pth = os.path.join(path + "/" + file)
                    os.remove(pth)


