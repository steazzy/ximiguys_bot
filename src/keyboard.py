from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# User keyboard
mainKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
sendMemeBtn = types.KeyboardButton(text="Отправить мем")
sendMessageBtn = types.KeyboardButton(text="Написать в поддержку")
mainKeyboard.add(sendMemeBtn).add(sendMessageBtn)

# Owner (король, крутой тип) keyboard
adminKeyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
safeModeBtn = types.KeyboardButton(text="Безопасный режим")
dbBtn = types.KeyboardButton(text="Database")
adminKeyboard.add(sendMemeBtn)
adminKeyboard.add(safeModeBtn)
adminKeyboard.add(dbBtn)


acceptMeme = InlineKeyboardButton("✅ Принять", callback_data="acceptmeme")
declineMeme = InlineKeyboardButton("❌ Отклонить", callback_data="declinememe")
banButton = InlineKeyboardButton("⛔ Забанить", callback_data="ban")
memeKeyboard = InlineKeyboardMarkup(resize_keyboard=True)
memeKeyboard.add(acceptMeme)
memeKeyboard.add(declineMeme)
memeKeyboard.add(banButton)

cancelKb = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_1 = types.KeyboardButton(text="Отмена")
cancelKb.add(button_1)

rethinKb= InlineKeyboardMarkup(resize_keyboard=True)
rethinkButton = InlineKeyboardButton("🔄 Передумать", callback_data="rethink")
rethinKb.add(rethinkButton)

supportkb = InlineKeyboardMarkup(resize_keyboard=True).add(banButton)
