import requests, asyncio, json
from bs4 import BeautifulSoup

token = None
cookies = None


async def set_cookies(c):
    global cookies, token
    clist = c.split("; ")
    cdict = {}
    for i in clist:
        k = i.split("=")[0]
        v = i.split("=")[1]
        cdict[k] = v
    cookies = cdict
    dat = await get_user_data()
    token = dat['__tok']
    return cookies


def strip_commas(n):
    return int(n.replace(",", ""))


def base36encode(number):
    if not isinstance(number, (int)):
        raise TypeError('number must be an integer')
    if number < 0:
        raise ValueError('number must be positive')

    alphabet, base36 = ['0123456789abcdefghijklmnopqrstuvwxyz', '']

    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]


class MemePortal:
    def __init__(self):
        self.link = "https://imgflip.com/i/0"
        self.link_id = "0"
        self.id = 0
        self.author = "anonymous"
        self.upvote_ct = 0
        self.view_ct = 0
        self.comment_ct = 0
        self.title = ""
        self.type = 'jpg'
        self.stream_name = None

    async def meme(self):
        return await get_meme(self.link_id)

    async def post_vote(self, vote):
        return await post_vote(vote, self.id)

    async def post_comment(self, text):
        return await post_comment(text, self.id)


class Meme:
    def __init__(self):
        self.link = "https://imgflip.com/i/0"
        self.link_id = "0"
        self.id = 0
        self.author = "anonymous"
        self.authorid = 1
        self.upvote_ct = 0
        self.view_ct = 0
        self.comment_ct = 0
        self.tags = []
        self.title = ""
        self.submitted = False
        self.featured = False
        self.stream_name = None
        self.type = 'jpg'
        self.description = ""
        self.isNSFW = False

    async def post_vote(self, vote):
        return await post_vote(vote, self.id)

    async def post_comment(self, text):
        return await post_comment(text, self.id)



async def get_meme(iname):
    data = requests.get("https://imgflip.com/i/" + iname, cookies=cookies).content
    open("log.html", "wb").write(data)
    basic = str(data).split("img=")[1].split(";a=new XMLHttpRequest();")[0]
    basic = json.loads(basic)
    mtemp = Meme()
    mtemp.link = "https://imgflip.com/i/" + iname
    mtemp.link_id = iname
    mtemp.id = basic['id']
    mtemp.authorid = basic['uid']
    mtemp.submitted = basic['submitted']
    mtemp.featured = basic['featured']
    mtemp.stream_name = basic['stream_name']
    soup = BeautifulSoup(data, "html.parser")
    mtemp.author = soup.find('a', class_="u-username").text
    mtemp.view_ct = int(soup.find('span', class_="img-views").text.replace(',', '').split(" ")[0])
    try:
        mtemp.upvote_ct = int(soup.find('span', class_="img-votes").text.replace(',', '').split(" ")[0])
    except AttributeError:
        mtemp.upvote_ct = 0
    for t in soup.find_all('a', class_="img-tag"):
        mtemp.tags.append(t.text)
    if len(soup.find_all('div', class_="img-is-nsfw")) != 0:
        mtemp.isNSFW = True
    try:
        mtemp.description = soup.find("div", class_="img-desc").text.replace("\nIMAGE DESCRIPTION:\n", "", 1)
    except AttributeError:
        mtemp.description = ""
    try:
        mtemp.title = soup.find(id="img-title").text
    except AttributeError:
        mtemp.title = ""
    # Vote isn't working for some reason
    # mtemp.vote = await get_user_data(mtemp.id)
    # mtemp.vote = int(mtemp.vote['vote'])
    return mtemp


async def get_stream_data(stream, **kwargs):
    if stream == '':
        data = requests.get("https://imgflip.com/", cookies=cookies).content
    else:
        data = requests.get("https://imgflip.com/m/" + stream, cookies=cookies).content
    open("log.html", "wb").write(data)
    soup = BeautifulSoup(data, "html.parser")
    mlist = []
    htmlist = soup.find_all('div', class_="base-unit clearfix")
    memeln = len(htmlist)
    for i in range(0, memeln):
        #print(i)
        mportal = MemePortal()
        if stream == '':
            mportal.stream_name = stream
        try:
            mportal.title = soup.find_all('h2', class_='base-unit-title')[i].text
        except IndexError:
            mportal.title = ""
        mportal.author = soup.find_all('div', class_='base-author')[i].text[3:]
        if " in " in mportal.author:
            mportal.stream_name = mportal.author.split(' in ')[1]
            mportal.author = mportal.author.split(' in ')[0]
        # This FUCKING call gave me an aneurisym trying to figure how it out with out is an error!!
        try:
            mportal.link_id = soup('div', class_='base-img-wrap-wrap')[i].contents[0].contents[0]['href']  # lil shit!
        except:
            print("For whatever reason, I can't look at this meme because it's NSFW.")
            mportal.link_id = "/i/4qakll"
        mportal.link = "https://imgflip.com" + mportal.link_id
        try:
            mportal.link_id = mportal.link_id.split("i/")[1]
        except IndexError:
            mportal.link_id = mportal.link_id.split("gif/")[1]
        mportal.id = int(mportal.link_id, 36)
        info = soup('div', class_='base-view-count')[i].text.split(", ")
        mportal.view_ct = strip_commas(info[0].split(' ')[0])
        if len(info) == 2:
            if info[1].split(' ')[1][0] == 'u':
                mportal.upvote_ct = strip_commas(info[1].split(' ')[0])
            elif info[1].split(' ')[1][0] == 'c':
                mportal.comment_ct = strip_commas(info[1].split(' ')[0])
        elif len(info) == 3:
            mportal.upvote_ct = strip_commas(info[1].split(' ')[0])
            mportal.comment_ct = strip_commas(info[2].split(' ')[0])

        mlist.append(mportal)
    return mlist


async def get_user_data(m=9):
    if not m:
        m = 9
    res = requests.get("https://imgflip.com/ajax_get_le_data?i=" + str(m), cookies=cookies).content
    return json.loads(res)


async def toggle_NSFW(sfw):
    if not sfw:
        toggle = "NSFW"
    else:
        toggle = "SFW"
    return requests.post("https://imgflip.com/ajax_safemode", data={
        "safe": toggle,
        '__tok': token,
        '__cookie_enabled': 1
    }, cookies=cookies)


async def post_comment(text, iid):
    return requests.post("https://imgflip.com/ajax_add_comment", data={
        'text': text,
        'iid': iid,
        'comImage': 0,
        'parent_id': 0,
        'level': 0,
        '__tok': token,
        '__cookie_enabled': 1
    }, cookies=cookies)


async def post_vote(vote, iid):
    if vote < -1 or vote > 1:
        raise ValueError("Invalid vote")
    return requests.post("https://imgflip.com/ajax_vote", data={
        "new_vote": str(vote),
        "iid": str(iid),
        '__tok': token,
        '__cookie_enabled': 1
    }, cookies=cookies)


async def follow_user(uid):
    return requests.post("https://imgflip.com/ajax_follow_user", data={
        'uid': uid,
        'follow': 1,
        '__tok': token,
        '__cookie_enabled': 1
    })


