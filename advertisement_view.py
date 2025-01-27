from aiohttp import web
from models import Advertisement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from errors import get_http_error


async def get_advertisement_by_id(advertisement_id:int, session:AsyncSession):
    """ Метод получения Advertisement по id """
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, 'advertisement not found')
    return advertisement


async def add_advertisement(advertisement:Advertisement, session:AsyncSession):
    """ Метод обновления Advertisement """
    session.add(advertisement)
    try:
        await session.commit()
    except IntegrityError as err:
        raise get_http_error(web.HTTPConflict, 'The user is not specified or specified incorrectly')
    

async def delete_advertisement(advertisement:Advertisement, session:AsyncSession):
    """ Метод удаления  Advertisement """
    await session.delete(advertisement)
    await session.commit()


class AdvertisementView(web.View):
    """
    Класс предствление для Advertisement с методами POST, GET, DELETE, PATCH 
    и метод получения id из запроса 
    """

    @property
    def advertisement_id(self):
        return int(self.request.match_info['advertisement_id'])


    async def get(self):
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.request.session)
        return web.json_response(advertisement.dict)


    async def post(self):
        json_data = await self.request.json()
        advertisement = Advertisement(**json_data)
        await add_advertisement(advertisement, self.request.session)
        return web.json_response(advertisement.dict)


    async def patch(self):
        json_data = await self.request.json()
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.request.session)
        for field, value in json_data.items():
            setattr(advertisement, field, value)
        await add_advertisement(advertisement, self.request.session)
        return web.json_response(advertisement.dict)


    async def delete(self):
        advertisement = await get_advertisement_by_id(self.advertisement_id, self.request.session)
        await delete_advertisement(advertisement, self.request.session)
        return web.json_response({'status': 'delete' })