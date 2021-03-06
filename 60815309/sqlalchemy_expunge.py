"""
Reproducing
https://stackoverflow.com/questions/60815309/how-to-expunge-foreign-key-reocrds-in-sqlalchemy
"""
import contextlib
import enum
import re

from sqlalchemy import UniqueConstraint, ForeignKey, Integer, Column, Unicode, Enum, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import DetachedInstanceError

Base = declarative_base()


class Series(Base):
    __tablename__ = "Series"
    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    series_name = Column("SeriesName", Unicode(50), nullable=False, unique=True)


class Season(Base):
    __tablename__ = "Seasons"
    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    series_id = Column(
        "SeriesId", Integer, ForeignKey(f"{Series.__tablename__}.Id"), nullable=False
    )
    season_number = Column("SeasonNumber", Integer, nullable=False)

    series = relationship("Series", uselist=False, lazy="joined", innerjoin=True)
    __table_args__ = (
        UniqueConstraint("SeriesId", "SeasonNumber", name="UQ_SeriesId_SeasonNumber"),
    )


class Episode(Base):
    __tablename__ = "Episodes"
    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    episode = Column("Episode", Integer, nullable=False)
    episode_name = Column("EpisodeName", Unicode, nullable=True)
    season_id = Column(
        "SeasonId", Integer, ForeignKey(f"{Season.__tablename__}.Id"), nullable=False
    )

    season = relationship("Season", uselist=False, lazy="joined", innerjoin=True)
    __table_args__ = (
        UniqueConstraint("SeasonId", "Episode", name="UQ_SeasonId_Episode"),
    )


class DownloadStatus(enum.Enum):
    Start = "Start"
    Processing = "Processing"
    Downloading = "Downloading"
    Finish = "Finish"


class Request(Base):
    __tablename__ = "DownloadRequests"
    id = Column("Id", Integer, primary_key=True, autoincrement=True)
    status = Column("Status", Enum(DownloadStatus), nullable=False)
    episode_id = Column(
        "EpisodeId", Integer, ForeignKey(f"{Episode.__tablename__}.Id"), nullable=True
    )

    episode = relationship("Episode", uselist=False, lazy="joined", innerjoin=True)
    # NOTE: Commented out because there is no DownloaderId
    # __table_args__ = (
    #     UniqueConstraint("DownloaderId", "EpisodeId", name="UQ_DownloaderId_EpisodeId"),
    # )


def init_db(Session):
    session = Session()

    foo_series = Series(series_name="foo")
    bar_series = Series(series_name="bar")
    session.add(foo_series)
    session.add(bar_series)

    foo1 = Season(series=foo_series, season_number=1)
    foo2 = Season(series=foo_series, season_number=2)
    session.add(foo1)
    session.add(foo2)

    foo1_e1 = Episode(episode=1, episode_name="The Begging", season=foo1)
    foo2_e1 = Episode(episode=1, episode_name="All Over again", season=foo2)
    session.add(foo1_e1)
    session.add(foo2_e1)

    session.commit()
    session.flush()
    session.close()


@contextlib.contextmanager
def session_context(Session):
    session = Session()
    try:
        yield session
    finally:
        session.commit()
        # session.flush()
        session.close()


def _extract_class_name(error):
    return re.search("(?:Parent )?[iI]nstance <(.*) at 0x", error._message()).group(1)


def main():
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=True)
    init_db(Session)

    print("no expunge at all")
    with session_context(Session) as session:
        first_episode = session.query(Episode).first()
    try_get_info(first_episode)

    print("expunge only the first object")
    with session_context(Session) as session:
        first_episode = session.query(Episode).first()
        session.expunge(first_episode)
    try_get_info(first_episode)

    print("expunge only the first and second object")
    with session_context(Session) as session:
        first_episode = session.query(Episode).first()
        session.expunge(first_episode)
        session.expunge(first_episode.season)
    try_get_info(first_episode)

    print("expunge only the first, second and third object")
    with session_context(Session) as session:
        first_episode = session.query(Episode).first()
        session.expunge(first_episode)
        session.expunge(first_episode.season)
        session.expunge(first_episode.season.series)
    try_get_info(first_episode)

    print("expunge_all")
    with session_context(Session) as session:
        first_episode = session.query(Episode).first()
        session.expunge_all()
    try_get_info(first_episode)


def try_get_info(first_episode):
    try:
        first_episode.season.series.series_name == "foo"
    except DetachedInstanceError as e:
        print("{} is not expunged".format(_extract_class_name(e)))
    else:
        print("Working!")
    print()


if __name__ == '__main__':
    main()
