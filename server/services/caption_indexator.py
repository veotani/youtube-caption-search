from elasticsearch import Elasticsearch
from services.caption_processor import split_captions

es = Elasticsearch()


def index_captions(captions, video_id):
    for ctime, ctext in split_captions(captions):
        doc = {
            'time': ctime,
            'text': ctext,
            'video': video_id
        }
        es.index(index="simple-captions", doc_type='caption', body=doc)


def index_caption_pause_splitted(captions, video_id, index_name = "pause-splitted-captions"):
    for ctime, ctext in captions:
        doc = {
            'time': ctime,
            'text': ctext,
            'video': video_id,
        }
        es.index(index=index_name, doc_type='caption', body=doc)
