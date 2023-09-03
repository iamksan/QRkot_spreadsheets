from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Extra, Field, PositiveInt


class Base(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str]

    class Config:
        extra = Extra.forbid


class DonationCreate(Base):
    invested_amount: int = 0


class DonationResponse(Base):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class DonationDB(DonationResponse):
    user_id: int
    invested_amount: int
    fully_invested: bool = Field(False)
    close_date: Optional[datetime]
