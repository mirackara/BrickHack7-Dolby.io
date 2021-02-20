import praw
from redvid import Downloader

reddit = praw.Reddit(username='enhancebot_BH', password='', client_id='aF9EuE9d4zWsCg', client_secret='', user_agent='enhancebot')

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
        print('Commented!')
        if str(submission.url).find("https://v.redd.it/") != -1:
            redditVid = Downloader(max_q=True)
            redditVid.url = str(submission.url)
            redditVid.download()

