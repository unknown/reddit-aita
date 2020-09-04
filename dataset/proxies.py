import random

proxy_list = [
    'http://p.webshare.io:19999'
]

def random_proxy():
    i = random.randint(0, len(proxy_list) - 1)
    p = {
        'http': proxy_list[i]
    }
    return p

def remove_proxy(proxy):
    proxy_list.remove(proxy)
    print(f'Removed {proxy}-- {len(proxy_list)} proxies left')