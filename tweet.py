import tweepy

# Set up your API credentials
consumer_key = "BQpTeOTPlkH3wSjHd6mnFt5tJ"
consumer_secret = "XdP59gwvmyxGOFjrj84CF8N6d5jnImaFWi9i0WNjwTG9ft7myd"
access_token = "1781770895716974594-D4Dx44aPlFBVuJYs4885o9xSBPKAMh"
access_token_secret = "8vZ0bWihkb554hX5iZdD4vllHf28p1OCqzn3aw1yE743w"



bearer_token = "AAAAAAAAAAAAAAAAAAAAAAuutQEAAAAAb94gmBjZvnEHoXZrVg8Lhc8bPVY%3DED1xH9NA2Kwi53kyauttxPctBjTlixUTnaTGqeDquY6iRyRytm"

# You can authenticate as your app with just your bearer token
#tweepy_client = tweepy.Client(bearer_token=bearer_token)

# You can provide the consumer key and secret with the access token and access
# token secret to authenticate as a user
tweepy_client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)

#response = client.create_tweet(
#    text="This Tweet was Tweeted using Tweepy and Twitter API v2!"
#)
#print(f"https://twitter.com/user/status/{response.data['id']}")


#response = tweepy_client.search_recent_tweets("Tweepy")
# The method returns a Response object, a named tuple with data, includes,
# errors, and meta fields
#print(response.meta)

# In this case, the data field of the Response returned is a list of Tweet
# objects
#tweets = response.data

# Each Tweet object has default ID and text fields
#for tweet in tweets:
#    print(tweet.id)
#    print(tweet.text)

# By default, this endpoint/method returns 10 results
# You can retrieve up to 100 Tweets by specifying max_results
#response = tweepy_client.search_recent_tweets("Tweepy", max_results=100)