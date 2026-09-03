import asyncio
import difflib
import os
import uuid
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from aiohttp import web

TOKEN = "8854942536:AAHwvwjuecCpgdf4p3stFebRH6z1SqdLI5I"
router = Router()

_hugs_and_touch = [
    "обнять",
    "прижать",
    "погладить",
    "гладь",
    "поглаживать",
    "массировать",
    "помассировать",
    "погреть",
    "согреть",
    "потрогать",
    "трогать",
    "помацать",
    "пожмякать",
    "мацать",
    "жмякать",
    "потискать",
    "затискать",
    "прильнуть",
    "ластиться",
    "млеть",
    "таять",
    "уткнуться",
    "прислониться",
    "притулиться",
    "потереться",
    "укрыть",
    "укутать",
    "окутать",
    "успокоить",
    "поддержать",
    "причесать",
    "перевязать",
    "пожать",
    "положить",
]

_kisses_and_love = [
    "поцеловать",
    "разцеловать",
    "цемнуть",
    "чмокнуть",
    "отчмокать",
    "зацеловать",
    "ласкать",
    "обласкать",
    "подарить",
    "поздравить",
    "пожелать",
    "извиниться",
    "похвалить",
]

_explicit_actions = [
    "засосать",
    "трахнуть",
    "оттрахать",
    "изнасиловать",
    "иметь",
    "отиметь",
    "отшлифовать",
    "трахать",
    "ебать",
    "выебать",
    "отсосать",
    "отлизать",
    "отполировать",
    "полировать",
    "отминенить",
    "ссосать",
    "высосать",
    "раздеть",
    "осеменить",
    "оплодотворить",
]

_bites_and_scratches = [
    "щекотать",
    "пощекотать",
    "укусить",
    "лизь",
    "лизнуть",
    "облизать",
    "вылизать",
    "полизать",
    "подлизать",
    "кусь",
    "куснуть",
    "покусать",
    "погрызть",
    "загрызть",
    "цап",
    "цапнуть",
    "царап",
    "поцарапать",
    "оцарапать",
    "исцарапать",
    "поноюхать",
    "занюхнуть",
    "нюх-нюх",
    "подразнить",
    "дразнить",
    "хыть-хыть",
]

_hits_and_fights = [
    "наказать",
    "шлеп",
    "шлепнуть",
    "шлепать",
    "отшлепать",
    "выпороть",
    "хлопнуть",
    "отхлопать",
    "хлопать",
    "ущипнуть",
    "щипать",
    "пощипать",
    "пихнуть",
    "толкнуть",
    "швырнуть",
    "бросить",
    "кинуть",
    "запульнуть",
    "запустить",
    "треснуть",
    "трепать",
    "потрепать",
    "взъерошить",
    "опрокинуть",
    "сбить",
    "повалить",
    "скрутить",
    "связать",
    "обезоружить",
    "отобрать",
    "выбить",
    "сдернуть",
    "сорвать",
    "ударить",
    "уебать",
    "ебануть",
    "долбануть",
    "ушатать",
    "порвать",
    "въебать",
    "разъебать",
    "пнуть",
    "попинать",
]

_kills_and_dangers = [
    "застрелить",
    "расстрелять",
    "отстрелить",
    "застрелиться",
    "порезаться",
    "стрельнуть",
    "шмальнуть",
    "сжечь",
    "поджечь",
    "убить",
    "уничтожить",
    "унизить",
    "арестовать",
    "оторвать",
    "отрубить",
    "отъебать",
    "отрезать",
    "порезать",
    "резать",
    "закопать",
    "выкопать",
    "взорвать",
    "подорвать",
    "заминировать",
    "кастрировать",
    "послать",
]

_food_and_drink = [
    "покормить",
    "покушать",
    "поесть",
    "есть",
    "кушать",
    "пить",
    "попить",
    "выпить",
    "попоить",
    "бухнуть",
    "хрум",
    "хрумкать",
    "хрустнуть",
]

_emotions_and_sounds = [
    "орать",
    "наорать",
    "рассмешить",
    "рассказать",
    "улыбнуться",
    "засмеяться",
    "заплакать",
    "ухмыльнуться",
    "нахмуриться",
    "закатить",
    "вздохнуть",
    "зевнуть",
    "кивнуть",
    "покачать",
    "подмигнуть",
    "помахать",
    "показать",
    "постучать",
    "указать",
    "ткнуть",
    "поделиться",
    "фырк",
    "фыркнуть",
    "хмык",
    "хмыкнуть",
    "мур",
    "мурчать",
    "мурлыкнуть",
    "тявкнуть",
    "пырк",
    "шмяк",
    "чмяк",
    "бум",
    "плюх",
    "хлюп",
    "поморщиться",
    "покоситься",
    "пялиться",
    "уставиться",
    "оценить",
    "окинуть",
    "проигнорировать",
    "отмахнуться",
    "отвернуться",
    "огрызнуться",
    "буркнуть",
    "пробормотать",
    "прошептать",
    "прокричать",
    "завопить",
    "визгнуть",
    "заикнуться",
    "изумиться",
    "удивить",
    "опешить",
    "поблагодарить",
    "попросить",
    "позвать",
    "игнорировать",
    "слушать",
]

_movement_and_actions = [
    "сесть",
    "присесть",
    "посидеть",
    "встать",
    "привстать",
    "лечь",
    "прилечь",
    "полежать",
    "похрустеть",
    "сделать",
    "стать",
    "делать",
    "дать",
    "передать",
    "взять",
    "забрать",
    "схватить",
    "хвать",
    "подергать",
    "дернуть",
    "дергать",
    "тянуть",
    "потянуть",
    "оставить",
    "посмотреть",
    "смотреть",
    "отправить",
    "открыть",
    "записать",
    "предложить",
    "пригласить",
    "снять",
    "медленно",
    "быстро",
    "ускориться",
    "замедлиться",
    "подпрыгнуть",
    "спрыгнуть",
    "запрыгнуть",
    "перепрыгнуть",
    "убежать",
    "улизнуть",
    "смыться",
    "поползти",
    "приползти",
    "подползти",
    "уползти",
    "прокрасться",
    "подкрасться",
    "напасть",
    "наброситься",
    "прыгнуть",
    "шмыгнуть",
    "увернуться",
    "уклониться",
    "оглянуться",
    "повернуться",
    "нагнуться",
    "наклониться",
    "откинуться",
    "развалиться",
    "растянуться",
    "подбежать",
    "подлететь",
    "влететь",
    "ворваться",
    "скрыться",
    "ускользнуть",
    "спрятать",
    "закутать",
]

INSTANT_ACTIONS = {
    "застрелиться": "💀",
    "бухнуть": "🍻",
    "порезаться": "🩸",
    "упасть": "💥",
    "зевнуть": "🥱",
    "заплакать": "💧",
    "заснуть": "💤",
}

ACTIONS_DICT = {}
for w in _hugs_and_touch:
    ACTIONS_DICT[w] = ("🤗", "🫂")
for w in _kisses_and_love:
    ACTIONS_DICT[w] = ("💋", "💖")
for w in _explicit_actions:
    ACTIONS_DICT[w] = ("🔥", "❤️‍🔥")
for w in _bites_and_scratches:
    ACTIONS_DICT[w] = ("🐾", "✨")
for w in _hits_and_fights:
    ACTIONS_DICT[w] = ("👊", "💥")
for w in _kills_and_dangers:
    if w not in INSTANT_ACTIONS:
        ACTIONS_DICT[w] = ("💀", "⚰️")
for w in _food_and_drink:
    if w not in INSTANT_ACTIONS:
        ACTIONS_DICT[w] = ("🍕", "🥂")
for w in _emotions_and_sounds:
    if w not in INSTANT_ACTIONS:
        ACTIONS_DICT[w] = ("💬", "💫")
for w in _movement_and_actions:
    ACTIONS_DICT[w] = ("👣", "⚡")

STORAGE = {}
DECLINED_STORAGE = {}
STATS = {"total_accepted": 0, "actions_usage": {}}
MARRIAGES = {}
BLACKLIST = {}
USER_NAME_TO_ID = {}


@router.message(CommandStart())
async def start_handler(message: Message):
    text = (
        "✨ <b>Доступные действия для ролевой игры:</b>\n\n"
        "⚡ <b>Мгновенные действия (без подтверждения):</b>\n"
        f"{', '.join(INSTANT_ACTIONS.keys())}\n\n"
        "🤗 <b>Обнимашки и касания:</b>\n"
        f"{', '.join(_hugs_and_touch)}\n\n"
        "💋 <b>Любовь и романтика:</b>\n"
        f"{', '.join(_kisses_and_love)}\n\n"
        "🔥 <b>Пикантное:</b>\n"
        f"{', '.join(_explicit_actions)}\n\n"
        "🐾 <b>Кусь и царапки:</b>\n"
        f"{', '.join(_bites_and_scratches)}\n\n"
        "👊 <b>Удары и драки:</b>\n"
        f"{', '.join(_hits_and_fights)}\n\n"
        "💀 <b>Опасно и жестко:</b>\n"
        f"{', '.join(_kills_and_dangers)}\n\n"
        "🍕 <b>Еда и напитки:</b>\n"
        f"{', '.join(_food_and_drink)}\n\n"
        "💬 <b>Эмоции и звуки:</b>\n"
        f"{', '.join(_emotions_and_sounds)}\n\n"
        "👣 <b>Движения:</b>\n"
        f"{', '.join(_movement_and_actions)}\n\n"
        "💍 <b>Браки:</b> Используйте /marry в ответ на сообщение партнера, а /divorce для расторжения.\n"
        "🚫 <b>Черный список:</b> /block и /unblock по юзернейму.\n"
        "📊 <b>Статистика:</b> /stats\n\n"
        "💡 <i>Инлайн-режим: введите @ваш_бот действие [цель/текст]</i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@router.message(Command("stats"))
async def stats_handler(message: Message):
    total = STATS["total_accepted"]
    usage = STATS["actions_usage"]
    top_actions = sorted(usage.items(), key=lambda x: x[1], reverse=True)[:5]
    top_text = (
        "\n".join([f"• <code>{act}</code> — {cnt} раз(а)" for act, cnt in top_actions])
        if top_actions
        else "Пока нет данных"
    )

    await message.answer(
        f"📊 <b>Статистика бота:</b>\n\n"
        f"✅ Успешно выполненных действий: <b>{total}</b>\n\n"
        f"🏆 <b>Топ-5 популярных действий:</b>\n{top_text}",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("marry"))
async def marry_handler(message: Message):
    user_id = message.from_user.id
    if not message.reply_to_message:
        await message.reply("💍 Ответьте на сообщение пользователя, с которым хотите пожениться!")
        return

    partner_id = message.reply_to_message.from_user.id
    partner_name = message.reply_to_message.from_user.first_name

    if user_id == partner_id:
        await message.reply("💍 Нельзя пожениться на самом себе!")
        return

    if user_id in MARRIAGES or partner_id in MARRIAGES:
        await message.reply("💍 Кто-то из вас уже состоит в браке!")
        return

    MARRIAGES[user_id] = partner_id
    MARRIAGES[partner_id] = user_id

    await message.answer(
        f"💍 <b>Поздравляем!</b> <b>{message.from_user.first_name}</b> и <b>{partner_name}</b> теперь официально в браке! ❤️",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("divorce"))
async def divorce_handler(message: Message):
    user_id = message.from_user.id
    if user_id not in MARRIAGES:
        await message.reply("💔 Вы и так не состоите в браке.")
        return

    partner_id = MARRIAGES[user_id]
    del MARRIAGES[user_id]
    if partner_id in MARRIAGES:
        del MARRIAGES[partner_id]

    await message.reply("💔 Вы успешно развелись и разорвали брак.")


@router.message(Command("block"))
async def block_handler(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("🚫 Укажите юзернейм для блокировки, например: /block @username")
        return

    target_username = args[1].lstrip("@").lower()
    target_id = USER_NAME_TO_ID.get(target_username)

    if not target_id:
        await message.reply("🚫 Пользователь не найден в кеше бота.")
        return

    user_id = message.from_user.id
    if user_id not in BLACKLIST:
        BLACKLIST[user_id] = set()

    BLACKLIST[user_id].add(target_id)
    await message.reply(f"🚫 Пользователь @{target_username} добавлен в ваш черный список.")


@router.message(Command("unblock"))
async def unblock_handler(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("✅ Укажите юзернейм для разблокировки, например: /unblock @username")
        return

    target_username = args[1].lstrip("@").lower()
    target_id = USER_NAME_TO_ID.get(target_username)

    user_id = message.from_user.id
    if user_id in BLACKLIST and target_id in BLACKLIST[user_id]:
        BLACKLIST[user_id].remove(target_id)
        await message.reply(f"✅ Пользователь @{target_username} удален из черного списка.")
    else:
        await message.reply("⚠️ Пользователь не найден в вашем черном списке.")


@router.message(F.text.lower() == "!принудить")
async def force_action_handler(message: Message):
    if not message.reply_to_message:
        return

    msg_id = message.reply_to_message.message_id
    data = DECLINED_STORAGE.get(msg_id)

    if not data:
        return

    if message.from_user.id != data["sender_id"]:
        await message.reply("⚠️ Принудить к действию может только тот, кто его отправил!")
        return

    sender_name = data["sender_name"]
    target_name = data["target_name"]
    action_text = data["action_text"]
    accepted_emoji = data["accepted_emoji"]

    updated_text = f"⚡ <b>{sender_name}</b> принудительно совершил(а) действие над <b>{target_name}</b>: {action_text} {accepted_emoji}"

    try:
        if data.get("inline_message_id"):
            await message.bot.edit_message_text(
                inline_message_id=data["inline_message_id"],
                text=updated_text, 
                parse_mode=ParseMode.HTML, 
                reply_markup=None
            )
        else:
            await message.reply_to_message.edit_text(
                text=updated_text, 
                parse_mode=ParseMode.HTML, 
                reply_markup=None
            )
    except Exception as e:
        print(f"Ошибка в force_action_handler: {e}")

    STATS["total_accepted"] += 1
    base_action = data["base_action"]
    STATS["actions_usage"][base_action] = STATS["actions_usage"].get(base_action, 0) + 1

    del DECLINED_STORAGE[msg_id]
    if msg_id in STORAGE:
        del STORAGE[msg_id]


@router.inline_query()
async def inline_rp_handler(query: InlineQuery):
    user_id = query.from_user.id
    if query.from_user.username:
        USER_NAME_TO_ID[query.from_user.username.lower()] = user_id

    text = query.query.strip()
    results = []

    if not text:
        article = InlineQueryResultArticle(
            id="empty",
            title="Введите действие...",
            description="Пример: поцеловать @username или застрелиться",
            input_message_content=InputTextMessageContent(
                message_text="✨ Напишите действие после юзернейма бота!"
            ),
        )
        await query.answer([article], cache_time=1)
        return

    words = text.split()
    first_word = words[0].lower() if words else ""
    rest_of_words = words[1:] if len(words) > 1 else []

    for word in rest_of_words:
        if word.startswith("@"):
            target_uname = word.lstrip("@").lower()
            target_id = USER_NAME_TO_ID.get(target_uname)
            if target_id and target_id in BLACKLIST and user_id in BLACKLIST[target_id]:
                article = InlineQueryResultArticle(
                    id="blocked",
                    title="🚫 Ошибка отправки",
                    description="Этот пользователь добавил вас в черный список!",
                    input_message_content=InputTextMessageContent(
                        message_text="🚫 Вы не можете отправлять запросы этому пользователю."
                    ),
                )
                await query.answer([article], cache_time=1)
                return

    if first_word in INSTANT_ACTIONS:
        emoji = INSTANT_ACTIONS[first_word]
        sender_name = query.from_user.first_name

        message_content = InputTextMessageContent(
            message_text=f"{emoji} <b>{sender_name}</b> решил(а) {first_word}",
            parse_mode=ParseMode.HTML,
        )
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4())[:8],
                title=f"{emoji} {first_word.capitalize()}",
                description="Мгновенное действие (без подтверждения)",
                input_message_content=message_content,
            )
        )
        await query.answer(results, cache_time=1, is_personal=True)
        return

    all_actions = list(ACTIONS_DICT.keys())
    matches = difflib.get_close_matches(first_word, all_actions, n=3, cutoff=0.3)

    if first_word in all_actions and first_word not in matches:
        matches.insert(0, first_word)
        matches = matches[:3]

    if not matches:
        article = InlineQueryResultArticle(
            id="error",
            title="❌ Неизвестное действие",
            description="Такого действия нет в списке!",
            input_message_content=InputTextMessageContent(
                message_text="❌ Ошибка: такого действия нет в списке разрешенных команд."
            ),
        )
        await query.answer([article], cache_time=1)
        return

    for match in matches:
        initial_emoji, accepted_emoji = ACTIONS_DICT[match]
        suggested_text = match + (" " + " ".join(rest_of_words) if rest_of_words else "")

        action_id = str(uuid.uuid4())[:8]
        sender_name = query.from_user.first_name

        STORAGE[action_id] = {
            "sender_name": sender_name,
            "sender_id": user_id,
            "base_action": match,
            "full_text": suggested_text,
            "accepted_emoji": accepted_emoji,
        }

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text="Принять", callback_data=f"accept_{action_id}"),
                InlineKeyboardButton(text="Отказаться", callback_data=f"decline_{action_id}"),
            ]]
        )

        message_content = InputTextMessageContent(
            message_text=f"{initial_emoji} <b>{sender_name}</b> хочет {suggested_text}",
            parse_mode=ParseMode.HTML,
        )

        results.append(
            InlineQueryResultArticle(
                id=action_id,
                title=f"{initial_emoji} {suggested_text.capitalize()}",
                description=f"Предложить собеседнику {suggested_text}",
                input_message_content=message_content,
                reply_markup=keyboard,
            )
        )

    await query.answer(results, cache_time=1, is_personal=True)


@router.callback_query(F.data.startswith("accept_"))
async def accept_callback(callback: CallbackQuery):
    action_id = callback.data.split("_")[1]
    data = STORAGE.get(action_id)

    if not data:
        await callback.answer("Срок действия запроса истёк или бот перезапускался.", show_alert=True)
        return

    if callback.from_user.id == data["sender_id"]:
        await callback.answer("Вы не можете принять собственное действие!", show_alert=True)
        return

    sender_name = data["sender_name"]
    full_text = data["full_text"]
    accepted_emoji = data["accepted_emoji"]
    base_action = data["base_action"]

    STATS["total_accepted"] += 1
    STATS["actions_usage"][base_action] = STATS["actions_usage"].get(base_action, 0) + 1

    updated_text = f"{accepted_emoji} <b>{sender_name}</b> {full_text}"

    try:
        if callback.inline_message_id:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=updated_text,
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
        else:
            await callback.message.edit_text(
                text=updated_text,
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
        await callback.answer("Действие принято! ❤️")
    except Exception as e:
        print(f"Ошибка в accept_callback: {e}")
        await callback.answer("Произошла ошибка при обновлении сообщения.", show_alert=True)
    
    STORAGE.pop(action_id, None)


@router.callback_query(F.data.startswith("decline_"))
async def decline_callback(callback: CallbackQuery):
    action_id = callback.data.split("_")[1]
    data = STORAGE.get(action_id)

    if not data:
        await callback.answer("Срок действия запроса истёк или бот перезапускался.", show_alert=True)
        return

    if callback.from_user.id == data["sender_id"]:
        await callback.answer("Вы не можете отклонить собственное действие!", show_alert=True)
        return

    sender_name = data["sender_name"]
    target_name = callback.from_user.first_name
    
    storage_key = callback.message.message_id if callback.message else action_id

    DECLINED_STORAGE[storage_key] = {
        "sender_id": data["sender_id"],
        "sender_name": sender_name,
        "target_name": target_name,
        "action_text": data["full_text"],
        "accepted_emoji": data["accepted_emoji"],
        "base_action": data["base_action"],
        "inline_message_id": callback.inline_message_id,
    }

    updated_text = (
        f"💔 <b>{sender_name}</b> попытался совершить действие, но <b>{target_name}</b> отказался(-ась)."
    )

    try:
        if callback.inline_message_id:
            await callback.bot.edit_message_text(
                inline_message_id=callback.inline_message_id,
                text=updated_text,
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
        else:
            await callback.message.edit_text(
                text=updated_text,
                parse_mode=ParseMode.HTML,
                reply_markup=None
            )
        await callback.answer("Действие отклонено.")
    except Exception as e:
        print(f"Ошибка в decline_callback: {e}")
        await callback.answer("Произошла ошибка при обновлении сообщения.", show_alert=True)

    STORAGE.pop(action_id, None)


async def handle(request):
    return web.Response(text="Bot is alive!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    
    await start_web_server()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
