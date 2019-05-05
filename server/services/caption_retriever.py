# Writes captions from video to file
import os
from pprint import pprint
from os import listdir
import sys

import google.oauth2.credentials
import google_auth_oauthlib.flow

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow


CLIENT_SECRETS_FILE = "secrets/client_secret_362782908966-e4h5nrqke9e9rp2l839100jvclbt3pvv.apps.googleusercontent.com.json"

SCOPES = [
  'https://www.googleapis.com/auth/youtube.force-ssl',
  'https://www.googleapis.com/auth/youtubepartner'
]

API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_auth_url():  
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  flow.redirect_uri = 'http://127.0.0.1:5000/'
  authorization_url, state = flow.authorization_url(
      access_type='offline',
      include_granted_scopes='true')
  return authorization_url

# def get_authenticated_service():
    
    
#     credentials = flow.run_console()
#     return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

def write_video_captions_to_file(client, video_id):
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    response = client.captions().list(
        part = 'id',
        videoId = video_id
    ).execute()
    
    if not response['items']:
        print('ERROR! No captions for video id {}'.format(video_id))
        return

    caption_id = response['items'][0]['id']

    captions = client.captions().download(id = caption_id).execute()

    decoded_captions = captions.decode('utf8').split('\n')
    
    return decoded_captions

#     with open(filename, mode='w+') as f:
#         for caption in decoded_captions:
#             f.write(caption + '\n')
# Пример: 
#client = get_authenticated_service()
#write_video_captions_to_file(client, 'w4rc63zv1n0', 'captions_to_index.txt')