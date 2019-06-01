#alex Shelton


from InstagramAPI import InstagramAPI
import praw
import json
import datetime
import os
import requests
import bcrypt #hashing image names
import random
import time
import hashlib
import sys #arguments to the script
from multiprocessing import Process
import subprocess #calls shell script uppon startup

## Reddit Script API Credentials ## Visit reddit / pref / app
client_id= ''
client_secret=''
password=''
user_agent = ''
username = ''
#####     #####     #####     #####     #####
## Path where files will be saved to ##
path = ''

#List of subreddits to browse through
subreddit_list = ['memes','dank_meme']
#Captions to add to photo post
captionList = ['Beans','jajaja','Premium memes posted all day every day','I post memes all day', 'All I do is make and browse memes', 'My memes are superior just admit it','Share this with 5 homies', 'I need to get off the internet', 'Krumpit','Fart','ayy lmao', 'Haha rawr XD', 'If I punch myself and it hurts does that make me strong or weak?']
# Tags to add to post
tags = '#dankmemes #memes #meme #dank #funny #lol #cringe #edgy #dankmeme #edgymemes #funnymemes #anime #memesdaily #lmfao #follow #comedy #hilarious #nochill #ayylmao #triggered #fortnite #savage'

files = []

reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret, password=password,
                    user_agent=user_agent, username=username)

#Add tags goes to your most recent post and adds a comment of tags to the image
#Called right after post since there insnt a way to add comments to post only caption
def addTags():
    #instaBot.login()
    user_posts = instaBot.getSelfUserFeed()
    feed = instaBot.LastJson
    latestMediaItem = feed["items"][0]
    latestMediaItemID = latestMediaItem["caption"]["media_id"]

    instaBot.comment(mediaId=latestMediaItemID, commentText=tags)
    print("Tags added to photo")
    #instaBot.logout()

#Post image picks a random file from the directory of images and posts it
#After the post, the file is deleted from folder and file list
def postImage():
    randomImage = random.randrange(0,len(files))
    randomCaption = random.randrange(0,len(captionList))

    desiredFile = files[randomImage]
    desiredCaption = captionList[randomCaption]
    #instaBot.login()
    instaBot.uploadPhoto(desiredFile, caption=desiredCaption)

    #instaBot.logout()
    print("Image has been posted")
    #delete file from directory and list:
    del files[randomImage] #deleted from list
    os.remove(desiredFile)
    print("File destroyed from directory")

#Evaluate runs each post through a test checking how long since the post was made and how many upvotes it has`
#The more upvotes with less time = better post to save
def evaluate(post):
    print("Evaluating: ", post.id)
    upvotes = post.ups
    time = post.created
    age = datetime.datetime.fromtimestamp(time)
    #Age is now the utc date timestamp of post: now converting into secconds since
    now = datetime.datetime.now()
    #converting to secconds and / 3600 for hours, need to absolute value to dussssse some times are (-)
    ellapsed = abs((((now - age).total_seconds()) / 3600.0))

    if ellapsed < 1.5 and upvotes > 8000:
        return True
    elif ellapsed >= 1.5 and ellapsed <= 4 and upvotes > 12000:
        return True
    elif ellapsed > 4 and ellapsed < 7 and upvotes > 36000:
        return True
    else:
        return False


#Since each file needs a unique name we create our file names using SHA1 hashing algorithm
def encodeName(post):
    url = hashlib.sha1((post.title).encode())
    encoded_url = url.hexdigest()
    encoded_url += '.jpg'
    return encoded_url




#Saving a reddit post to our files using requests on the image url
def save(post):
    url = post.url
    if '.png' in url:
        return #only using jpg images for formatiing
    image = requests.get(url).content
    imageName = encodeName(post)
    with open(imageName, 'wb') as handler:
        handler.write(image)
        print('Image saved from meme: ' + str(post.title) + '\nImage had ' + str(post.ups) + ' upvotes')
    #Saving filename to list:
    files.append(imageName)


#Wipe all files goes through the list of files and deletes each file from the folder and list for a fresh start
def wipeAllFiles():
    subprocess.call(['./cleanfile.sh'], shell=True) #calling shell file to erase all photos
    files.clear()


def retreivePhotos():
    print("Scraping images,")
    for name in subreddit_list:
        subreddit = reddit.subreddit(name)
        hotList  = subreddit.hot(limit=15)
        #loop through posts of each subreddit
        for post in hotList:
            if evaluate(post):
                save(post)


#Autono
def autonomousUser(timeBetweenPosts):
    postCount = 0
    while True:
        fileCount = (len(files)-1)
        if fileCount < 2:
            retreivePhotos()
        time.sleep(timeBetweenPosts*60)
        postImage()
        addTags()
        postCount += 1

        if len(files)-1 > 7:
            wipeAllFiles()






# def commentModerator():
#     user_posts = instaBot.getSelfUserFeed()
#     feed = instaBot.LastJson
#     numPosts = 0
#     while numPosts < 5:
#         latestMediaItem = feed["items"][numPosts]
#         latestMediaItemID = latestMediaItem["caption"]["media_id"]
#         instaBot.getMediaComments(latestMediaItem)
#         comments = instaBot.LastJson
#
#         for comment in comments:
#             print(comment['user']['comment']['text'])



if __name__ == '__main__':
    #Creating bot
    subprocess.call(['./cleanfile.sh'], shell=True) #calling shell file to erase all photos
    instaBot = InstagramAPI(sys.argv[1], sys.argv[2])
    instaBot.login()
    # #
    # #process 1.) Autonomous searching and posting:
    autoUser = Process(target = autonomousUser(int(sys.argv[3])))
    autoUser.start() #starting first process of bot
    # #
    # #
    #
    instaBot.logout()
