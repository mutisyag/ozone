import concurrent.futures
import requests
import time


URL = 'www.github.com'

pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)


def invalidate_aggregation_cache():
    # TODO: replace this with proper stuff
    print(f'Invalidating - {time.time()}')
    # This will timeout even if it receives data
    requests.get(URL, timeout=0.01)
    print(f'Done invalidating - {time.time()}')
    return True
