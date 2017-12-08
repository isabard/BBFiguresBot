import praw
import pdb
import re
import os

# Create reddit instance
reddit = praw.Reddit('bot1')
subreddit = reddit.subreddit("pythonforengineers")

# # See if reply log exists
# # If not, create an empty list
# if not os.path.isfile("replied_to.txt"):
#     replied_to = []
# # If so, open it, read it in, splitting on newline, getting rid of empty values
# else:
#     with open("replied_to.txt", "r") as f:
#         replied_to = f.read()
#         replied_to = replied_to.split("\n")
#         replied_to = list(filter(None, replied_to))
#
# # Get the top 5 hot posts
# for submission in subreddit.hot(limit=10):
#     # For posts not already replied to,
#     if submission.id not in replied_to:
#         # Search for those "i love python" and reply
#         if re.search("i love python", submission.title, re.IGNORECASE):
#             submission.reply("I love Python, as well.")
#             print("Bot replying to: ", submission.title)
#             replied_to.append(submission.id)
#
# # Rewrite updated list
# with open("replied_to.txt", "w") as f:
#     for post_id in replied_to:
#         f.write(post_id + "\n")

# Look at comments in subreddit
for comment in subreddit.stream.comments():
    if re.search("works", comment.body, re.IGNORECASE):
        print("Found a comment: " + comment.body)
