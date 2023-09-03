from sqlalchemy import Column, String, Text

from app.models.base import CharityProjectBase


class CharityProject(CharityProjectBase):
    __table_args__ = {'extend_existing': True}

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return (
            f'{super().__repr__()},'
            f'name={self.name},'
            f'description={self.description}'
        )
