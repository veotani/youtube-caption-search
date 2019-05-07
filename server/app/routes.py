from app import app
import flask
from flask import request

from services import caption_retriever
from services.caption_processor import split_captions, split_by_pauses, get_intersection_captions_indexes, \
    merge_captions, get_similar_captions_indexes
from services.caption_indexator import index_captions, index_caption_pause_splitted
from services.caption_search import search_caption, search_caption_pause_splitted

import google.oauth2.credentials
import google_auth_oauthlib.flow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow

import os
import sys
import json

import redis

CLIENT_SECRETS_FILE = "secrets/client_secret_905645781686-rga1p5l65i2k4rnq8i50dsooamfqsk8b.apps.googleusercontent.com.json"

SCOPES = [
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtubepartner'
]

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
CLIENT_AUTH_REDIRECT_TO = 'http://127.0.0.1:4200'

r = redis.Redis(host='localhost', port=6379, db=0)


@app.route('/')
@app.route('/index')
def index():
    return "hello world"


@app.route('/add_to_index', methods=['POST'])
def add_to_index():
    session_key = json.loads(request.data.decode('utf8'))['public_key']
    object_from_redis = r.hgetall(session_key)
    credentials_pack = dict()
    for field in object_from_redis:
        credentials_pack[field.decode('utf8')] = object_from_redis[field].decode('utf8')
    credentials_pack['scopes'] = SCOPES

    credentials = google.oauth2.credentials.Credentials(
        **credentials_pack)
    video_id = json.loads(request.data.decode('utf8'))['videoId']
    client = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    captions = caption_retriever.write_video_captions_to_file(client, video_id)

    # Default indexing (1 caption = 1 document)
    index_captions(captions, video_id)

    # Merged captions w/o pauses between
    captions_formatted = split_by_pauses(captions)
    indexes_to_merge = get_intersection_captions_indexes(captions_formatted)
    merged_captions = merge_captions(captions_formatted, indexes_to_merge)
    index_caption_pause_splitted(merged_captions, video_id)

    # Merged captions with similar words
    captions_formatted = split_by_pauses(captions)
    indexes_to_merge = get_similar_captions_indexes(captions_formatted)
    merged_captions = merge_captions(captions_formatted, indexes_to_merge)
    index_caption_pause_splitted(merged_captions, video_id, "similar-captions")

    return flask.jsonify("indexed")


@app.route('/search/<query>')
def search(query):
    print(query, file=sys.stdout)
    return flask.jsonify(search_caption(query))


@app.route('/search_pause_splitted/<query>')
def search_pause_splitted(query):
    print(query, file=sys.stdout)
    return flask.jsonify(search_caption_pause_splitted(query))

@app.route('/search_similar_merged/<query>')
def search_similar_merged(query):
    return flask.jsonify(search_caption_pause_splitted(query, "similar-captions"))


@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.

    # flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    flow.redirect_uri = CLIENT_AUTH_REDIRECT_TO

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state
    print('Current state is: ' + str(state), file=sys.stdout)
    return flask.jsonify(authorization_url)


@app.route('/oauth2callback', methods=['POST'])
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    # state = flask.session['state']

    url = json.loads(request.data.decode('utf8'))['url']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)  # , state=state)
    flow.redirect_uri = CLIENT_AUTH_REDIRECT_TO

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = url
    print('Authorization url is: ' +
          authorization_response, file=sys.stdout
          )
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    credentials_to_store = credentials_to_dict(credentials, True)
    r.hmset(credentials_to_store['token'], credentials_to_store)
    return flask.jsonify(credentials_to_store['token'])


def credentials_to_dict(credentials, no_scope=False):
    if no_scope:
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
        }

    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}
