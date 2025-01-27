import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker , AsyncAttrs
from sqlalchemy import Integer, Text, String, Join, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


DSN = 'postgresql+asyncpg://dimavorobev:1234@localhost:5432/netology_homeworks_aiohttp'
engine = create_async_engine(DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    
    @property
    def id_dict(self):
        return {'id': self.id}
    

class User(Base):
    """ Класс модели User """
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    advertisements: Mapped['Advertisement'] = relationship('Advertisement', back_populates='users')

    @property
    def dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'registration_time': self.registration_time.isoformat(),
            # 'advertisements': self.advertisements
        }
    

class Advertisement(Base):
    """
    Класс модели Advertisement связь с моделью User """
    __tablename__ = 'advertisement'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    heading: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str]=mapped_column(String, nullable=False)
    registration_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    users: Mapped['User'] = relationship(User, back_populates='advertisements')

    @property
    def dict(self):
        return {
            'id': self.id,
            'heading': self.heading,
            'description': self.description,
            'user_id': self.user_id,
            'date_of_creation': self.registration_time.isoformat(),
        }
    

async def init_orm():
    """ Инициализация ОРМ """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    """ Закрытие ОРМ """
    await engine.dispose()