#Alexnader Shelton
#Meme grabber program
# pulls memes from reddit to be posted to an instagram account every hr and a half

from InstagramAPI import InstagramAPI #unoffical instagram api
import praw #Redddit api
import json #InstagramAPI uses Json data
import datetime #time stamps on posts
import os #saving image
import requests #downloading a photo from a link
import random #random photo
import time #intervals between posts
import hashlib #hashing file names
import sys #arguments to the script


           #visit reddit preferences api
######### Reddit API Credentials #############################
client_id= ''
client_secret=''
password=''
user_agent = ''
username = ''
##############################################################

path = '' #Path of where files should be saved to

#Instagram username & Password is passed into program through arguments given to code
insta_user = sys.argv[1]
insta_pswd = sys.argv[2]
timeBetweenPosts = sys.argv[3] #in minutes:
subreddit_list = ['memes','dank_meme'] #list of subreddits the bot goes through

captionList = ['Beans','Premium memes posted all day every day','I post memes all day', 'All I do is make and browse memes', 'My memes are superior just admit it','Share this with 5 homies', 'I need to get off the internet', 'Krumpit','Fart','ayy lmao', 'Haha rawr XD', 'If I punch myself and it hurts does that make me strong or weak?']
#tags added to photo
tags = '#dankmemes #memes #meme #dank #funny #lol #cringe #edgy #dankmeme #edgymemes #funnymemes #anime #memesdaily #lmfao #follow #comedy #hilarious #nochill #ayylmao #triggered #fortnite #savage'

#holds the name of every file downloaded in the directory
files = []

#Reddit API instance
reddit = praw.Reddit(client_id=client_id,
                    client_secret=client_secret, password=password,
                    user_agent=user_agent, username=username)


#Add tags goes to your most recent post and adds a comment of tags to the image
#Called right after post since there insnt a way to add comments to post only caption
def addTags():
    user_posts = instaBot.getSelfUserFeed()
    feed = instaBot.LastJson #load json data
    latestMediaItem = feed["items"][0] #pull index 0 - most recent post
    latestMediaItemID = latestMediaItem["caption"]["media_id"] #capture media id

    instaBot.comment(mediaId=latestMediaItemID, commentText=tags)
    print("Tags added to photo")

#Post image picks a random file from the directory of images and posts it
#After the post, the file is deleted from folder and file list
def postImage():
    randomImage = random.randrange(0,len(files))
    randomCaption = random.randrange(0,len(captionList))

    desiredFile = files[randomImage]
    desiredCaption = captionList[randomCaption]

    instaBot.uploadPhoto(desiredFile, caption=desiredCaption)

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


#Since each file needs a unique name we create our file names using SHA1 hashing algorithm
def encodeName(post):
    url = hashlib.sha1((post.title).encode())
    encoded_url = url.hexdigest()
    encoded_url += '.jpg'
    return encoded_url


#Saving a reddit post to our files using requests on the image url
def save(post):
    url = post.url
    image = requests.get(url).content
    imageName = encodeName(post)


    with open(imageName, 'wb') as handler:
        handler.write(image)
        print('Image saved from meme: ' + str(post.title) + '\nImage had ' + str(post.ups) + ' upvotes')

    #Saving filename to list:
    files.append(imageName)

#Wipe all files goes through the list of files and deletes each file from the folder and list for a fresh start
def wipeAllFiles():
    for file in files:
        os.remove(file)
    files.clear()

#retreivePhotos loops through all the subdirectory posts and passes each post to evaluate
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
    instaBot.login()
    postCount = 0
    timeBetweenPosts = timeBetweenPosts*60 #convert to secconds for time.sleep
    while True:
        fileCount = (len(files) - 1)
        if fileCount < 2:
            retreivePhotos()

        time.sleep((sys.argv[3])*60) #takes third argument for sleep time in minutes. multiply by 60 for secconds
        postImage()
        addTags()
        postCount += 1

        if len(files)-1 > 7: #wipe all files when more than 7 are saved: New content only
            wipeAllFiles() #wipe all files to find new images to use, need new material only
