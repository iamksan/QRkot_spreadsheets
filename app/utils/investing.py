from datetime import datetime
from typing import List

from app.models.base import CharityProjectBase


def investing(
    target: CharityProjectBase,
    sources: List[CharityProjectBase],
) -> List[CharityProjectBase]:
    modified = []
    for open_obj in sources:
        fund = min(
            target.full_amount - target.invested_amount,
            open_obj.full_amount - open_obj.invested_amount
        )
        for investment in [target, open_obj]:
            investment.invested_amount += fund
            if investment.invested_amount == investment.full_amount:
                investment.fully_invested = True
                investment.close_date = datetime.now()
        modified.append(open_obj)
        if target.fully_invested:
            break
    return modified
