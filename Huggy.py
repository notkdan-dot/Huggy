import asyncio
import difflib
import os
import random
import sqlite3
import uuid
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    ChosenInlineResult,
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

# Поддержка Render Disk для сохранения базы данных при перезагрузках
if os.path.exists("/data") or os.environ.get("RENDER"):
    os.makedirs("/data", exist_ok=True)
    DB_FILE = "/data/bot_data.db"
else:
    DB_FILE = "bot_data.db"

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS marriages (
        user_id INTEGER PRIMARY KEY,
        partner_id INTEGER,
        partner_name TEXT
    )
""")
# Глобальные таблицы статистики для инлайн-режима
cursor.execute("""
    CREATE TABLE IF NOT EXISTS global_totals (
        id INTEGER PRIMARY KEY,
        total_accepted INTEGER
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS global_actions (
        action TEXT PRIMARY KEY,
        count INTEGER
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS blacklist (
        user_id INTEGER,
        blocked_id INTEGER,
        PRIMARY KEY (user_id, blocked_id)
    )
""")
conn.commit()

_hugs_and_touch = [
    "обнять", "прижать", "погладить", "гладь", "поглаживать", "массировать",
    "помассировать", "погреть", "согреть", "потрогать", "трогать", "помацать",
    "пожмякать", "мацать", "жмякать", "потискать", "затискать", "прильнуть",
    "ластиться", "млеть", "таять", "уткнуться", "прислониться", "притулиться",
    "потереться", "укрыть", "укутать", "окутать", "успокоить", "поддержать",
    "причесать", "перевязать", "пожать", "положить",
]

_kisses_and_love = [
    "поцеловать", "разцеловать", "цемнуть", "чмокнуть", "отчмокать", "зацеловать",
    "ласкать", "обласкать", "подарить", "поздравить", "пожелать", "извиниться", "похвалить",
]

_explicit_actions = [
    "засосать", "трахнуть", "оттрахать", "изнасиловать", "иметь", "отиметь",
    "отшлифовать", "трахать", "ебать", "выебать", "отсосать", "отлизать",
    "отполировать", "полировать", "отминенить", "ссосать", "высосать", "раздеть",
    "осеменить", "оплодотворить",
]

_bites_and_scratches = [
    "щекотать", "пощекотать", "укусить", "лизь", "лизнуть", "облизать", "вылизать",
    "полизать", "подлизать", "кусь", "куснуть", "покусать", "погрызть", "загрызть",
    "цап", "цапнуть", "царап", "поцарапать", "оцарапать", "исцарапать", "понюхать",
    "занюхнуть", "нюх-нюх", "подразнить", "дразнить", "хыть-хыть",
]

_hits_and_fights = [
    "наказать", "шлеп", "шлепнуть", "шлепать", "отшлепать", "выпороть", "хлопнуть",
    "отхлопать", "хлопать", "ущипнуть", "щипать", "пощипать", "пихнуть", "толкнуть",
    "швырнуть", "бросить", "кинуть", "запульнуть", "запустить", "треснуть",
    "трепать", "потрепать", "взъерошить", "опрокинуть", "сбить", "повалить",
    "скрутить", "связать", "обезоружить", "отобрать", "выбить", "сдернуть",
    "сорвать", "ударить", "уебать", "ебануть", "долбануть", "ушатать", "порвать",
    "въебать", "разъебать", "пнуть", "попинать",
]

_kills_and_dangers = [
    "застрелить", "расстрелять", "отстрелить", "стрельнуть", "шмальнуть", "сжечь", 
    "поджечь", "убить", "уничтожить", "унизить", "арестовать", "оторвать", "отрубить", 
    "отъебать", "отрезать", "порезать", "резать", "закопать", "выкопать", "взорвать", 
    "подорвать", "заминировать", "кастрировать", "послать",
]

_food_and_drink = [
    "покормить", "покушать", "поесть", "есть", "кушать", "пить", "попить",
    "выпить", "попоить", "хрум", "хрумкать", "хрустнуть",
]

_emotions_and_sounds = [
    "орать", "наорать", "рассмешить", "рассказать", "улыбнуться", "засмеяться",
    "ухмыльнуться", "нахмуриться", "закатить", "вздохнуть",
    "кивнуть", "покачать", "подмигнуть", "помахать", "показать", "постучать",
    "указать", "ткнуть", "поделиться", "фырк", "фыркнуть", "хмык", "хмыкнуть",
    "мур", "мурчать", "мурлыкнуть", "тявкнуть", "пырк", "шмяк", "чмяк", "бум",
    "плюх", "хлюп", "поморщиться", "покоситься", "пялиться", "уставиться",
    "оценить", "окинуть", "проигнорировать", "отмахнуться", "отвернуться",
    "огрызнуться", "буркнуть", "пробормотать", "прошептать", "прокричать",
    "завопить", "визгнуть", "заикнуться", "изумиться", "удивить", "опешить",
    "поблагодарить", "попросить", "позвать", "игнорировать", "слушать",
]

_movement_and_actions = [
    "сесть", "присесть", "посидеть", "встать", "привстать", "лечь", "прилечь",
    "полежать", "похрустеть", "сделать", "стать", "делать", "дать", "передать",
    "взять", "забрать", "схватить", "хвать", "подергать", "дернуть", "дергать",
    "тянуть", "потянуть", "оставить", "посмотреть", "смотреть", "отправить",
    "открыть", "записать", "предложить", "пригласить", "снять", "медленно",
    "быстро", "ускориться", "замедлиться", "подпрыгнуть", "спрыгнуть",
    "запрыгнуть", "перепрыгнуть", "смыться", "поползти",
    "приползти", "подползти", "уползти", "прокрасться", "подкрасться", "напасть",
    "наброситься", "прыгнуть", "шмыгнуть", "увернуться", "уклониться",
    "оглянуться", "повернуться", "нагнуться", "наклониться", "откинуться",
    "развалиться", "растянуться", "подбежать", "подлететь", "влететь",
    "ворваться", "скрыться", "ускользнуть", "спрятать", "закутать",
]

INSTANT_ACTIONS = {
    "застрелиться": "💀",
    "застрелиться_я": "💀",
    "бухнуть": "🍻",
    "порезаться": "🩸",
    "упасть": "💥",
    "зевнуть": "🥱",
    "заплакать": "💧",
    "заснуть": "💤",
}

ATTEMPT_ACTIONS = [
    "улизнуть", "ускользнуть", "смыться", "убежать", "увернуться", "уклониться", "спрятаться"
]

ACTIONS_DICT = {}
for w in _hugs_and_touch: ACTIONS_DICT[w] = ("🤗", "🫂")
for w in _kisses_and_love: ACTIONS_DICT[w] = ("💋", "💖")
for w in _explicit_actions: ACTIONS_DICT[w] = ("🔥", "❤️‍🔥")
for w in _bites_and_scratches: ACTIONS_DICT[w] = ("🐾", "✨")
for w in _hits_and_fights: ACTIONS_DICT[w] = ("👊", "💥")
for w in _kills_and_dangers:
    if w not in INSTANT_ACTIONS: ACTIONS_DICT[w] = ("💀", "⚰️")
for w in _food_and_drink:
    if w not in INSTANT_ACTIONS: ACTIONS_DICT[w] = ("🍕", "🥂")
for w in _emotions_and_sounds:
    if w not in INSTANT_ACTIONS: ACTIONS_DICT[w] = ("💬", "💫")
for w in _movement_and_actions:
    if w not in ATTEMPT_ACTIONS: ACTIONS_DICT[w] = ("👣", "⚡")

STORAGE = {}
DECLINED_STORAGE = {}
MARRY_STORAGE = {}
ATTEMPT_TASKS_DATA = {}
USER_NAME_TO_ID = {}


def get_past_form(verb: str) -> str:
    verb = verb.lower().strip()
    irregulars = {
        "сесть": "сел(-а)", "встать": "встал(-а)", "привстать": "привстал(-а)",
        "лечь": "лег(-ла)", "прилечь": "прилег(-ла)", "полежать": "полежал(-а)",
        "дать": "дал(-а)", "взять": "взял(-а)", "забрать": "забрал(-а)",
        "схватить": "схватил(-а)", "напасть": "напал(-а)", "наброситься": "набросился(-ась)",
        "убить": "убил(-а)", "упасть": "упал(-а)", "заплакать": "заплакал(-а)",
        "засмеяться": "засмеялся(-ась)", "улыбнуться": "улыбнулся(-ась)",
        "нахмуриться": "нахмурился(-ась)", "вздохнуть": "вздохнул(-а)",
        "зевнуть": "зевнул(-а)", "кивнуть": "кивнул(-а)", "подмигнуть": "подмигнул(-а)",
        "помахать": "помахал(-а)", "постучать": "постучал(-а)", "ткнуть": "ткнул(-а)",
        "фыркнуть": "фыркнул(-а)", "хмыкнуть": "хмыкнул(-а)", "мурчать": "мурчал(-а)",
        "мурлыкнуть": "мурлыкнул(-а)", "тявкнуть": "тявкнул(-а)", "поморщиться": "поморщился(-ась)",
        "покоситься": "покосился(-ась)", "огрызнуться": "огрызнулся(-ась)",
        "буркнуть": "буркнул(-а)", "пробормотать": "пробормотал(-а)", "прошептать": "прошептал(-а)",
        "прокричать": "прокричал(-а)", "завопить": "завопил(-а)", "визгнуть": "визгнул(-а)",
        "заикнуться": "заикнулся(-ась)", "изумиться": "изумился(-ась)", "опешить": "опешил(-а)",
        "поблагодарить": "поблагодарил(-а)", "попросить": "попросил(-а)", "позвать": "позвал(-а)",
        "слушать": "слушал(-а)", "улизнуть": "улизнул(-а)", "ускользнуть": "ускользнул(-а)",
        "смыться": "смылся(-ась)", "убежать": "убежал(-а)", "увернуться": "увернулся(-ась)",
        "уклониться": "уклонился(-ась)", "спрятаться": "спрятался(-ась)"
    }
    if verb in irregulars:
        return irregulars[verb]
    
    if verb.endswith("ться") or verb.endswith("тись"):
        return verb[:-4] + "лся(-ась)"
    elif verb.endswith("ть"):
        return verb[:-2] + "л(-а)"
    elif verb.endswith("ти"):
        return verb[:-2] + "л(-а)"
    elif verb.endswith("чь"):
        return verb[:-2] + "г(-ла)"
        
    return verb + "л(-а)"


@router.message(CommandStart())
async def start_handler(message: Message):
    text = (
        "✨ <b>Добро пожаловать в ролевой бот!</b>\n\n"
        "💍 <b>Команды браков:</b>\n"
        "• /marry — сделать предложение (в ответ на сообщение)\n"
        "• /divorce — расторгнуть брак\n\n"
        "📊 <b>Статистика и черный список:</b>\n"
        "• /stats — посмотреть общую статистику\n"
        "• /block @user — заблокировать пользователя\n"
        "• /unblock @user — разблокировать пользователя\n"
        "• <code>!принудить</code> — ответить на отклоненное действие\n\n"
        "⚡ <b>Мгновенные действия:</b>\n"
        f"• {', '.join(INSTANT_ACTIONS.keys())}\n\n"
        "🎲 <b>Попытки (шанс 50/50 с анимацией):</b>\n"
        f"• {', '.join(ATTEMPT_ACTIONS)}\n\n"
        "🤗 <b>Обнимашки и касания:</b>\n"
        f"• {', '.join(_hugs_and_touch[:15])} и др.\n\n"
        "💋 <b>Любовь и романтика:</b>\n"
        f"• {', '.join(_kisses_and_love)}\n\n"
        "🔥 <b>Эротические действия:</b>\n"
        f"• {', '.join(_explicit_actions[:12])} и др.\n\n"
        "🐾 <b>Укусы и царапины:</b>\n"
        f"• {', '.join(_bites_and_scratches[:12])} и др.\n\n"
        "👊 <b>Драки и удары:</b>\n"
        f"• {', '.join(_hits_and_fights[:15])} и др.\n\n"
        "💀 <b>Оружие и опасности:</b>\n"
        f"• {', '.join(_kills_and_dangers[:12])} и др.\n\n"
        "🍕 <b>Еда и напитки:</b>\n"
        f"• {', '.join(_food_and_drink)}\n\n"
        "💬 <b>Эмоции и звуки:</b>\n"
        f"• {', '.join(_emotions_and_sounds[:12])} и др.\n\n"
        "👣 <b>Движения и действия:</b>\n"
        f"• {', '.join(_movement_and_actions[:12])} и др.\n\n"
        "💡 <i>Инлайн-режим: введите в любом чате <code>@ваш_бот [действие] [цель/текст]</code></i>"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)


@router.message(Command("stats"))
async def stats_handler(message: Message):
    cursor.execute("SELECT total_accepted FROM global_totals WHERE id = 1")
    row = cursor.fetchone()
    total = row[0] if row else 0

    cursor.execute("SELECT action, count FROM global_actions ORDER BY count DESC LIMIT 5")
    top_actions = cursor.fetchall()
    
    top_text = (
        "\n".join([f"• <code>{act}</code> — {cnt} раз(а)" for act, cnt in top_actions])
        if top_actions
        else "Пока нет данных"
    )

    user_id = message.from_user.id
    cursor.execute("SELECT partner_name FROM marriages WHERE user_id = ?", (user_id,))
    marriage_row = cursor.fetchone()
    if marriage_row:
        marriage_text = f"Состоит в браке с <b>{marriage_row[0]}</b> ❤️"
    else:
        marriage_text = "Не состоит в браке 💔"

    await message.answer(
        f"📊 <b>Глобальная статистика бота:</b>\n\n"
        f"💍 Ваш статус: {marriage_text}\n"
        f"✅ Всего успешных действий: <b>{total}</b>\n\n"
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

    cursor.execute("SELECT user_id FROM marriages WHERE user_id = ? OR partner_id = ?", (user_id, user_id))
    user_married = cursor.fetchone()
    cursor.execute("SELECT user_id FROM marriages WHERE user_id = ? OR partner_id = ?", (partner_id, partner_id))
    partner_married = cursor.fetchone()

    if user_married or partner_married:
        await message.reply("💍 Кто-то из вас уже состоит в браке!")
        return

    proposal_id = str(uuid.uuid4())[:8]
    MARRY_STORAGE[proposal_id] = {
        "user_id": user_id,
        "partner_id": partner_id,
        "user_name": message.from_user.first_name,
        "partner_name": partner_name,
    }

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Принять ❤️", callback_data=f"marryaccept_{proposal_id}"),
            InlineKeyboardButton(text="Отклонить 💔", callback_data=f"marrydecline_{proposal_id}"),
        ]]
    )

    await message.answer(
        f"💍 <b>{message.from_user.first_name}</b> делает предложение руки и сердца <b>{partner_name}</b>!\nПринимаете предложение?",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )


@router.callback_query(F.data.startswith("marryaccept_"))
async def marry_accept_callback(callback: CallbackQuery):
    proposal_id = callback.data.split("_")[1]
    data = MARRY_STORAGE.get(proposal_id)

    if not data:
        await callback.answer("Срок действия предложения истёк.", show_alert=True)
        return

    if callback.from_user.id != data["partner_id"]:
        await callback.answer("Это предложение адресовано не вам!", show_alert=True)
        return

    user_id = data["user_id"]
    partner_id = data["partner_id"]

    cursor.execute("SELECT user_id FROM marriages WHERE user_id = ? OR partner_id = ? OR user_id = ? OR partner_id = ?", (user_id, user_id, partner_id, partner_id))
    if cursor.fetchone():
        await callback.answer("Кто-то из вас уже состоит в браке!", show_alert=True)
        return

    cursor.execute("INSERT OR REPLACE INTO marriages (user_id, partner_id, partner_name) VALUES (?, ?, ?)", (user_id, partner_id, data["partner_name"]))
    cursor.execute("INSERT OR REPLACE INTO marriages (user_id, partner_id, partner_name) VALUES (?, ?, ?)", (partner_id, user_id, data["user_name"]))
    conn.commit()

    await callback.message.edit_text(
        f"💍 <b>Поздравляем!</b> <b>{data['user_name']}</b> и <b>{data['partner_name']}</b> теперь официально в браке! ❤️",
        parse_mode=ParseMode.HTML
    )
    MARRY_STORAGE.pop(proposal_id, None)
    await callback.answer("Вы приняли предложение! 💍")


@router.callback_query(F.data.startswith("marrydecline_"))
async def marry_decline_callback(callback: CallbackQuery):
    proposal_id = callback.data.split("_")[1]
    data = MARRY_STORAGE.get(proposal_id)

    if not data:
        await callback.answer("Срок действия предложения истёк.", show_alert=True)
        return

    if callback.from_user.id != data["partner_id"]:
        await callback.answer("Это предложение адресовано не вам!", show_alert=True)
        return

    await callback.message.edit_text(
        f"💔 <b>{data['partner_name']}</b> отклонил(-а) предложение руки и сердца от <b>{data['user_name']}</b>.",
        parse_mode=ParseMode.HTML
    )
    MARRY_STORAGE.pop(proposal_id, None)
    await callback.answer("Предложение отклонено.")


@router.message(Command("divorce"))
async def divorce_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT partner_id FROM marriages WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        await message.reply("💔 Вы и так не состоите в браке.")
        return

    partner_id = row[0]
    cursor.execute("DELETE FROM marriages WHERE user_id = ? OR user_id = ?", (user_id, partner_id))
    conn.commit()

    await message.reply("💔 Вы успешно развелись и разорвали брак.")


@router.message(Command("block"))
async def block_handler(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("🚫 Укажите юзернейм, например: /block @username")
        return

    target_username = args[1].lstrip("@").lower()
    target_id = USER_NAME_TO_ID.get(target_username)

    if not target_id:
        await message.reply("🚫 Пользователь не найден в кеше бота.")
        return

    user_id = message.from_user.id
    cursor.execute("INSERT OR IGNORE INTO blacklist (user_id, blocked_id) VALUES (?, ?)", (user_id, target_id))
    conn.commit()
    await message.reply(f"🚫 Пользователь @{target_username} добавлен в ваш черный список.")


@router.message(Command("unblock"))
async def unblock_handler(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.reply("✅ Укажите юзернейм, например: /unblock @username")
        return

    target_username = args[1].lstrip("@").lower()
    target_id = USER_NAME_TO_ID.get(target_username)

    user_id = message.from_user.id
    cursor.execute("DELETE FROM blacklist WHERE user_id = ? AND blocked_id = ?", (user_id, target_id))
    conn.commit()
    await message.reply(f"✅ Пользователь @{target_username} удален из черного списка.")


@router.message(F.text.lower() == "!принудить")
async def force_action_handler(message: Message):
    user_id = message.from_user.id
    data = DECLINED_STORAGE.get(user_id)

    if not data:
        await message.reply("⚠️ У вас нет отклоненных действий для принуждения!")
        return

    sender_name = data["sender_name"]
    base_action = data["base_action"]
    rest_of_text = data["rest_of_text"]
    accepted_emoji = data["accepted_emoji"]

    past_verb = get_past_form(base_action)
    updated_text = f"⚡ <b>{sender_name}</b> принудительно {past_verb} {rest_of_text} {accepted_emoji}".strip()

    # Обновляем глобальную статистику
    cursor.execute("INSERT INTO global_totals (id, total_accepted) VALUES (1, 1) ON CONFLICT(id) DO UPDATE SET total_accepted = total_accepted + 1")
    cursor.execute("INSERT INTO global_actions (action, count) VALUES (?, 1) ON CONFLICT(action) DO UPDATE SET count = count + 1", (base_action,))
    conn.commit()

    try:
        if data.get("inline_message_id"):
            await message.bot.edit_message_text(
                inline_message_id=data["inline_message_id"],
                text=updated_text, 
                parse_mode=ParseMode.HTML, 
                reply_markup=None
            )
        elif data.get("chat_id") and data.get("message_id"):
            await message.bot.edit_message_text(
                chat_id=data["chat_id"],
                message_id=data["message_id"],
                text=updated_text, 
                parse_mode=ParseMode.HTML, 
                reply_markup=None
            )
    except Exception as e:
        print(f"Ошибка в force_action_handler: {e}")

    DECLINED_STORAGE.pop(user_id, None)


async def run_attempt_animation(bot, inline_msg_id, data):
    sender_name = data["sender_name"]
    action = data["base_action"]
    rest = data["rest_of_text"]
    
    base_phrase = f"⚡ <b>{sender_name}</b> пытается {action}"
    if rest:
        base_phrase += f" {rest}"
        
    try:
        await bot.edit_message_text(
            inline_message_id=inline_msg_id,
            text=base_phrase + "...",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(1)
        await bot.edit_message_text(
            inline_message_id=inline_msg_id,
            text=base_phrase + "..",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(1)
        await bot.edit_message_text(
            inline_message_id=inline_msg_id,
            text=base_phrase + ".",
            parse_mode=ParseMode.HTML
        )
        await asyncio.sleep(1)
        
        success = random.choice([True, False])
        
        if success:
            past = get_past_form(action)
            final_text = f"✅ <b>{sender_name}</b> успешно {past}"
            if rest:
                final_text += f" {rest}"
        else:
            fail_verbs = {
                "улизнуть": "не смог(-ла) улизнуть",
                "ускользнуть": "не смог(-ла) ускользнуть",
                "смыться": "не смог(-ла) смыться",
                "убежать": "не смог(-ла) убежать",
                "увернуться": "не смог(-ла) увернуться",
                "уклониться": "не смог(-ла) уклониться",
                "спрятаться": "не смог(-ла) спрятаться"
            }
            fail_msg = fail_verbs.get(action, f"не смог(-ла) {action}")
            final_text = f"❌ <b>{sender_name}</b> {fail_msg}"
            if rest:
                final_text += f" {rest}"
                
        await bot.edit_message_text(
            inline_message_id=inline_msg_id,
            text=final_text,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        print(f"Animation error (убедитесь, что Inline Feedback включен в BotFather): {e}")


@router.chosen_inline_result()
async def chosen_inline_handler(chosen: ChosenInlineResult):
    result_id = chosen.result_id
    if result_id in ATTEMPT_TASKS_DATA:
        data = ATTEMPT_TASKS_DATA[result_id]
        inline_msg_id = chosen.inline_message_id
        if inline_msg_id:
            asyncio.create_task(run_attempt_animation(chosen.bot, inline_msg_id, data))


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
            description="Пример: поцеловать @username или улизнуть",
            input_message_content=InputTextMessageContent(
                message_text="✨ Напишите действие после юзернейма бота!"
            ),
        )
        await query.answer([article], cache_time=1)
        return

    words = text.split()
    first_word = words[0].lower() if words else ""
    rest_of_words = words[1:] if len(words) > 1 else []
    rest_text_str = " ".join(rest_of_words) if rest_of_words else ""

    for word in rest_of_words:
        if word.startswith("@"):
            target_uname = word.lstrip("@").lower()
            target_id = USER_NAME_TO_ID.get(target_uname)
            if target_id:
                cursor.execute("SELECT 1 FROM blacklist WHERE user_id = ? AND blocked_id = ?", (target_id, user_id))
                if cursor.fetchone():
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
        
        msg_text = f"{emoji} <b>{sender_name}</b> решил(а) {first_word}"
        if rest_text_str:
            msg_text += f" {rest_text_str}"

        message_content = InputTextMessageContent(
            message_text=msg_text,
            parse_mode=ParseMode.HTML,
        )
        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4())[:8],
                title=f"{emoji} {first_word.capitalize()} {rest_text_str}".strip(),
                description="Мгновенное действие",
                input_message_content=message_content,
            )
        )
        await query.answer(results, cache_time=1, is_personal=True)
        return

    if first_word in ATTEMPT_ACTIONS:
        sender_name = query.from_user.first_name
        action_id = str(uuid.uuid4())[:8]
        
        ATTEMPT_TASKS_DATA[action_id] = {
            "sender_name": sender_name,
            "base_action": first_word,
            "rest_of_text": rest_text_str
        }
        
        initial_display = f"⚡ <b>{sender_name}</b> пытается {first_word}"
        if rest_text_str:
            initial_display += f" {rest_text_str}"
        initial_display += "..."

        message_content = InputTextMessageContent(
            message_text=initial_display,
            parse_mode=ParseMode.HTML,
        )
        results.append(
            InlineQueryResultArticle(
                id=action_id,
                title=f"⚡ Попытка: {first_word.capitalize()} {rest_text_str}".strip(),
                description="Шанс 50 на 50 (с анимацией)",
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
        suggested_text = match + (" " + rest_text_str if rest_text_str else "")

        action_id = str(uuid.uuid4())[:8]
        sender_name = query.from_user.first_name

        STORAGE[action_id] = {
            "sender_name": sender_name,
            "sender_id": user_id,
            "base_action": match,
            "rest_of_text": rest_text_str,
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
    base_action = data["base_action"]
    rest_of_text = data["rest_of_text"]
    accepted_emoji = data["accepted_emoji"]

    past_verb = get_past_form(base_action)
    updated_text = f"{accepted_emoji} <b>{sender_name}</b> {past_verb} {rest_of_text}".strip()

    # Записываем в глобальную статистику
    cursor.execute("INSERT INTO global_totals (id, total_accepted) VALUES (1, 1) ON CONFLICT(id) DO UPDATE SET total_accepted = total_accepted + 1")
    cursor.execute("INSERT INTO global_actions (action, count) VALUES (?, 1) ON CONFLICT(action) DO UPDATE SET count = count + 1", (base_action,))
    conn.commit()

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
    sender_id = data["sender_id"]

    DECLINED_STORAGE[sender_id] = {
        "sender_id": sender_id,
        "sender_name": sender_name,
        "target_name": target_name,
        "base_action": data["base_action"],
        "rest_of_text": data["rest_of_text"],
        "accepted_emoji": data["accepted_emoji"],
        "inline_message_id": callback.inline_message_id,
        "chat_id": callback.message.chat.id if callback.message else None,
        "message_id": callback.message.message_id if callback.message else None,
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
