import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker , AsyncAttrs
from sqlalchemy import Integer, Text, String, Join, DateTime , func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


DSN = 'postgresql+asyncpg://dimavorobev:1234@localhost:5432/netology_homeworks_aiohttp'
engine = create_async_engine(DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    
    @property
    def id_dict(self):
        return {'id': self.id}
    

class User(Base):

    __tablename__ = 'app_users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    creation_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def dict(self):
        return{
            'id': self.id,
            'name': self.name,
            'creation_time': self.creation_time.isoformat(),
        }
    

async def init_orm():
    """ Инициализация ОРМ """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    """ Закрытие ОРМ """
    await engine.dispose()