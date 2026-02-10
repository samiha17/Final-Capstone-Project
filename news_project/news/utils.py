from requests_oauthlib import OAuth1Session
from django.conf import settings


class Tweet:
    """
    Singleton class for posting tweets to X (Twitter) API v2.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # Initialize OAuth1 session
            cls._instance.oauth = OAuth1Session(
                client_key=settings.TWITTER_API_KEY,
                client_secret=settings.TWITTER_API_SECRET,
                resource_owner_key=settings.TWITTER_ACCESS_TOKEN,
                resource_owner_secret=settings.TWITTER_ACCESS_SECRET,
            )
        return cls._instance

    def make_tweet(self, tweet_text):
        """
        Posts a tweet to X API v2.
        """
        url = "https://api.twitter.com/2/tweets"
        payload = {"text": tweet_text}

        response = self.oauth.post(url, json=payload)

        if response.status_code != 201:
            raise Exception(
                f"Tweet failed: Status {response.status_code}, Response: {response.text}"
            )

        return response.json()
