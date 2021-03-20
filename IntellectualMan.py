import imgflipAPI as imgflip
from datetime import datetime
import asyncio, json, random, sys

cookies = str(open("cookies.txt", "r").read())

generic = json.loads(str(open("generic.json", "r").read()))
tuned = json.loads(str(open("tuned_responses.json", "r").read()))

def search_triggers(text):
    responses = []
    for i in tuned:
        for t in i['triggers']:
            if t in text:
                responses.extend(i['responses'])
    return responses

def generate_comment(title, description, tags):
    if title == '' and description == '':
        return random.choice(generic)
    res = search_triggers(title.lower())
    res.extend(search_triggers(description.lower())) 
    res.extend(search_triggers(str(tags).lower()))
    if res == []:
        return random.choice(generic)
    res.extend(res)
    res.append(random.choice(generic))
    return random.choice(res)

async def send_comment():
    streamname = random.choice(json.loads(open("allowed_streams.json", "r").read()))
    blacklisted = json.loads(open("im_blacklist.json", "r").read())
    print("Looking in " + streamname + " for a meme")
    memes = await imgflip.get_stream_data(streamname)
    meme = await random.choice(memes).meme()
    if meme.author == "IntellectualMan":
        print("It's my own meme!")
        return
    elif meme.author in blacklisted:
        print("Blacklisted memer (" + meme.author + "). They know too much.")
        return
    om = open("commented.txt", "r")
    if "\n" + meme.link_id in om.read():
        print("Already commented on meme " + meme.link_id)
        return
    comment = generate_comment(meme.title, meme.description, meme.tags)
    print("Title: " + meme.title)
    print("Description: " + meme.description)
    print("Tags: " + str(meme.tags))
    print("Stream: " + meme.stream_name)
    print("Comment: " + comment)
    c = await meme.post_comment(comment)
    om = open("commented.txt", "a")
    om.write(meme.link_id + "\n")
    print(c.content)
    print("\n")


async def main():
    global cookies
    cookies = await imgflip.set_cookies(open("cookies.txt", "r").read())
    while True:
        now = datetime.now()
        time = now.strftime("%H:%M")
        time = time.split(":")
        time[0] = int(time[0])
        time[1] = int(time[1])
        time = (time[0] * 60) + time[1]
        d = await imgflip.get_user_data()
        if d['user']['user'] == None:
            print("REPLACE COOKIES NOW!!!!!")
            sys.exit()
        points = d['user']['points']
        # Minutes after midnight
        if (time > 420 and time < 720) or (time > 840 and time < 1020):
            cookies = await imgflip.set_cookies(open("cookies.txt", "r").read())
            if points < 10000:
                await send_comment()
            else:
                sys.exit()
        else:
            print("On break")
        # Record amount of points the bot has
        open("points.txt", "a").write("\n" + now.strftime("[%m/%d/%y %H:%M] " + str(points) + " points"))
        interval = random.randint(500,700)
        print("Waiting " + str(interval/60) + " minutes\n")
        await asyncio.sleep(interval)

    
    

asyncio.run(main())
