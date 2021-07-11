# -*- encoding: utf-8 -*-
import re
import collections
from datetime import datetime

def ignore_files_func(logs):
    return [log for log in logs if not re.search(r'\.[a-z]+$', log['url'])]
        
def start_at_func(start_at, logs):
    date_fstr = r'[%d/%b/%Y %H:%M:%S]'
    return [log for log in logs if datetime.strptime(log['date'], date_fstr) >= datetime.strptime(start_at, r'%d/%b/%Y %H:%M:%S')]
    
def stop_at_func(stop_at, logs):
    date_fstr = r'[%d/%b/%Y %H:%M:%S]'
    return [log for log in logs if datetime.strptime(log['date'], date_fstr) <= datetime.strptime(stop_at, r'%d/%b/%Y %H:%M:%S')]

def ignore_urls_func(list, logs):
    return [log for log in logs if not log['url'] in list]
    
def request_type_func(req_type, logs):
    return [log for log in logs if log['req_type'] == req_type]

def ignore_www_func(logs):
    for log in logs:
        log['url'] = log['url'].replace(r'www.', '')
    return logs

def slow_queries_func(logs):
    unique_urls = list(set([log['url'] for log in logs]))
    url_counter = collections.Counter([log['url'] for log in logs])
    sum_time = []
    avg_time = []
    for i, unique_url in enumerate(unique_urls):
        sum_time.append(0)
        for log in logs:
            if unique_url == log['url']:
                sum_time[i] += int(log['resp_time'])
    for i, t in enumerate(sum_time):
        avg_time.append(int(t / url_counter[unique_urls[i]]))
    avg_time.sort(reverse = True)
    return avg_time[0:5]
    
def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    date_ptrn = r'\[\d{2}\/[a-zA-Z]{3}\/\d{4} \d{2}:\d{2}:\d{2}\]'
    req_type_ptrn = r'(GET|POST|PUT|DELETE)'
    url_ptrn = r':\/\/\S*'
    resp_time_ptrn = r'\d+'
        
    log_re = re.compile(r'(?P<date>' + date_ptrn + 
        r') \W(?P<req_type>' + req_type_ptrn + 
        r') http(s|)(?P<url>' + url_ptrn + 
        r') \S+ \d+ (?P<resp_time>' + resp_time_ptrn + 
        r')')
    
    with open('log.log', 'r') as fp:
        data = fp.readlines()
    
    logs = []   #list of dicts {'date', 'req_type', 'url', 'resp_time'}

    for line in data:
        m = log_re.match(line)
        if m:
            logs.append(m.groupdict())
            
    if ignore_files:
        logs = ignore_files_func(logs)
    if ignore_urls:
        logs = ignore_urls_func(ignore_urls, logs)
    if start_at:
        logs = start_at_func(start_at, logs)
    if stop_at:
        logs = stop_at_func(stop_at, logs)
    if request_type:
        logs = request_type_func(request_type, logs)
    if ignore_www:
        logs = ignore_www_func(logs)

#log list is ready for analysis
    if slow_queries:
        return slow_queries_func(logs)
        
    url_counter = collections.Counter([log['url'] for log in logs])
    return [tuple[1] for tuple in url_counter.most_common(5)]