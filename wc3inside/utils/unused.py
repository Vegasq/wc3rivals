from typing import List

from wc3inside.utils.db import DB


chunk_size = 10000


def unused(db: DB, init_id: int) -> List[int]:
    """

    :param db: Db instance
    :param init_id: first game_id
    :return: List of IDs not created in DB
    """
    low = init_id - chunk_size
    high = init_id

    got = db.get_by_range(low, high)
    all_our_ids = [i["game_id"] for i in got]

    cur = low
    unused = []

    while cur <= high:
        if cur not in all_our_ids:
            unused.append(cur)
        cur += 1

    return unused
