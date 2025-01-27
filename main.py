import json
from aiohttp import web
from models import  init_orm, close_orm, Session
from user_view import UserView
from advertisement_view import AdvertisementView


app = web.Application()


async def orm_contexr(app: web.Application):
    print('start')
    await init_orm()
    yield
    print('finish')
    await close_orm()


@web.middleware
async def session_middleware(request:web.Request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_contexr)
app.middlewares.append(session_middleware)
       

app.add_routes([
    web.post('/user/', UserView),
    web.get('/user/{user_id:[0-9]+}/', UserView),
    web.patch('/user/{user_id:[0-9]+}/', UserView),
    web.delete('/user/{user_id:[0-9]+}/', UserView),
    web.post('/advertisement/', AdvertisementView),
    web.get('/advertisement/{advertisement_id:[0-9]+}/', AdvertisementView),
    web.patch('/advertisement/{advertisement_id:[0-9]+}/', AdvertisementView),
    web.delete('/advertisement/{advertisement_id:[0-9]+}/', AdvertisementView),
])
web.run_app(app)