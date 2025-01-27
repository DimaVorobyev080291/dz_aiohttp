from aiohttp import web
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from errors import get_http_error


async def get_user_by_id(user_id:int, session:AsyncSession):
    """ Метод получения User по id """
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, 'user not found')
    return user


async def add_user(user:User, session:AsyncSession):
    """ Метод обновления User """
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as err:
        raise get_http_error(web.HTTPConflict, 'user already exists')
    

async def delete_user(user:User, session:AsyncSession):
    """ Метод удаления User """
    await session.delete(user)
    await session.commit()


class UserView(web.View):
    """
    Класс предствление для User с методами POST, GET, DELETE, PATCH 
    и метод получения id из запроса 
    """

    @property
    def user_id(self):
        return int(self.request.match_info['user_id'])


    async def get(self):
        user = await get_user_by_id(self.user_id, self.request.session)
        return web.json_response(user.dict)


    async def post(self):
        json_data = await self.request.json()
        user = User(**json_data)
        await add_user(user, self.request.session)
        return web.json_response(user.dict)


    async def patch(self):
        json_data = await self.request.json()
        user = await get_user_by_id(self.user_id, self.request.session)
        for field, value in json_data.items():
            setattr(user, field, value)
        await add_user(user, self.request.session)
        return web.json_response(user.dict)


    async def delete(self):
        user = await get_user_by_id(self.user_id, self.request.session)
        await delete_user(user, self.request.session)
        return web.json_response({'status': 'delete' })