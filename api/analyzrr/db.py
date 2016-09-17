from sqlalchemy import Column, Unicode, Integer, Enum, ForeignKey
from sqlalchemy.orm import scoped_session, relationship, backref

from selfspy import models


def get_session():
    db = scoped_session(models.initialize("data.db"))
    return db


class NetworkLocation(models.SpookMixin, models.Base):
    fingerprint = Column(Unicode, index=True, unique=True)
    kind = Column(Enum("work", "personal"), nullable=False)

    def __repr__(self):
        return "<NetworkLocation '%s' (%s)>" % (self.fingerprint, self.kind)


class Network(models.SpookMixin, models.Base):
    action = Column(Enum("connect", "disconnect"), nullable=False)

    location_id = Column(Integer, ForeignKey(NetworkLocation.id), nullable=False)
    location = relationship(NetworkLocation, backref=backref('entries'))
