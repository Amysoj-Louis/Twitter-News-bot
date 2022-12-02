from requests_oauthlib import OAuth1Session
import os
import json
import requests
from bs4 import BeautifulSoup
import time


def init():
    consumer_key = "<consumer_key>"
    consumer_secret = "<consumer_secret>"

    # Get request token
    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token and secret")

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    scrape(oauth)


def scraper(oauth):
    previous_tweet = {}

    while True:
        page = requests.get(
            "https://www.reuters.com/business/future-of-money/")
        soup = BeautifulSoup(page.content, "html.parser")
        home = soup.find(class_="editorial-franchise-layout__main__3cLBl")
        posts = home.find_all(
            class_="text__text__1FZLe text__dark-grey__3Ml43 text__inherit-font__1Y8w3 text__inherit-size__1DZJi link__underline_on_hover__2zGL4")
        top_post = posts[0].find(
            "h3", class_="text__text__1FZLe text__dark-grey__3Ml43 text__medium__1kbOh text__heading_3__1kDhc heading__base__2T28j heading__heading_3__3aL54 hero-card__title__33EFM").find_all("span")[0].text.strip()
        # Be sure to add replace the text of the with the text you wish to Tweet. You can also add parameters to post polls, quote Tweets, Tweet with reply settings, and Tweet to Super Followers in addition to other features.
        payload = {
            "text": f"{top_post}\nSource:https://www.reuters.com/business/future-of-money/"}

        if previous_tweet != payload:
            previous_tweet = payload
            tweet(payload, oauth)
        else:
            print("Content hasn't changed")
        time.sleep(60)


def tweet(payload, oauth):

    # Making the request
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Showing the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    init()
