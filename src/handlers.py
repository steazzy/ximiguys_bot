
from functions import *
from config import *
from variables import storage, FSMContext, Form


@dp.message_handler(text="Отправить мем", chat_type=types.ChatType.PRIVATE)
async def send_meme(msg: types.message):
    if await isBanned(msg.from_user.id):
        return
    if (
        str(msg.from_user.id) in uncheckedMemes
        and uncheckedMemes[str(msg.from_user.id)] >= 9
    ):
        return await msg.answer(
            "Сейчас на проверке слишком много мемов от вас, после проверки вы сможете опять присылать мемы"
        )
    if safeMode == True:
        return await msg.answer("Админ включил безопасный режим")
    await Form.meme.set()
    await msg.answer("📥 Отправьте ваш мем", reply_markup=cancelKb)


@dp.message_handler(text="Написать в поддержку", chat_type=types.ChatType.PRIVATE)
async def send_message(msg: types.message):
    if await isBanned(msg.from_user.id):
        return
    if safeMode == True:
        return await msg.answer("Админ включил безопасный режим")
    await Form.message.set()
    await msg.answer("📥 Отправьте ваше сообщение", reply_markup=cancelKb)


@dp.message_handler(commands="ban")
async def banCommand(msg: types.Message):
    if msg.from_user.id != OwnerID:
        return
    user_id = msg.get_args()
    result = await ban(user_id)
    await msg.answer(result)


@dp.message_handler(commands="unban")
async def unban_user(msg: types.Message):
    if msg.from_user.id != OwnerID:
        return
    user_id = msg.get_args()
    result = await unban(user_id)
    await msg.answer(result)


@dp.message_handler(commands="post")
async def post_from(msg: types.Message):
    if msg.from_user.id != OwnerID:
        return
    postMeme = msg.reply_to_message
    if postMeme is not None:
        await meme.post(
            postMeme.caption,
            postMeme.from_user.full_name,
            postMeme.from_user.id,
            postMeme.chat.id,
            postMeme.message_id,
        )


@dp.message_handler(commands="stats")
async def post_from(msg: types.Message):
    data = update_data()
    reply_to = msg.reply_to_message
    if reply_to is not None:
        name = reply_to.from_user.full_name
        id = reply_to.from_user.id
        user = f"[{name}](tg://user?id={id})"
        if str(id) not in approvedMemes:
            message = f"У {user} нет принятых мемов"
        else:
            memes = approvedMemes[str(id)]["memes"]
            message = f"Принятых мемов у {user}: `{memes}`"
    else:
        name = msg.from_user.full_name
        id = msg.from_user.id
        user = f"[вас](tg://user?id={id})"
        if str(id) not in approvedMemes:
            message = f"У {user} нет принятых мемов"
        else:
            memes = approvedMemes[str(id)]["memes"]
            message = f"У {user} `{memes}` принятых мемов"
    await msg.reply(message, parse_mode="Markdown")


@dp.message_handler(commands="start", chat_type=[types.ChatType.PRIVATE])
async def send_welcome(msg: types.message):
    if await isBanned(msg.from_user.id):
        return
    if msg.from_user.id != OwnerID:
        await msg.answer(
            "👋 Привет, тут ты можешь прислать свой мем или написать в поддержку",
            reply_markup=mainKeyboard,
        )
    else:
        await msg.answer(
            "Ку, босс",
            parse_mode="Markdown",
            reply_markup=adminKeyboard,
        )


@dp.message_handler(state="*", text="Отмена", chat_type=types.ChatType.PRIVATE)
async def cancel_handler(msg: types.message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return await msg.answer(
            "Произошла ошибка, возвращаем вас обратно", reply_markup=mainKeyboard
        )
    logging.info("Cancelling state %r", current_state)
    await state.finish()
    await msg.answer("Отменено.", reply_markup=mainKeyboard)


@dp.message_handler(
    content_types=types.ContentTypes.PHOTO
    | types.ContentTypes.VIDEO
    | types.ContentTypes.TEXT
    | types.ContentTypes.ANIMATION,
    state=Form.meme,
)
async def process_meme(msg: types.message, state: FSMContext):
    name = msg.from_user.full_name
    id = msg.from_user.id
    username = msg.from_user.username
    if msg.text:
        type = "text"
        caption = f"{msg.text}\n\nby [{name}](tg://user?id={id})"
        meme = await bot.send_message(
            chat_id=GroupID,
            text=caption,
            parse_mode="Markdown",
            reply_markup=memeKeyboard,
        )
    else:
        caption = msg.caption
        type = "media"
        if caption is not None:
            caption = f"{msg.caption}\n\nby [{name}](tg://user?id={id})"
        else:
            caption = f"by [{name}](tg://user?id={id})"
        meme = await bot.copy_message(
            message_id=msg.message_id,
            chat_id=GroupID,
            from_chat_id=id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=memeKeyboard,
        )
    memesToCheck[meme.message_id] = {
        "id": id,
        "name": name,
        "username": username,
        "type": type,
        "caption": caption,
        "reply_to_id": msg.message_id,
        "status": "unchecked"
    }
    await msg.reply("📨 Ваш мем был отправлен, дождитесь его проверки", reply_markup=mainKeyboard)
    if str(id) not in uncheckedMemes:
        uncheckedMemes[str(id)] = 1
    else:
        uncheckedMemes[str(id)] += 1
    save_data()
    await state.finish()


@dp.message_handler(
    content_types=types.ContentTypes.PHOTO
    | types.ContentTypes.VIDEO
    | types.ContentTypes.TEXT
    | types.ContentTypes.ANIMATION,
    state=Form.message,
)
async def proccess_message(msg: types.message, state: FSMContext):
    name = msg.from_user.full_name
    id = msg.from_user.id
    username = msg.from_user.username
    if msg.text:
        type = "text"
        caption = f"{msg.text}\n\nby [{name}](tg://user?id={id})"
        message = await bot.send_message(
            chat_id=GroupID,
            text=caption,
            parse_mode="Markdown",
            reply_markup=supportkb,
        )   
    else:
        caption = msg.caption
        type = "media"
        if caption is not None:
            caption = f"{msg.caption}\n\nby [{name}](tg://user?id={id})"
        else:
            caption = f"by [{name}](tg://user?id={id})"
        message = await bot.copy_message(
            message_id=msg.message_id,
            chat_id=GroupID,
            from_chat_id=id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=supportkb,
        )
    supportMessages[message.message_id] = {
        "id": id,
        "name": name,
        "type": type,
        "username": username,
        "caption": caption,
        "reply_to_id": msg.message_id,
    }
    await msg.reply("📨 Ваше сообщение в поддержку было отправлено, ожидайте ответа", reply_markup=mainKeyboard)
    save_data()
    await state.finish()


@dp.message_handler(text="Database")
async def send_bd(msg: types.Message):
    if msg.from_user.id != OwnerID:
        return
    db = open("db.json", "rb")
    await bot.send_document(OwnerID, document=db)


@dp.message_handler(text="Безопасный режим")
async def safeModeToggle(msg: types.Message):
    if msg.from_user.id != OwnerID:
        return
    global safeMode
    safeMode = not safeMode
    if safeMode == True:
        status = "включен"
    else:
        status = "выключен"
    await msg.answer(f"Безопасный режим был {status}")


@dp.callback_query_handler()
async def query_handler(callback: types.CallbackQuery):
    message_id = str(callback.message.message_id)
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name
    match callback.data:
        case "acceptmeme":
            await meme.approve(
                message_id,
                user_id,
                full_name,
            )
            await callback.answer("✅ Принято")
        case "declinememe":
            await meme.decline(
                message_id,
                user_id,
                full_name,
            )
            await callback.answer("❌ Отклонено")
        case "ban":
            await meme.ban(
                message_id,
                user_id,
                full_name,
            )
            await callback.answer("⛔ Забанено")
        case "unban":
            await meme.unban(
                message_id,
                user_id,
                full_name,
            )
        case "rethink":
            await meme.rethink(
                message_id,
                user_id,
                full_name,
            )
            await callback.answer("✅ Разбанено")


@dp.message_handler(chat_type=[types.ChatType.SUPERGROUP, types.ChatType.GROUP])
async def message_handler(msg: types.Message):
    data = update_data()
    reply_to = msg.reply_to_message
    if msg.chat.id != GroupID: return
    if reply_to is not None and reply_to.from_user.is_bot == True:
        message = str(reply_to.message_id)
        sendTo = await where_is(message)
        await bot.copy_message(
            from_chat_id=msg.chat.id,
            message_id=msg.message_id,
            reply_to_message_id=sendTo["reply_to_id"],
            chat_id=sendTo["id"]
        )
        await msg.reply("📩 Сообщение было отправлено")



@dp.message_handler()
async def message_handler(msg: types.Message):
    print(f"{msg.from_user.full_name}: {msg.text} Id: {msg.from_user.id}")

from main import *
from variables import *
