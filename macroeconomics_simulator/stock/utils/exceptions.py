import logging

from rest_framework.response import Response


class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)


# logger conf... | make a separate file?
custom_logger = logging.getLogger('custom_logger')
custom_logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('logs.log', encoding='utf-8')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s (%(asctime)s): %(message)s [%(filename)s]', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
custom_logger.addHandler(handler)


def custom_exception(func: callable):
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except CustomException as e:
            return Response({"error": f"{e}"}, status=400)
    return wrapper
