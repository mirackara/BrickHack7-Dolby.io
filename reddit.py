import praw
reddit = praw.Reddit(username  = 'enhancebot_BH', password = '',client_id='aF9EuE9d4zWsCg', client_secret='', user_agent='enhancebot')

#Phrase to activate bot
keyphrase = '!enhancebot'

#Sub to live on
subreddit = reddit.subreddit('Bot_Test_I2R')

for comment in subreddit.stream.comments():
    if keyphrase in comment.body:
        # If the keyphrase is found, respond to it with code here...
        print('Commented!')