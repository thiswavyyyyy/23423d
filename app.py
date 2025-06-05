from aiogram.utils import executor
from loader import dp
# Don`t remove this above, otherwise handlers will not be imported
import handlers
import logging


# Установите уровень логирования на INFO
logging.basicConfig(level=logging.INFO)

# Если вы хотите отключить отладочные сообщения только для aiogram
logging.getLogger("aiogram").setLevel(logging.WARNING)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
