import os

from sqlalchemy import Boolean, Column, Float, Integer, JSON, String, update

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import  declarative_base, sessionmaker

_DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data.db"
)
engine = create_async_engine(f"sqlite+aiosqlite:///{_DB_PATH}", future=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class SongData(Base):
    __tablename__ = "song"
    id = Column(String, primary_key = True)
    name = Column(String)
    artists = Column(JSON)
    genres = Column(JSON, default = None)
    features = Column(JSON, default = None)
    

class Playlist(Base):
    __tablename__ = "playlist"
    id = Column(String, primary_key = True)
    owner = Column(String)
    data = Column(JSON, default = "{}")


if __name__ == "__main__":

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    import asyncio

    asyncio.run(create_tables())