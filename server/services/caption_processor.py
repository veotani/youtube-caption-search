import sys

def split_captions(captions):
    res = []
    for i in range(3, len(captions), 3):
        hhmmss = captions[i].split('.')[0]
        if len(hhmmss.split(':')) != 3:
            break
        hh = int(hhmmss.split(':')[0])
        mm = int(hhmmss.split(':')[1])
        ss = int(hhmmss.split(':')[2])
        sec = ss + 60*mm + 3600*hh
        
        res.append((sec, captions[i+1]))
    return res



def split_by_pauses(captions):
    captions_converted = []
    for i in range(3, len(captions), 3):
        hhmmss = captions[i].split('.')[0]
        if len(hhmmss.split(':')) != 3:
            break
        hh = int(hhmmss.split(':')[0])
        mm = int(hhmmss.split(':')[1])
        ss = int(hhmmss.split(':')[2])
        sec = ss + 60*mm + 3600*hh

        hhmmss_end = captions[i].split(',')[1].split('.')[0]
        hh_end = int(hhmmss_end.split(':')[0])
        mm_end = int(hhmmss_end.split(':')[1])
        ss_end = int(hhmmss_end.split(':')[2])
        sec_end = ss_end + 60 * mm_end + 3600 * hh_end
        
        captions_converted.append((sec, sec_end, captions[i+1]))

    return captions_converted

def get_intersection_captions_indexes(captions):
    intersecting_indexes = [set()]

    for index in range(1, len(captions)):
        if captions[index-1][1] >= captions[index][0]:
            intersecting_indexes[-1].add(index)
        else:
            intersecting_indexes.append(set())
            intersecting_indexes[-1].add(index)

    return intersecting_indexes

def merge_captions(captions, intersecting_indexes):
    res = []
    for group in intersecting_indexes:
        min_start_time = 60*60*15
        group_captions = ""
        for index in group:
            if captions[index][0] < min_start_time:
                min_start_time = captions[index][0] 
            group_captions += captions[index][2] + " "
        res.append((min_start_time, group_captions))

    return res