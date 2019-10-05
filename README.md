# WorldWideVibes
## How does the world feel today?

Given a user-specified topic or hashtag, this [Flask](https://flask.palletsprojects.com/en/1.1.x/) app will scrape Twitter for that topic, analyze the sentiment of the found tweets and display how the world (or at least Twitter, that is... ;) ) feels about that topic.

The app structure is based on the [Flaskex](https://github.com/anfederico/Flaskex) flask boilerplate. If you want to try out the app locally, you need to export your stripe-keys and Twitter tokens. To do that, locate your stripe secret key, your stripe publishable key and your Twitter consumer key, consumer secret, access token and token secret in your respective Stripe/ Twitter accounts. Then, on the command line, run

```
> export STRIPE_SECRET_KEY=your_secret_key
> export STRIPE_PUBLISHABLE_KEY=your_publishable_key
> export TWITTER_CONSUMER_KEY=your_consumer_key
> export TWITTER_CONSUMER_SECRET=your_consumer_secret
> export TWITTER_ACCESS_TOKEN=your_access_token
> export TWITTER_TOKEN_SECRET=your_token_secret
