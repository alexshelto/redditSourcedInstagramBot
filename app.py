#Alexnader Shelton
#Meme grabber program
# pulls memes from reddit to be posted to an instagram account every hr and a half

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


           #visit reddit preferences api
######### Reddit API Credentials #############################
client_id= 'bggfuF1vKehqyg'
client_secret='pxIaMYmHVN3i28oYKk-D1qGv9_g'
password='memeanddestroy'
user_agent = 'memePuller'
username = 'almightyMeme'
##############################################################

path = '' #Path of where files should be saved to

#Instagram username & Password is passed into program through arguments given to code
insta_user = sys.argv[1]
insta_pswd = sys.argv[2]
#timeBetweenPosts = sys.argv[3] #in minutes:

subreddit_list = ['memes','dank_meme']

captionList = ['Beans','Premium memes posted all day every day','I post memes all day', 'All I do is make and browse memes', 'My memes are superior just admit it','Share this with 5 homies', 'I need to get off the internet', 'Krumpit','Fart','ayy lmao', 'Haha rawr XD', 'If I punch myself and it hurts does that make me strong or weak?']

tags = '#dankmemes #memes #meme #dank #funny #lol #cringe #edgy #dankmeme #edgymemes #funnymemes #anime #memesdaily #lmfao #follow #comedy #hilarious #nochill #ayylmao #triggered #fortnite #savage'

files = []

reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret, password=password,
                    user_agent=user_agent, username=username)









def addTags():
    instaBot.login() #log in
    user_posts = instaBot.getSelfUserFeed()
    feed = instaBot.LastJson #load json data
    latestMediaItem = feed["items"][0] #pull index 0 - most recent post
    latestMediaItemID = latestMediaItem["caption"]["media_id"] #capture media id

    instaBot.comment(mediaId=latestMediaItemID, commentText=tags)
    print("Tags added to photo")
    instaBot.logout()


def postImage():
    randomImage = random.randrange(0,len(files))
    randomCaption = random.randrange(0,len(captionList))

    desiredFile = files[randomImage]
    desiredCaption = captionList[randomCaption]
    instaBot.login()
    instaBot.uploadPhoto(desiredFile, caption=desiredCaption)

    instaBot.logout()
    print("Image has been posted")
    #delete file from directory and list:
    del files[randomImage] #deleted from list
    os.remove(desiredFile)
    print("File destroyed from directory")


def evaluate(post):
    print("Evaluating: ", post.id)
    upvotes = post.ups
    time = post.created
    age = datetime.datetime.fromtimestamp(time)
    #Age is now the utc date timestamp of post: now converting into secconds since
    now = datetime.datetime.now()
    #converting to secconds and / 3600 for hours, need to absolute value to dussssse some times are (-)
    ellapsed = abs((((now - age).total_seconds()) / 3600.0))

    if ellapsed < 1.5 and upvotes > 5500:
        return True
    elif ellapsed >= 1.5 and ellapsed <= 4 and upvotes > 8000:
        return True
    elif ellapsed > 4 and ellapsed < 7 and upvotes > 24000:
        return True
    elif ellapsed >= 7 and ellapsed <= 12 and upvotes > 42000:
        return True
    else:
        return False



def encodeName(post):
    url = hashlib.sha1((post.title).encode())
    encoded_url = url.hexdigest()
    encoded_url += '.jpg'
    return encoded_url



def save(post):
    url = post.url
    image = requests.get(url).content
    imageName = encodeName(post)


    with open(imageName, 'wb') as handler:
        handler.write(image)
        print('Image saved from meme: ' + str(post.title) + '\nImage had ' + str(post.ups) + ' upvotes')

    #Saving filename to list:
    files.append(imageName)


def wipeAllFiles():
    for file in files:
        os.remove(file)
    files.clear()



def retreivePhotos():
    print("Scraping images,")
    for name in subreddit_list:
        subreddit = reddit.subreddit(name)
        hotList  = subreddit.hot(limit=30)
        #loop through posts of each subreddit
        for post in hotList:
            if evaluate(post):
                save(post)







if __name__ == '__main__':
    #Creating bot
    instaBot = InstagramAPI(insta_user,insta_pswd)
    postCount = 0

    while True:
        fileCount = (len(files) - 1)
        if fileCount < 2:
            retreivePhotos()

        time.sleep(6000) # sleeping for 1.5 hours (the break betweeen the posts)
        postImage()
        addTags()
        postCount += 1

        if postCount % 7 == 0: #every 7 posts do this:
            wipeAllFiles() #wipe all files to find new images to use, need new material only
