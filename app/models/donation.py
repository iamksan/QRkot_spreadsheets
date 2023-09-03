from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import CharityProjectBase


class Donation(CharityProjectBase):
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)

    def __repr__(self):
        return (
            f'{super().__repr__()},'
            f'user_id={self.user_id},'
            f'comment={self.comment}'
        )
