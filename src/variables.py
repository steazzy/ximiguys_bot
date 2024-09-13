import logging
from functions import update_data
from config import ChannelUsername, API_TOKEN
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, types


storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

data = update_data()


class Form(StatesGroup):
    meme = State()
    message = State()

bannedUsers = data["users"]["bannedUsers"]
uncheckedMemes = data["users"]["uncheckedMemes"]
approvedMemes = data["users"]["approvedMemes"]
memesToCheck = data["memes"]["memesToCheck"]
supportMessages = data["supportMessages"]
channelLink = ChannelUsername[1:]
safeMode = False
