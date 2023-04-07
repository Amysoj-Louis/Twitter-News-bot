from requests_oauthlib import OAuth1Session
import requests
from bs4 import BeautifulSoup
import time


user_id = 0000000000000000000  # Get userid from https://tweeterid.com/
bearer_token = "<BEARER_TOKEN>"
consumer_key = "<CONSUMER_KEY>"
consumer_secret = "<CONSUMER_SECRET>"
access_token = "<ACCESS_TOKEN>"
access_token_secret = "<ACCESS_TOKEN_SECRET>"


def init():
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret,
                          resource_owner_key=access_token, resource_owner_secret=access_token_secret)
    while True:
        page = requests.get("https://www.moneycontrol.com/")
        soup = BeautifulSoup(page.content, "html.parser")
        top_post_link = soup.select_one(
            ".tabs_container #keynwstb1 .tabs_nwsconlist li a")["href"]
        top_post_page = requests.get(top_post_link)
        top_post_soup = BeautifulSoup(top_post_page.content, "html.parser")
        top_post_title = top_post_soup.select_one(
            ".article_title.artTitle").text.strip()
        top_post_description = top_post_soup.select_one(
            ".article_desc").text.strip()
        payload = {
            "text": f"{top_post_title}\n\n{top_post_description}\nSource:{top_post_link}"}
        previous_payload = previous_tweet()
        if previous_payload != {"text": payload["text"].split("\n")[0]}:
            tweet(payload, oauth)
        else:
            print("Content hasn't changed")
        time.sleep(300)


def previous_tweet():
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {"tweet.fields": "text"}
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
        raise Exception(
            f"Request returned an error: {response.status_code} {response.text}")
    return {"text": response.json()["data"][0]["text"].split("\n")[0]} if response.json() != {'meta': {'result_count': 0}} else {"text": ""}


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r


def tweet(payload, oauth):
    response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
    try:
        message = response.json()["errors"][0]["message"]
    except:
        message = ""
    if "Your Tweet text is too long" in message:
        source = payload["text"].split("\n")[-1]
        title = payload["text"].split("\n")[:1][0]
        payload = {"text": f"{title}\nSource:{source}"}
        response = oauth.post("https://api.twitter.com/2/tweets", json=payload)
        print(response.json())
    else:
        print(response.json())


if __name__ == "__main__":
    init()
