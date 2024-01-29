import asyncio
import logging
import os

# получение пользовательского логгера и установка уровня логирования
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)

# настройка обработчика и форматировщика в соответствии с нашими нуждами
log_file = os.path.join(f"log_directory/{__name__}.log")
py_handler = logging.FileHandler(log_file, mode='w')

#py_handler = logging.FileHandler(f"{__name__}.log", mode='w')
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# добавление форматировщика к обработчику
py_handler.setFormatter(py_formatter)
# добавление обработчика к логгеру
py_logger.addHandler(py_handler)


def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            py_logger.info(f"func: {func.__qualname__}"
                           f"Параметры: args={args}, kwargs={kwargs}")
            return func(*args, **kwargs)
        except Exception as e:
            py_logger.error(f"func: {func.__qualname__}"
                            f"Параметры: args={args}, kwargs={kwargs} "
                            f"Ошибка такого типа: {e}")
            return False
    return wrapper


def async_exception_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            py_logger.info(f"func: {func.__qualname__}"
                           f"Параметры: args={args}, kwargs={kwargs}")
            return await func(*args, **kwargs)
        except Exception as e:
            py_logger.error(f"func: {func.__qualname__}"
                            f"Параметры: args={args}, kwargs={kwargs} "
                            f"Ошибка такого типа: {e}")
            return False
    return wrapper

