# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers

import tweepy
from flask import Flask, redirect, url_for, render_template, request, session, jsonify
import json
import sys
import os
import stripe
import pandas as pd
from werkzeug.utils import secure_filename

from flask import make_response, Response

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer







app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

# Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    user.active = user.payment == helpers.payment_token()
    user.key = stripe_keys['publishable_key']
    return render_template('home.html', user=user)

# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))

# -------- Charge ---------------------------------------------------------- #
@app.route('/charge', methods=['POST'])
def charge():
    if session.get('logged_in'):
        user = helpers.get_user()
        try:
            amount = 1000   # amount in cents
            customer = stripe.Customer.create(
                email= user.email,
                source=request.form['stripeToken']
            )
            stripe.Charge.create(
                customer=customer.id,
                amount=amount,
                currency='usd',
                description='WorldWideVibes Charge'
            )
            helpers.change_user(payment=helpers.payment_token())
            user.active = True
            return render_template('home.html', user=user)
        except stripe.error.StripeError:
            return render_template('error.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


#---------------------------------------------------------------------------
# Twitter setup
consumer_key = os.environ['TWITTER_CONSUMER_KEY']
consumer_secret = os.environ['TWITTER_CONSUMER_SECRET']

access_token=os.environ['TWITTER_ACCESS_TOKEN']
access_token_secret=os.environ['TWITTER_TOKEN_SECRET']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


#-------------------------------------------------------------------------

@app.route("/search",methods=["POST"])
def search():
    search_tweet = request.data
    tweets = api.search(search_tweet, tweet_mode='extended', count=100, result_type="popular")
    analyser = SentimentIntensityAnalyzer()
    t2 = []
    for tweet in tweets:
        score = analyser.polarity_scores(tweet.full_text)
        t2.append(score)
    df = pd.DataFrame(t2)
    nrows = len(df)
    positives = len(df.loc[df['compound']>=0.25])
    negatives = len(df.loc[df['compound']<=- 0.25])
    neutrals = (nrows - positives - negatives)
    positives = round(positives/nrows*100, 2)
    negatives = round(negatives/nrows*100, 2)
    neutrals = round(neutrals/nrows*100, 2)

    sizes = [positives, negatives, neutrals]
    max_index = sizes.index(max(sizes))
    labels = 'Positive', 'Negative', 'Neutral'
    sentiment = labels[max_index]
    
    return "The sentimant about {} is mostly {}. It is {}% postive, {}% negative and {}% neutral." .format(search_tweet.decode('utf-8'), sentiment, positives, negatives, neutrals)





# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
