Reddit and Twitter Media Enhancer Using Dolby.io API

Reddit Bot Functionality:
    Reddit bot is for the most part done.
    It can either stay in a certain subreddit, or All.
    Goes through every comment looking for a specified command.
    If the command is found, the bot will download the video using redvid.
    Then, it will upload the video to the Dolby.io API which returns a background noise suppressed video.
    Thirdly, the application will upload that new enhanced video to Streamable.
    Finally, the bot will reply with a link to the enhanced media hosted on Streamable.
    (The post has to be a video, otherwise the bot does not reply.)

Twitter Bot Functionality:
    NOT COMPLETE
    Looks for a specified keyword in replies to a tweet with media.
    Downloads the video, passes it through Dolby.io API, then uploads enhanced media as a reply.

Dependencies:
    You need Python 3 and above.
    Yuu need to install ffmpeg because reddit.py uses redvid.
