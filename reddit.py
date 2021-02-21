import os
import argparse
import praw
import time
import json
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
    parser.add_argument("--strmail", help="Streamable account email")
    parser.add_argument("--strpass", help="Streamable account password")

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

    if not args.strmail:
        raise ValueError("Use --strmail to input Streamable email")

    if not args.strmail:
        raise ValueError("Use --strpass to input Streamable password")

    reddit = praw.Reddit(username=args.user, password=args.passw, client_id=args.id, client_secret=args.secret, user_agent=args.name)

    # Phrase to activate bot
    keyphrase = '!enhancebotdolby.io'

    # List to keep track of which comments were replied to already
    replied_to = []

    # Sub to live on
    subreddit = reddit.subreddit('All')
    for comment in subreddit.stream.comments():
        if keyphrase in comment.body:
            # If the keyphrase is found, respond to it with code here...
            temp = str(comment.link_id).split('_', 1)
            link = temp[1]
            submission = reddit.submission(link)
            if str(submission.url).find("https://v.redd.it/") != -1 and comment.link_id not in replied_to:
                redditVid = Downloader(max_q=True)
                redditVid.url = str(submission.url)
                redditVid.download()
                path = str(os.path.dirname(__file__))
                pathList = str(os.listdir(os.path.dirname(__file__)))
                inputFile = glob(pathList + "*.mp4")[0]
                dolbyEnhancement = enhanceVideo(inputFile, args.key)
                dolbyEnhancement.main()

                with open(os.path.join(path + "/" + "outfile.mp4"), 'rb') as uploadFile:

                    file_processed = {
                        'file': ("Enhanced Output", uploadFile),
                    }

                    response = requests.post('https://api.streamable.com/upload', auth=(args.strmail, args.strpass), files=file_processed)
                    responseJson = response.json()

                path = str(os.path.dirname(__file__))
                pathList = str(os.listdir(os.path.dirname(__file__)))

                try:
                    comment.reply("Enhanced Video Link: https://streamable.com/" + responseJson['shortcode'])
                except:
                    print("Error, need to wait 2 minutes before replying again.")
                    time.sleep(120)
                    comment.reply("Enhanced Video Link: https://streamable.com/" + responseJson['shortcode'])

                replied_to.append(comment.link_id)

                response.close()

                for file in glob(pathList + "*.mp4"):
                    os.remove(os.path.join(path + "/" + file))
