from elasticsearch import Elasticsearch
import sys

def search_caption(query):
    es = Elasticsearch()
    #r = es.search(index='simple-captions', doc_type='caption', q=query)
    r = es.search(index='simple-captions', q=query)
    result_array = r['hits']['hits'][0:10]

    get_text = lambda x: x['_source']['text'].replace('\n', '')
    get_videoid = lambda x: x['_source']['video']
    get_time = lambda x: x['_source']['time']

    time_array = list(map(get_time, result_array))
    video_id_array = list(map(get_videoid, result_array))
    text_array = list(map(get_text, result_array))

    res = []

    for index in range(len(time_array)):
        res.append({
            'link': f'https://youtu.be/{video_id_array[index]}?t={time_array[index]}',
            'text': text_array[index]
        })
    
    return res

def search_caption_pause_splitted(query, index_name='pause-splitted-captions'):
    es = Elasticsearch()
    r = es.search(index=index_name, q=query)
    result_array = r['hits']['hits'][0:10]

    get_text = lambda x: x['_source']['text'].replace('\n', '')
    get_videoid = lambda x: x['_source']['video']
    get_time = lambda x: x['_source']['time']

    time_array = list(map(get_time, result_array))
    video_id_array = list(map(get_videoid, result_array))
    text_array = list(map(get_text, result_array))

    res = []

    for index in range(len(time_array)):
        res.append({
            'link': f'https://youtu.be/{video_id_array[index]}?t={time_array[index]}',
            'text': text_array[index]
        })
    
    return res
    