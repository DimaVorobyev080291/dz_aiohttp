import json


def get_http_error(err_cls, message:str|dict|list):
    """ Метод обработки статуса ошибки и сообщение для нее """
    error_message = json.dumps({'error': message})
    return err_cls(text = error_message, content_type='application/json')