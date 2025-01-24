import json
from aiohttp import web
from models import User, init_orm, close_orm, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


def get_http_error(err_cls, message:str|dict|list):
    error_message = json.dumps({'error': message})
    return err_cls(text = error_message, content_type='application/json')


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


async def get_user_by_id(user_id:int, session:AsyncSession):
    user = await session.get(User, user_id)
    if user is None:
        raise get_http_error(web.HTTPNotFound, 'user not found')
    return user


async def add_user(user:User, session:AsyncSession):
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as err:
        raise get_http_error(web.HTTPConflict, 'user already exists')
    

async def delete_user(user:User, session:AsyncSession):
    await session.delete(user)
    await session.commit()


class UserView(web.View):

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
        return web.json_response(user.id_dict)


    async def patch(self):
        json_data = await self.request.json()
        user = await get_user_by_id(self.user_id, self.request.session)
        for field, value in json_data.items():
            setattr(user, field, value)
        await add_user(user, self.request.session)
        return web.json_response(user.id_dict)


    async def delete(self):
        user = await get_user_by_id(self.user_id, self.request.session)
        await delete_user(user, self.request.session)
        return web.json_response({'status': 'delete' })

        


app.add_routes([
    web.post('/user/', UserView),
    web.get('/user/{user_id:[0-9]+}/', UserView),
    web.patch('/user/{user_id:[0-9]+}/', UserView),
    web.delete('/user/{user_id:[0-9]+}/', UserView),
])

web.run_app(app)