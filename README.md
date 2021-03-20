# IntellectualManBot
Bot from imgflip that used to comment on conservative posts

This requires **requests** and **BeautifulSoup4**.

### What is everything?

* **allowed_streams.json** - A list of streams that the bot is allowed to comment in.
* **generic.json** - A list of responses that the bot always has a chance of sending.
* **im_blacklist.json** - A list of users whose memes the bot won't comment on.
* **tuned_responses.json** - A series of trigger words and their respective responses.

### To get data for cookies.txt:

Log into your bot account, go to the imgflip homepage, right click anywhere on the page, and then click on "Inspect Element." Click on the Network tab, and then click on a meme without closing the developer tools.

For Chrome:

![](doc_chrome.png)

For Firefox:

![](doc_firefox.png)

Copy and paste the big string of cookies into your cookies.txt file, and you should be good to go. 
