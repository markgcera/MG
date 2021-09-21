import praw
import pandas as pd
import numpy as np
import re
from praw.models import MoreComments
reddit = praw.Reddit(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
    password="PASSWORD",
    user_agent="USER_AGENT",
    username="USERNAME")

course = 'cs'
pd.set_option('max_colwidth', 1000)
nmbrs = ['1', '2', '3', '4', '5', '6' , '7', '8', '9', '0']
df = []
moduleNames = set()
url = ''
# the following section is for scraping the posts' title and posts' body paragraphs for any CS module
# by checking if the character immediately after "cs" is a number
# this also factors in variables such has "CS" being in capital letters or small letters, as well as
# if there is a space in between the letters and the numbers. Eg: cs 1000, cs 1000, CS1000, CS 1000
for all_posts in reddit.subreddit('nus').search(course, limit = 10):
    if course in all_posts.title.casefold():
        indicesOfTargets = [i for i in range(len(all_posts.title)) if all_posts.title.casefold().startswith(course, i)]
        for indexOfTarget in indicesOfTargets:
            for nmbr in nmbrs:
                if all_posts.title[(indexOfTarget + 2): (indexOfTarget + 3)] == nmbr:
                    moduleNames.add((all_posts.title[indexOfTarget: (indexOfTarget + 6)]).strip())
                    continue
                if all_posts.title[(indexOfTarget + 3): (indexOfTarget + 4)] == nmbr and all_posts.title[(indexOfTarget + 2): (indexOfTarget + 3)] == ' ':
                    moduleNames.add((all_posts.title[indexOfTarget: (indexOfTarget + 7)]).strip())
    if course in all_posts.selftext.casefold():
        indicesOfTargets = [i for i in range(len(all_posts.selftext)) if all_posts.selftext.casefold().startswith(course, i)]
        for indexOfTarget in indicesOfTargets:
            for nmbr in nmbrs:
                if all_posts.selftext[(indexOfTarget + 2): (indexOfTarget + 3)] == nmbr:
                    moduleNames.add((all_posts.selftext[indexOfTarget: (indexOfTarget + 6)]).strip())
                if all_posts.selftext[(indexOfTarget + 3): (indexOfTarget + 4)] == nmbr and all_posts.selftext[(indexOfTarget + 2): (indexOfTarget + 3)] == ' ':
                    moduleNames.add((all_posts.selftext[indexOfTarget: (indexOfTarget + 7)]).strip())
# the section below is to filter out the edge cases in which the character after "CS" is a number
# but is not actually a nus cs mod. Eg: "CS 2k mods". Edge case I found during testing
for eachMod in moduleNames.copy():
    listOfLen = [len(x) for x in eachMod.split()]
    if len(listOfLen)>1:
        if listOfLen[1]<4:
            moduleNames.remove(eachMod)
# the section below is to do a second-layer scrape of any NUS CS mods by searching the comments
# of the posts that already have a CS mod in their title/body
# this is because some students recommend other new CS mods in their comments
# and the main goal of this programme is to search for as many CS mods as possible
# although during testing, this section below occasionally causes HTTP error likely due to there
# being too many searches which the Reddit API cannot handle, so simply comment out the block below if that occurs
for moduleName in moduleNames.copy():
    for post in reddit.subreddit('nus').search(moduleName, limit = 1000):
        url = post.url
        if ".jpg" in url:
            continue
        submission = reddit.submission(url=post.url)
        submission.comments.replace_more(limit=None)
        for top_level_comment in submission.comments:
            if course in top_level_comment.body:
                indicesOfTargets = [i for i in range(len(submission.comments)) if
                                top_level_comment.body.casefold().startswith(course, i)]
                for indexOfTarget in indicesOfTargets:
                    for nmbr in nmbrs:
                        if top_level_comment.body[(indexOfTarget + 2): (indexOfTarget + 3)] == nmbr:
                            moduleNames.add((top_level_comment.body[indexOfTarget: (indexOfTarget + 6)]).strip())
                            continue
                        if top_level_comment.body[
                        (indexOfTarget + 3): (indexOfTarget + 4)] == nmbr and top_level_comment.body[
                                                                             (indexOfTarget + 2): (
                                                                                     indexOfTarget + 3)] == ' ':
                            moduleNames.add((top_level_comment.body[indexOfTarget: (indexOfTarget + 7)]).strip())
            if isinstance(top_level_comment, MoreComments):
                continue
# filtering the module names for any edge cases once again
for eachMod in moduleNames:
    listOfLen = [len(x) for x in eachMod.split()]
    if len(listOfLen)>1:
        if listOfLen[1]<4:
            moduleNames.remove(eachMod)
print(moduleNames)

# the section below creates a simple Excel sheet with the post(s) body, post title, and comments regarding each
# individual module
for moduleName in moduleNames:
    for post in reddit.subreddit('nus').search(moduleName, limit = 10):
        url = post.url
        df.append([post.title, post.selftext, np.nan])
        if ".jpg" in url:
            continue
        submission = reddit.submission(url=post.url)
        for top_level_comment in submission.comments:
            if isinstance(top_level_comment, MoreComments):
                continue
            df.append([np.nan, np.nan, top_level_comment.body])
        df.append([np.nan, np.nan, np.nan])
    df = pd.DataFrame(df,  columns = ["title", "body", "comments"])
    df.to_excel(moduleName +'.xlsx')
    df =[]
