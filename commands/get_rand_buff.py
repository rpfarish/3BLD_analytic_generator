import random


def get_rand_buff(all_buffers_order: list):
    buffers = all_buffers_order.copy()
    random.shuffle(buffers)
    for i in buffers:
        print(i, end='')
        resp = input().lower()
        if resp.startswith('q') or 'quit' in resp:
            return
