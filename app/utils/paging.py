import math
from app.errors import exceptions as ex
from typing import Optional


async def api_paging(total_count: Optional[int] = None, page_now: int = 1, page_set: int = 25, block_set: int = 5):
    if page_set > 100:
        raise ex.CustomEx("page_set의 최대 limit은 100입니다.")
    if block_set > 20:
        raise ex.CustomEx("block_set의 최대 limit은 20입니다.")

    if total_count is None or total_count == 0:
        raise ex.CustomEx("데이터가 없습니다.")

    total_page = math.ceil(total_count/page_set)
    total_block = math.ceil(total_page/block_set)
    block = math.ceil(page_now/block_set)
    limit_idx = (page_now - 1) * page_set

    first_page = ((block-1)*block_set)+1
    last_page = min(total_page, block*block_set)
    prev_page = page_now - 1
    next_page = page_now + 1

    return dict(
        limit_idx=limit_idx,
        page_set=page_set,
        page_now=page_now,
        total_list_count=total_count,
        total_page=total_page,
        total_block=total_block,
        first_page=first_page,
        last_page=last_page,
        prev_page=prev_page,
        next_page=next_page
    )
