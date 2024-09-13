import json

def update_data():
    with open("db.json", "r") as json_file:
        data = json.load(json_file)
    return data


def save_data():
    with open("db.json", "w") as json_file:
        json.dump(data, json_file, indent=2)


async def create_post_button(memeLink):
    post_button = InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(
            text="Пост", url=f"https://t.me/{channelLink}/{memeLink.message_id}"
        )
    )
    return post_button


async def ban(id):
    if int(id) not in bannedUsers:
        bannedUsers.append(int(id))
        save_data()
        return f"Пользователь с ID {id} заблокирован."
    else:
        return f"Пользователь с ID {id} уже заблокирован."


async def unban(id):
    if int(id) in bannedUsers:
        bannedUsers.remove(int(id))
        save_data()
        return f"Пользователь с ID {id} разблокирован."
    else:
        return f"Пользователь с ID {id} уже разблокирован."

async def isBanned(id):
    if id in bannedUsers:
        await bot.send_message(
            id, "Вы забанены в этом боте.", reply_markup=types.ReplyKeyboardRemove()
        )
        return True
    return False

async def updateStats():
    top_list = sorted(approvedMemes.items(), key=lambda x: x[1]["memes"], reverse=True)
    stats = []
    total_approved = 0
    for rank, (user_id, data) in enumerate(top_list[:10], start=1):
        name = data["name"]
        memes = data["memes"]
        stats.append(
            f"**{rank}**: [{name}](tg://user?id={user_id}), **Мемов:** `{memes}`"
        )
        total_approved += memes
    result = "\n".join(stats)
    message = f"**Топ по принятым мемам:**\n{result}\n\nВсего принято мемов: `{total_approved}`"
    try:
        await bot.edit_message_text(
            chat_id=ChannelUsername,
            message_id=stats_message_id,
            text=f"{message}",
            parse_mode="Markdown",
        )
    except:
        return print("Stats message was not edited")
    print("Stats was updated")

async def where_is(message_id, minimal=False):
    data = update_data()
    memesToCheck = data["memes"]["memesToCheck"]
    supportMessages = data["supportMessages"]
    message_id = str(message_id)
    if message_id in memesToCheck:
        toReturn = memesToCheck
    elif message_id in supportMessages:
        toReturn = supportMessages
    if minimal == True:
        return toReturn
    else:
        return toReturn[message_id]
            

async def get_user_info(message_id):
    data = update_data()
    memesToCheck = data["memes"]["memesToCheck"]
    id = memesToCheck[message_id]["id"]
    type = memesToCheck[message_id]["type"]
    caption = memesToCheck[message_id]["caption"]
    reply_to = memesToCheck[message_id]["reply_to_id"]
    name = memesToCheck[message_id]["name"]
    return memesToCheck, id, type, caption, reply_to, name


async def edit_admin_message(message_id, chat_id, caption, reply_markup, type):
    if type == "text":
        await bot.edit_message_text(
            message_id=message_id,
            chat_id=GroupID,
            text=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )
    else:
        await bot.edit_message_caption(
            message_id=message_id,
            chat_id=GroupID,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=reply_markup,
        )

class meme:
    async def approve(message_id, adminId, adminName):
        memesToCheck, id, type, caption, reply_to, name = await get_user_info(message_id)

        print(f"#MemeAccept. Id: {id}, User: {name} Admin: {adminName}")

        if str(id) not in approvedMemes:
            memes = 1
        else:
            memes = approvedMemes[str(id)]["memes"] + 1
        approvedMemes[str(id)] = {"name": name, "memes": memes}

        memeLink = await bot.copy_message(
            chat_id=ChannelUsername, from_chat_id=GroupID, message_id=message_id
        )

        post_button = await create_post_button(memeLink)

        await edit_admin_message(message_id=message_id, chat_id=GroupID, type=type,
        caption=f"{caption}\n\n✅ Approved by [{adminName}](tg://user?id={adminId})", reply_markup=post_button)

        await bot.send_message(
            id,
            f"✅ Ваш мем был одобрен",
            reply_to_message_id=reply_to,
            disable_web_page_preview=True,
            reply_markup=post_button,
        )


        uncheckedMemes[str(id)] -= 1
        await updateStats()
        save_data()


    async def decline(message_id, adminId, adminName):
        try:
            memesToCheck, id, type, caption, reply_to, name = await get_user_info(message_id)
        except KeyError as e:
           print(f"Невозможно получить ключ {e}")
           return

        print(f"#MemeDecline. Id: {id}, User: {name} Admin: {adminName}")

        uncheckedMemes[str(id)] -= 1
        await bot.send_message(
            id,
            "❌ Ваш мем был отклонен",
            reply_to_message_id=reply_to,
            parse_mode="Markdown",
        )

        await edit_admin_message(message_id=message_id, chat_id=GroupID, type=type, reply_markup=rethinKb,
        caption=f"{caption}\n\n❌ Declined by [{adminName}](tg://user?id={adminId})")

        save_data()

    async def post(caption, name, id, chat_id, message_id):
        if str(id) not in approvedMemes:
            memes = 1
        else:
            memes = approvedMemes[str(id)]["memes"] + 1
        approvedMemes[str(id)] = {"name": name, "memes": memes}
        if caption is not None:
            caption = f"{caption}\n\nby [{name}](tg://user?id={id})"
        else:
            caption = f"\n\nby [{name}](tg://user?id={id})"
        memeLink = await bot.copy_message(
            chat_id=ChannelUsername,
            from_chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode="Markdown",
        )
        post_button = await create_post_button(memeLink)
        await bot.send_message(
            chat_id=chat_id,
            text="📥 Мем был отправлен в канал",
            reply_to_message_id=message_id,
            reply_markup=post_button,
        )
        await updateStats()

    async def rethink(message_id, adminId, name):
        data = update_data()
        memesToCheck = data["memes"]["memesToCheck"]
        whichKeyboard = await where_is(message_id, minimal=True)
        if whichKeyboard == memesToCheck:
            keyboard = memeKeyboard
        else:
            keyboard = supportkb
        message = await where_is(message_id)
        id = message["id"]
        type = message["type"]
        caption = message["caption"]
        await edit_admin_message(message_id=message_id, chat_id=GroupID, type=type, reply_markup=keyboard,
        caption=caption)


    async def ban(message_id, adminId, name):
        data = update_data()
        memesToCheck = data["memes"]["memesToCheck"]
        message = await where_is(message_id)
        id = message["id"]
        type = message["type"]
        caption = message["caption"]
        unban = InlineKeyboardButton("✅ Разбанить", callback_data="unban")
        unbanKb = InlineKeyboardMarkup(resize_keyboard=True)
        unbanKb.add(unban)
        await ban(id)
        await edit_admin_message(message_id=message_id, chat_id=GroupID, type=type, reply_markup=unbanKb,
        caption=f"{caption}\n\n⛔ Banned by [{name}](tg://user?id={adminId})")

    async def unban(message_id, adminId, name):
        data = update_data()
        memesToCheck = data["memes"]["memesToCheck"]
        message = await where_is(message_id)
        whichKeyboard = await where_is(message_id, minimal=True)
        if whichKeyboard == memesToCheck:
            keyboard = memeKeyboard
        else:
            keyboard = supportkb
        id = message["id"]
        type = message["type"]
        caption = message["caption"]
        await unban(id)
        await edit_admin_message(message_id=message_id, chat_id=GroupID, type=type, reply_markup=keyboard,
        caption=caption)


from main import *
from config import *
from keyboard import *
from variables import *
from handlers import *
