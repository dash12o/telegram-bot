# bot.py
# pip install aiogram aiosqlite
# python bot.py

import asyncio
import aiosqlite
import logging
import random
import string
import os
from typing import Optional, List
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command

# ====== CONFIG ======
API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8394181298:AAFLJykLt9D_FHcfK3fVtKi08u3OGUCehcA")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7526336529"))
DB_PATH = "bot_database.db"
INVITER_POINTS = 1
ADMIN_USERNAME = "@ii58n"
POINTS_WORD = "نقاط"
ENTRY_POINTS = 0
DEV_CONTACT = "@ii58n"

PROXY_URL = ""

logging.basicConfig(level=logging.INFO)

bot: Bot = None  # type: ignore
dp: Dispatcher = None  # type: ignore

user_pages: dict = {}
admin_pages: dict = {}
admin_prev_pages: dict = {}
admin_pending: dict = {}

# ================= TRANSLATIONS =================

TRANSLATIONS = {
    "ar": {
        "welcome": "👋 مرحباً بك في البوت!",
        "shop": "🛍️ المتجر",
        "profile": "👤 معلومات حسابك",
        "leaderboard": "المتصدرين",
        "collect_points": "💰 تجميع النقاط",
        "daily_gift": "🎁 هديّة يومية",
        "invite": "👥 دعوة أصدقاء",
        "help": "📖 المساعدة",
        "language": "🌐 اختر اللغة",
        "select_lang": "🌐 <b>اختر اللغة</b>",
        "arabic": "🇸🇦 العربية",
        "russian": "🇷🇺 الروسية",
        "lang_changed": "✅ تم تغيير اللغة إلى العربية!",
        "back": "🔙 القائمة الرئيسية",
        "back_shop": "🔙 رجوع للمتجر",
        "control_panel": "⚙️ لوحة الادمن",
        "stars": "نجوم تيليجرام",
        "play": "🎮 بطاقات Google Play",
        "all_products": "📦 كل المنتجات",
        "banned": "🚫 تم حظرك من استخدام البوت",
        "contact_admin": "للتواصل مع الإدارة",
        "buy_now": "✅ شراء الآن",
        "no_points": "🔒 تحتاج",
        "points": "نقطة",
        "store": "🛍️ المتجر",
        "my_points": "رصيدك",
        "choose_category": "📂 اختر قسم المنتجات",
        "my_account": "👤 معلومات حسابك",
        "statistics": "📊 الإحصائيات",
        "points_label": "النقاط",
        "rank": "🏅 الرتبة",
        "invited_friends": "👥 الأصدقاء المدعوين",
        "purchases": "🛒 عدد المشتريات",
        "leaderboard_title": "لوحة المتصدرين",
        "no_leaders": "📭 لا يوجد متصدرين بعد",
        "invite_friends": "👥 دعوة الأصدقاء",
        "invite_link": "🔗 رابط دعوتك",
        "daily_gift_title": "🎁 الهديّة اليومية",
        "get_gift": "✅ احصل على الهديّة",
        "gift_already_claimed": "⏰ تم استلام هديّتك اليومية بالفعل",
        "help_title": "📖 المساعدة",
        "how_it_works": "🤔 كيف يعمل البوت؟",
    },
    "ru": {
        "welcome": "👋 Добро пожаловать в бота!",
        "shop": "🛍️ Магазин",
        "profile": "👤 Мой профиль",
        "leaderboard": "Лидеры",
        "collect_points": "💰 Собрать очки",
        "daily_gift": "🎁 Ежедневный подарок",
        "invite": "👥 Пригласить друзей",
        "help": "📖 Помощь",
        "language": "🌐 Выберите язык",
        "select_lang": "🌐 <b>Выберите язык</b>",
        "arabic": "🇸🇦 Арабский",
        "russian": "🇷🇺 Русский",
        "lang_changed": "✅ Язык изменен на русский!",
        "back": "🔙 Главное меню",
        "back_shop": "🔙 Вернуться в магазин",
        "control_panel": "⚙️ Панель администратора",
        "stars": "Звезды Telegram",
        "play": "🎮 Карты Google Play",
        "all_products": "📦 Все продукты",
        "banned": "🚫 Вы заблокированы от использования бота",
        "contact_admin": "Чтобы связаться с администратором",
        "buy_now": "✅ Купить сейчас",
        "no_points": "🔒 Вам нужно",
        "points": "очков",
        "store": "🛍️ Магазин",
        "my_points": "Ваш баланс",
        "choose_category": "📂 Выберите категорию товаров",
        "my_account": "👤 Мой профиль",
        "statistics": "📊 Статистика",
        "points_label": "Очки",
        "rank": "🏅 Ранг",
        "invited_friends": "👥 Приглашенных друзей",
        "purchases": "🛒 Количество покупок",
        "leaderboard_title": "Таблица лидеров",
        "no_leaders": "📭 Лидеров пока нет",
        "invite_friends": "👥 Пригласить друзей",
        "invite_link": "🔗 Ваша ссылка приглашения",
        "daily_gift_title": "🎁 Ежедневный подарок",
        "get_gift": "✅ Получить подарок",
        "gift_already_claimed": "⏰ Вы уже получили подарок сегодня",
        "help_title": "📖 Помощь",
        "how_it_works": "🤔 Как это работает?",
    }
}


async def get_user_language(user_id: int, phone_language: Optional[str] = None) -> str:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT language FROM user_languages WHERE user_id=?", (user_id,))
            result = await cur.fetchone()
            if result:
                return result[0]
    except:
        pass
    
    if phone_language:
        if phone_language.startswith("ru"):
            return "ru"
        elif phone_language.startswith("ar"):
            return "ar"
    
    return "ar"


async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO user_languages(user_id, language) VALUES(?,?)", (user_id, language))
        await db.commit()


def get_text(key: str, language: str = "ar") -> str:
    return TRANSLATIONS.get(language, {}).get(key, TRANSLATIONS["ar"].get(key, key))


def get_product_name(name_ar: str, name_ru: str, language: str = "ar") -> str:
    if language == "ru" and name_ru:
        return name_ru
    return name_ar


async def get_points_word() -> str:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT value FROM settings WHERE key='points_word'")
            result = await cur.fetchone()
            return result[0] if result else "نقاط"
    except:
        return "نقاط"


async def set_points_word(word: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key, value) VALUES('points_word', ?)", (word,))
        await db.commit()


async def get_daily_gift_amount() -> int:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT value FROM settings WHERE key='daily_gift_amount'")
            result = await cur.fetchone()
            return int(result[0]) if result else 1
    except:
        return 1


async def set_daily_gift_amount(amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key, value) VALUES('daily_gift_amount', ?)", (str(amount),))
        await db.commit()


# ================= DECORATIONS =================


def create_header(title: str, emoji: str = "") -> str:
    line = "━" * 20
    return f"{emoji} <b>{title}</b> {emoji}\n{line}"


def create_box(content: str, style: str = "rounded") -> str:
    if style == "rounded":
        return f"╭{'─' * 28}╮\n{content}\n╰{'─' * 28}╯"
    elif style == "double":
        return f"╔{'═' * 28}╗\n{content}\n╚{'═' * 28}╝"
    else:
        return f"┌{'─' * 28}┐\n{content}\n└{'─' * 28}┘"


def points_display(points: int) -> str:
    return str(points)


def stock_indicator(stock: int) -> str:
    if stock <= 0:
        return "🔴 نفذت الكمية"
    elif stock <= 3:
        return f"🟠 متبقي {stock} فقط!"
    elif stock <= 10:
        return f"🟡 متبقي {stock}"
    else:
        return f"🟢 متوفر ({stock})"


# ================= DATABASE =================


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            points INTEGER DEFAULT 0,
            inviter INTEGER,
            join_date TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            name_ru TEXT,
            price_points INTEGER,
            stock INTEGER,
            button_id INTEGER
        )""")
        try:
            await db.execute("ALTER TABLE products ADD COLUMN name_ru TEXT")
        except:
            pass
        await db.execute("""
        CREATE TABLE IF NOT EXISTS codes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            code_text TEXT,
            used INTEGER DEFAULT 0
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            timestamp TEXT,
            delivered_text TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS banned_users(
            user_id INTEGER PRIMARY KEY,
            ban_date TEXT,
            reason TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS gift_links(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            link_code TEXT UNIQUE,
            points_per_use INTEGER,
            max_uses INTEGER,
            current_uses INTEGER DEFAULT 0,
            created_date TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS gift_link_users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            link_id INTEGER,
            used_date TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS moderators(
            user_id INTEGER PRIMARY KEY,
            promoted_date TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS daily_gifts(
            user_id INTEGER PRIMARY KEY,
            last_claim_date TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS product_notifications(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            user_id INTEGER,
            notified INTEGER DEFAULT 0,
            notified_date TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS user_languages(
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'ar'
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS custom_buttons(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            created_date TEXT
        )""")
        try:
            await db.execute("INSERT OR IGNORE INTO settings(key, value) VALUES('points_word', 'نقاط')")
        except:
            pass
        await db.commit()


async def is_user_banned(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id FROM banned_users WHERE user_id=?", (user_id, ))
        return await cur.fetchone() is not None


async def ban_user(user_id: int, reason: str = ""):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO banned_users(user_id, ban_date, reason) VALUES(?,?,?)",
            (user_id, datetime.now(timezone.utc).isoformat(), reason))
        await db.commit()


async def unban_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM banned_users WHERE user_id=?",
                         (user_id, ))
        await db.commit()


async def get_banned_users() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id, ban_date, reason FROM banned_users")
        return list(await cur.fetchall())


async def promote_moderator(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO moderators(user_id, promoted_date) VALUES(?,?)",
            (user_id, datetime.now(timezone.utc).isoformat()))
        await db.commit()


async def demote_moderator(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM moderators WHERE user_id=?", (user_id, ))
        await db.commit()


async def can_claim_daily_gift(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT last_claim_date FROM daily_gifts WHERE user_id=?", (user_id, ))
        row = await cur.fetchone()
        
        if not row:
            return True
        
        last_claim = datetime.fromisoformat(row[0])
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        last_claim_date = last_claim.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return last_claim_date < today


async def claim_daily_gift(user_id: int) -> bool:
    if not await can_claim_daily_gift(user_id):
        return False
    
    gift_amount = await get_daily_gift_amount()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO daily_gifts(user_id, last_claim_date) VALUES(?,?)",
            (user_id, datetime.now(timezone.utc).isoformat()))
        await db.execute(
            f"UPDATE users SET points = points + {gift_amount} WHERE user_id=?", (user_id, ))
        await db.commit()
    
    return True


async def is_moderator(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id FROM moderators WHERE user_id=?", (user_id, ))
        return await cur.fetchone() is not None


async def get_moderators() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id, promoted_date FROM moderators ORDER BY promoted_date DESC")
        return list(await cur.fetchall())


async def create_gift_link(points: int, max_uses: int,
                           bot_username: str) -> str:
    link_code = ''.join(
        random.choices(string.ascii_letters + string.digits, k=8))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO gift_links(link_code, points_per_use, max_uses, created_date) VALUES(?,?,?,?)",
            (link_code, points, max_uses, datetime.now(timezone.utc).isoformat()))
        await db.commit()
    full_link = f"https://t.me/{bot_username}?start=gift_{link_code}"
    return full_link


async def use_gift_link(user_id: int, link_code: str) -> tuple:
    if link_code.startswith("gift_"):
        link_code = link_code[5:]

    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, points_per_use, max_uses, current_uses FROM gift_links WHERE link_code=?",
            (link_code, ))
        link = await cur.fetchone()
        if not link:
            return (False, "الرابط غير موجود")

        lid, points, max_uses, current_uses = link
        if current_uses >= max_uses:
            return (False, "انتهت استخدامات هذا الرابط")

        cur = await db.execute(
            "SELECT id FROM gift_link_users WHERE user_id=? AND link_id=?",
            (user_id, lid))
        if await cur.fetchone():
            return (False, "لقد استخدمت هذا الرابط مسبقاً")

        await add_points(user_id, points)
        await db.execute(
            "UPDATE gift_links SET current_uses = current_uses + 1 WHERE id=?",
            (lid, ))
        await db.execute(
            "INSERT INTO gift_link_users(user_id, link_id, used_date) VALUES(?,?,?)",
            (user_id, lid, datetime.now(timezone.utc).isoformat()))
        await db.commit()
        return (True, f"تم إضافة {points} نقطة!")


# ================= USERS =================


async def ensure_user(user_id: int, inviter: Optional[int] = None) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id=?",
                               (user_id, ))
        if not await cur.fetchone():
            try:
                await db.execute(
                    "INSERT OR IGNORE INTO users(user_id, points, inviter, join_date) VALUES(?,?,?,?)",
                    (user_id, 0, inviter, datetime.now(timezone.utc).isoformat()))
                await db.commit()
                return True
            except Exception:
                return False
    return False


async def add_points(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        if amount < 0:
            cur = await db.execute("SELECT points FROM users WHERE user_id=?",
                                   (user_id, ))
            row = await cur.fetchone()
            current = row[0] if row else 0
            if current + amount < 0:
                return False
        await db.execute(
            "UPDATE users SET points = points + ? WHERE user_id=?",
            (amount, user_id))
        await db.commit()
        return True


async def get_points(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT points FROM users WHERE user_id=?",
                               (user_id, ))
        row = await cur.fetchone()
        return row[0] if row else 0


async def get_user_stats(user_id: int) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT points, join_date FROM users WHERE user_id=?", (user_id, ))
        row = await cur.fetchone()
        points = row[0] if row else 0
        join_date = row[1] if row else None

        cur = await db.execute("SELECT COUNT(*) FROM users WHERE inviter=?",
                               (user_id, ))
        row_invited = await cur.fetchone()
        invited = row_invited[0] if row_invited else 0

        cur = await db.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_id=?", (user_id, ))
        row_purchases = await cur.fetchone()
        purchases = row_purchases[0] if row_purchases else 0

        return {
            "points": points,
            "join_date": join_date,
            "invited_count": invited,
            "purchases": purchases
        }


async def get_leaderboard(limit: int = 5) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT user_id, points FROM users ORDER BY points DESC LIMIT ?",
            (limit, ))
        return list(await cur.fetchall())


async def get_total_users() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM users")
        result = await cur.fetchone()
    return result[0] if result else 0


async def get_banned_users_count() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM banned_users")
        result = await cur.fetchone()
    return result[0] if result else 0


# ================= PRODUCTS =================


async def list_products(category: Optional[str] = None,
                        button_id: Optional[int] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if category and button_id:
            cur = await db.execute(
                "SELECT id,category,name,name_ru,price_points,stock FROM products WHERE category=? AND button_id=?",
                (category, button_id))
        elif button_id:
            cur = await db.execute(
                "SELECT id,category,name,name_ru,price_points,stock FROM products WHERE button_id=?",
                (button_id, ))
        elif category:
            cur = await db.execute(
                "SELECT id,category,name,name_ru,price_points,stock FROM products WHERE category=?",
                (category, ))
        else:
            cur = await db.execute(
                "SELECT id,category,name,name_ru,price_points,stock FROM products")
        return list(await cur.fetchall())


async def get_product(pid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id,category,name,name_ru,price_points,stock FROM products WHERE id=?",
            (pid, ))
        return await cur.fetchone()


async def decrement_stock(pid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET stock = stock - 1 WHERE id=?",
                         (pid, ))
        await db.commit()


async def add_product(category: str, name: str, price: int, stock: int,
                       button_id: Optional[int] = None) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO products(category, name, price_points, stock, button_id) VALUES(?,?,?,?,?)",
            (category, name, price, stock, button_id))
        await db.commit()
        return cur.lastrowid or 0


async def remove_product(pid: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id=?", (pid, ))
        await db.execute("DELETE FROM codes WHERE product_id=?", (pid, ))
        await db.commit()


async def update_product_name(pid: int, new_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET name=? WHERE id=?",
                         (new_name, pid))
        await db.commit()


async def update_product_name_ru(pid: int, new_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET name_ru=? WHERE id=?",
                         (new_name, pid))
        await db.commit()


async def update_product_price(pid: int, new_price: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET price_points=? WHERE id=?",
                         (new_price, pid))
        await db.commit()


async def update_product_stock(pid: int, new_stock: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET stock=? WHERE id=?",
                         (new_stock, pid))
        await db.commit()


async def add_code(product_id: int, code_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO codes(product_id, code_text) VALUES(?,?)",
            (product_id, code_text))
        await db.commit()


async def get_available_code(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, code_text FROM codes WHERE product_id=? AND used=0 LIMIT 1",
            (product_id, ))
        return await cur.fetchone()


async def mark_code_used(code_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE codes SET used=1 WHERE id=?", (code_id, ))
        await db.commit()


async def add_transaction(user_id: int, product_id: int, delivered_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO transactions(user_id, product_id, timestamp, delivered_text) VALUES(?,?,?,?)",
            (user_id, product_id, datetime.now(timezone.utc).isoformat(),
             delivered_text))
        await db.commit()


async def get_custom_buttons():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, name FROM custom_buttons")
        return list(await cur.fetchall())


async def add_custom_button(name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO custom_buttons(name, created_date) VALUES(?,?)",
            (name, datetime.now(timezone.utc).isoformat()))
        await db.commit()
        return cur.lastrowid or 0


async def update_custom_button(btn_id: int, new_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE custom_buttons SET name=? WHERE id=?",
                         (new_name, btn_id))
        await db.commit()


async def delete_custom_button(btn_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM custom_buttons WHERE id=?", (btn_id, ))
        await db.execute("DELETE FROM products WHERE button_id=?", (btn_id, ))
        await db.commit()


async def notify_all_users_new_product(product_name: str, price: int,
                                        category: str):
    pass


# ================= KEYBOARDS =================


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def is_admin_or_moderator(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    return await is_moderator(user_id)


def main_menu_kb(is_user_admin: bool = False, lang: str = "ar"):
    buttons = [
        [InlineKeyboardButton(text=get_text("shop", lang), callback_data="menu:shop")],
        [InlineKeyboardButton(text=get_text("profile", lang), callback_data="menu:profile")],
        [InlineKeyboardButton(text=get_text("collect_points", lang), callback_data="menu:collect_points")],
        [InlineKeyboardButton(text=get_text("help", lang), callback_data="menu:help")],
        [InlineKeyboardButton(text=get_text("language", lang), callback_data="change_language")]
    ]
    if is_user_admin:
        buttons.append([InlineKeyboardButton(text=get_text("control_panel", lang), callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def category_kb(lang: str = "ar"):
    custom_buttons = await get_custom_buttons()
    buttons = [
        [InlineKeyboardButton(text=f"⭐ {get_text('stars', lang)}", callback_data="cat:stars")],
        [InlineKeyboardButton(text=get_text("play", lang), callback_data="cat:play")]
    ]
    for btn_id, btn_name in custom_buttons:
        buttons.append([InlineKeyboardButton(text=btn_name, callback_data=f"custombtn:{btn_id}")])
    buttons.append([InlineKeyboardButton(text=get_text("all_products", lang), callback_data="cat:all")])
    buttons.append([InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_main_kb(lang: str = "ar"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")]
    ])


def back_to_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")]
    ])


def back_to_shop_kb(lang: str = "ar"):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=get_text("back_shop", lang), callback_data="menu:shop")]
    ])


# ================= REGISTER HANDLERS =================

def register_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        global bot
        if await is_user_banned(message.from_user.id):
            lang = await get_user_language(message.from_user.id)
            await message.answer(
                f"{get_text('banned', lang)}\n{get_text('contact_admin', lang)}: {DEV_CONTACT}"
            )
            return

        args = message.text.split()[1] if len(message.text.split()) > 1 else None
        inviter = None

        if args:
            if args.startswith("gift_"):
                await ensure_user(message.from_user.id, None)
                success, msg = await use_gift_link(message.from_user.id, args)
                if success:
                    await message.answer(f"🎁 {msg}")
                else:
                    await message.answer(f"❌ {msg}")
                return
            else:
                try:
                    inviter = int(args)
                    if inviter == message.from_user.id:
                        inviter = None
                except:
                    pass

        is_new = await ensure_user(message.from_user.id, inviter)

        if is_new and inviter:
            await add_points(inviter, INVITER_POINTS)
            try:
                points_word = await get_points_word()
                await bot.send_message(
                    inviter,
                    f"🎉 انضم صديق جديد من رابطك!\n+{INVITER_POINTS} {points_word}"
                )
            except:
                pass

        lang = await get_user_language(message.from_user.id, message.from_user.language_code)
        points = await get_points(message.from_user.id)
        points_word = await get_points_word()
        me = await bot.get_me()
        invite_link = f"https://t.me/{me.username}?start={message.from_user.id}"
        username_display = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"

        if lang == "ar":
            text = (
                f"🎁 <b>بوت الجوائز والمكافآت</b> 🎁\n\n"
                f"👋 مرحباً <b>{message.from_user.first_name}</b>\n"
                f"👤 {username_display}\n\n"
                f"اجمع {points_word} واحصل على جوائز مذهلة بسهولة.\n\n"
                f"🔗 <b>رابط الدعوة الخاص بك:</b>\n"
                f"<code>{invite_link}</code>\n"
                f"انسخ هذا الرابط وشاركه مع أصدقاءك لتحصل على {points_word} مع كل صديق ينضم!\n\n"
                f"📌 <b>كيف يعمل البوت؟</b>\n"
                f"1️⃣ ادعُ أصدقاءك برابطك الخاص\n"
                f"2️⃣ احصل على {points_word} عن كل صديق ينضم\n"
                f"3️⃣ استبدل {points_word}ك بـ ⭐ نجوم تيليجرام و 🎮 بطاقات Google Play\n\n"
                f"🎁 كل صديق تقوم بدعوته يمكنك الحصول على <b>1 {points_word}</b>\n\n"
                f"💰 رصيدك الحالي: <b>{points_display(points)}</b> {points_word}\n"
            )
        else:
            text = (
                f"🎁 <b>Бот награды и подарки</b> 🎁\n\n"
                f"👋 Привет <b>{message.from_user.first_name}</b>\n"
                f"👤 {username_display}\n\n"
                f"Собирайте {points_word} и получайте удивительные награды легко.\n\n"
                f"🔗 <b>Ваша реферальная ссылка:</b>\n"
                f"<code>{invite_link}</code>\n"
                f"Скопируйте эту ссылку и поделитесь ею с друзьями, чтобы получить {points_word} за каждого присоединившегося друга!\n\n"
                f"📌 <b>Как это работает?</b>\n"
                f"1️⃣ Пригласите своих друзей по вашей личной ссылке\n"
                f"2️⃣ Получайте {points_word} за каждого присоединившегося друга\n"
                f"3️⃣ Обменивайте {points_word} на ⭐ звезды Telegram и 🎮 карты Google Play\n\n"
                f"🎁 За каждого приглашённого друга вы получаете <b>1 {points_word}</b>\n\n"
                f"💰 Ваш баланс: <b>{points_display(points)}</b> {points_word}\n"
            )

        user_pages[message.from_user.id] = "main"
        await message.answer(text, reply_markup=main_menu_kb(is_admin(message.from_user.id), lang))

    @dp.callback_query(F.data == "change_language")
    async def change_language_handler(cb: types.CallbackQuery):
        lang = await get_user_language(cb.from_user.id)
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text("arabic", lang), callback_data="setlang:ar")],
            [InlineKeyboardButton(text=get_text("russian", lang), callback_data="setlang:ru")],
            [InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")]
        ])
        await cb.message.edit_text(get_text("select_lang", lang), reply_markup=kb)
        await cb.answer()

    @dp.callback_query(F.data.startswith("setlang:"))
    async def set_language_handler(cb: types.CallbackQuery):
        new_lang = cb.data.split(":")[1]
        await set_user_language(cb.from_user.id, new_lang)
        await cb.message.edit_text(
            get_text("lang_changed", new_lang),
            reply_markup=back_to_main_kb(new_lang)
        )
        await cb.answer()

    @dp.callback_query(F.data == "claim_daily_gift")
    async def claim_daily_gift_handler(cb: types.CallbackQuery):
        lang = await get_user_language(cb.from_user.id)
        success = await claim_daily_gift(cb.from_user.id)
        if success:
            gift_amount = await get_daily_gift_amount()
            points_word = await get_points_word()
            await cb.message.edit_text(
                f"🎉 {'تهانينا! حصلت على' if lang == 'ar' else 'Поздравляем! Вы получили'} <b>{gift_amount} {points_word}</b>!",
                reply_markup=back_to_main_kb(lang)
            )
        else:
            await cb.message.edit_text(
                get_text("gift_already_claimed", lang),
                reply_markup=back_to_main_kb(lang)
            )
        await cb.answer()

    @dp.callback_query(F.data.startswith("menu:"))
    async def menu_handler(cb: types.CallbackQuery):
        global bot
        action = cb.data.split(":", 1)[1]
        lang = await get_user_language(cb.from_user.id)

        if action == "main":
            user_pages[cb.from_user.id] = "main"
            admin_pages[cb.from_user.id] = "main"
            points = await get_points(cb.from_user.id)
            points_word = await get_points_word()
            me = await bot.get_me()
            invite_link = f"https://t.me/{me.username}?start={cb.from_user.id}"
            username_display = f"@{cb.from_user.username}" if cb.from_user.username else f"ID: {cb.from_user.id}"
            
            if lang == "ar":
                text = (
                    f"🎁 <b>بوت الجوائز والمكافآت</b> 🎁\n\n"
                    f"👋 مرحباً <b>{cb.from_user.first_name}</b>\n"
                    f"👤 {username_display}\n\n"
                    f"اجمع {points_word} واحصل على جوائز مذهلة بسهولة.\n\n"
                    f"🔗 <b>رابط الدعوة الخاص بك:</b>\n"
                    f"<code>{invite_link}</code>\n"
                    f"انسخ هذا الرابط وشاركه مع أصدقاءك لتحصل على {points_word} مع كل صديق ينضم!\n\n"
                    f"📌 <b>كيف يعمل البوت؟</b>\n"
                    f"1️⃣ ادعُ أصدقاءك برابطك الخاص\n"
                    f"2️⃣ احصل على {points_word} عن كل صديق ينضم\n"
                    f"3️⃣ استبدل {points_word}ك بـ ⭐ نجوم تيليجرام و 🎮 بطاقات Google Play\n\n"
                    f"🎁 كل صديق تقوم بدعوته يمكنك الحصول على <b>1 {points_word}</b>\n\n"
                    f"💰 رصيدك الحالي: <b>{points_display(points)}</b> {points_word}\n"
                )
            else:
                text = (
                    f"🎁 <b>Бот награды и подарки</b> 🎁\n\n"
                    f"👋 Привет <b>{cb.from_user.first_name}</b>\n"
                    f"👤 {username_display}\n\n"
                    f"Собирайте {points_word} и получайте удивительные награды легко.\n\n"
                    f"🔗 <b>Ваша реферальная ссылка:</b>\n"
                    f"<code>{invite_link}</code>\n"
                    f"Скопируйте эту ссылку и поделитесь ею с друзьями, чтобы получить {points_word} за каждого присоединившегося друга!\n\n"
                    f"📌 <b>Как это работает?</b>\n"
                    f"1️⃣ Пригласите своих друзей по вашей личной ссылке\n"
                    f"2️⃣ Получайте {points_word} за каждого присоединившегося друга\n"
                    f"3️⃣ Обменивайте {points_word} на ⭐ звезды Telegram и 🎮 карты Google Play\n\n"
                    f"🎁 За каждого приглашённого друга вы получаете <b>1 {points_word}</b>\n\n"
                    f"💰 Ваш баланс: <b>{points_display(points)}</b> {points_word}\n"
                )
            await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))

        elif action == "shop":
            user_pages[cb.from_user.id] = "shop"
            points = await get_points(cb.from_user.id)
            points_word = await get_points_word()
            text = (f"{get_text('store', lang)}\n"
                    f"{get_text('my_points', lang)}: <b>{points_display(points)}</b> {points_word}\n\n"
                    f"{get_text('choose_category', lang)}:")
            await cb.message.edit_text(text, reply_markup=await category_kb(lang))

        elif action == "profile":
            stats = await get_user_stats(cb.from_user.id)
            rank = "🥉 مبتدئ" if lang == "ar" else "🥉 Новичок"
            if stats["points"] >= 100:
                rank = "💎 ماسي" if lang == "ar" else "💎 Мастер"
            elif stats["points"] >= 50:
                rank = "🥇 ذهبي" if lang == "ar" else "🥇 Золото"
            elif stats["points"] >= 20:
                rank = "🥈 فضي" if lang == "ar" else "🥈 Серебро"

            text = (f"{get_text('my_account', lang)}\n"
                    f"🆔 {'المعرف' if lang == 'ar' else 'ID'}: <code>{cb.from_user.id}</code>\n\n"
                    f"{get_text('statistics', lang)}\n"
                    f"{get_text('points_label', lang)}: <b>{stats['points']}</b>\n"
                    f"{get_text('rank', lang)}: {rank}\n"
                    f"{get_text('invited_friends', lang)}: <b>{stats['invited_count']}</b>\n"
                    f"{get_text('purchases', lang)}: <b>{stats['purchases']}</b>\n")
            
            user_pages[cb.from_user.id] = "profile"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("leaderboard", lang), callback_data="menu:leaderboard")],
                [InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")]
            ])
            await cb.message.edit_text(text, reply_markup=kb)

        elif action == "leaderboard":
            user_pages[cb.from_user.id] = "leaderboard"
            leaders = await get_leaderboard(5)
            text = f"{get_text('leaderboard_title', lang)}\n\n"
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            for i, (uid, pts) in enumerate(leaders):
                try:
                    user = await bot.get_chat(uid)
                    name = user.first_name[:15]
                except:
                    name = f"{'مستخدم' if lang == 'ar' else 'Пользователь'} {uid}"
                text += f"{medals[i]} <b>{name}</b> — {pts} {get_text('points', lang)}\n"

            if not leaders:
                text += f"{get_text('no_leaders', lang)}\n"
            await cb.message.edit_text(text, reply_markup=back_to_main_kb(lang))

        elif action == "invite":
            user_pages[cb.from_user.id] = "invite"
            me = await bot.get_me()
            stats = await get_user_stats(cb.from_user.id)
            points_word = await get_points_word()
            invite_link = f"https://t.me/{me.username}?start={cb.from_user.id}"
            text = (f"{get_text('invite_friends', lang)}\n"
                    f"🎁 {'ادعُ أصدقاءك واحصل على' if lang == 'ar' else 'Пригласите друзей и получите'} <b>{INVITER_POINTS} {points_word}</b>\n\n"
                    f"{get_text('invite_link', lang)}:\n"
                    f"<code>{invite_link}</code>\n\n"
                    f"📊 {get_text('invited_friends', lang)}: <b>{stats['invited_count']}</b>\n")
            await cb.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("back", lang), callback_data="menu:collect_points")]
            ]))

        elif action == "collect_points":
            user_pages[cb.from_user.id] = "collect_points"
            can_claim = await can_claim_daily_gift(cb.from_user.id)
            gift_status = "🟢" if can_claim else "🔴"
            
            if lang == "ar":
                text = (
                    f"💰 <b>تجميع النقاط</b>\n\n"
                    f"اجمع النقاط من خلال:\n"
                    f"• استلام الهدية اليومية {gift_status}\n"
                    f"• دعوة أصدقائك للبوت\n\n"
                    f"📌 اختر أحد الخيارات:"
                )
            else:
                text = (
                    f"💰 <b>Собрать очки</b>\n\n"
                    f"Собирайте очки через:\n"
                    f"• Ежедневный подарок {gift_status}\n"
                    f"• Приглашение друзей\n\n"
                    f"📌 Выберите опцию:"
                )
            
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("daily_gift", lang), callback_data="menu:daily_gift")],
                [InlineKeyboardButton(text=get_text("invite", lang), callback_data="menu:invite")],
                [InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")]
            ])
            await cb.message.edit_text(text, reply_markup=kb)

        elif action == "daily_gift":
            user_pages[cb.from_user.id] = "daily_gift"
            can_claim = await can_claim_daily_gift(cb.from_user.id)
            gift_amount = await get_daily_gift_amount()
            points_word = await get_points_word()
            if can_claim:
                text = f"{get_text('daily_gift_title', lang)}\n✨ {'تهانينا! هديّتك اليومية متاحة الآن!' if lang == 'ar' else 'Поздравляем! Ваш ежедневный подарок готов!'}\n\n🎉 {'اضغط للحصول على' if lang == 'ar' else 'Нажмите для получения'} <b>{gift_amount} {points_word}</b>"
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text=get_text("get_gift", lang), callback_data="claim_daily_gift")
                ], [
                    InlineKeyboardButton(text=get_text("back", lang), callback_data="menu:collect_points")
                ]])
            else:
                text = f"{get_text('daily_gift_title', lang)}\n{get_text('gift_already_claimed', lang)}!"
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=get_text("back", lang), callback_data="menu:collect_points")]
                ])
            await cb.message.edit_text(text, reply_markup=kb)

        elif action == "help":
            user_pages[cb.from_user.id] = "help"
            text = (f"{get_text('help_title', lang)}\n{get_text('how_it_works', lang)}\n\n"
                    f"1️⃣ {'اجمع النقاط' if lang == 'ar' else 'Соберите очки'}\n"
                    f"2️⃣ {'تصفح المتجر' if lang == 'ar' else 'Просмотрите магазин'}\n"
                    f"3️⃣ {'اشترِ واستمتع' if lang == 'ar' else 'Покупайте и наслаждайтесь'}\n")
            await cb.message.edit_text(text, reply_markup=back_to_main_kb(lang))

        await cb.answer()

    @dp.callback_query(F.data == "back:")
    async def back_handler(cb: types.CallbackQuery):
        global bot
        lang = await get_user_language(cb.from_user.id)
        
        last_user_page = user_pages.get(cb.from_user.id, None)
        is_in_user_page = last_user_page is not None and last_user_page != "main"
        
        if is_in_user_page:
            points = await get_points(cb.from_user.id)
            points_word = await get_points_word()
            me = await bot.get_me()
            invite_link = f"https://t.me/{me.username}?start={cb.from_user.id}"
            username_display = f"@{cb.from_user.username}" if cb.from_user.username else f"ID: {cb.from_user.id}"
            user_pages[cb.from_user.id] = "main"
            
            if lang == "ar":
                text = (
                    f"🎁 <b>بوت الجوائز والمكافآت</b> 🎁\n\n"
                    f"👋 مرحباً <b>{cb.from_user.first_name}</b>\n"
                    f"👤 {username_display}\n\n"
                    f"اجمع {points_word} واحصل على جوائز مذهلة بسهولة.\n\n"
                    f"🔗 <b>رابط الدعوة الخاص بك:</b>\n"
                    f"<code>{invite_link}</code>\n"
                    f"انسخ هذا الرابط وشاركه مع أصدقاءك لتحصل على {points_word} مع كل صديق ينضم!\n\n"
                    f"📌 <b>كيف يعمل البوت؟</b>\n"
                    f"1️⃣ ادعُ أصدقاءك برابطك الخاص\n"
                    f"2️⃣ احصل على {points_word} عن كل صديق ينضم\n"
                    f"3️⃣ استبدل {points_word}ك بـ ⭐ نجوم تيليجرام و 🎮 بطاقات Google Play\n\n"
                    f"🎁 كل صديق تقوم بدعوته يمكنك الحصول على <b>1 {points_word}</b>\n\n"
                    f"💰 رصيدك الحالي: <b>{points_display(points)}</b> {points_word}\n"
                )
            else:
                text = (
                    f"🎁 <b>Бот награды и подарки</b> 🎁\n\n"
                    f"👋 Привет <b>{cb.from_user.first_name}</b>\n"
                    f"👤 {username_display}\n\n"
                    f"Собирайте {points_word} и получайте удивительные награды легко.\n\n"
                    f"🔗 <b>Ваша реферальная ссылка:</b>\n"
                    f"<code>{invite_link}</code>\n"
                    f"Скопируйте эту ссылку и поделитесь ею с друзьями, чтобы получить {points_word} за каждого присоединившегося друга!\n\n"
                    f"📌 <b>Как это работает?</b>\n"
                    f"1️⃣ Пригласите своих друзей по вашей личной ссылке\n"
                    f"2️⃣ Получайте {points_word} за каждого присоединившегося друга\n"
                    f"3️⃣ Обменивайте {points_word} на ⭐ звезды Telegram и 🎮 карты Google Play\n\n"
                    f"🎁 За каждого приглашённого друга вы получаете <b>1 {points_word}</b>\n\n"
                    f"💰 Ваш баланс: <b>{points_display(points)}</b> {points_word}\n"
                )
            await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))
            await cb.answer()
            return

        if await is_admin_or_moderator(cb.from_user.id):
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ تعيين كلمة نقاط", callback_data="admin_setword"),
                    InlineKeyboardButton(text="🔢 تعيين نقاط الدخول", callback_data="admin_entrypoints")
                ],
                [
                    InlineKeyboardButton(text="👤 تعيين حساب المطور", callback_data="admin_setdev"),
                    InlineKeyboardButton(text="🎁 صنع روابط تمويل", callback_data="admin_giftlink")
                ],
                [
                    InlineKeyboardButton(text="📦 جميع السلع", callback_data="admin_productsmenu"),
                    InlineKeyboardButton(text="📦 جميع المنتجات", callback_data="admin_allproducts")
                ],
                [
                    InlineKeyboardButton(text="🏪 أقسام المتجر", callback_data="admin_categories"),
                    InlineKeyboardButton(text="🎟️ الخصم", callback_data="admin_coupons")
                ],
                [
                    InlineKeyboardButton(text="🎁 صنع رابط هدايا", callback_data="admin_giftlink2"),
                    InlineKeyboardButton(text="📤 إرسال نقاط", callback_data="admin_broadcast")
                ],
                [InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin_stats")],
                [InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="admin_settings")],
                [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="exit_admin:")]
            ])
            await cb.message.edit_text(
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"
                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)
        await cb.answer()

    @dp.callback_query(F.data == "exit_admin:")
    async def exit_admin_handler(cb: types.CallbackQuery):
        global bot
        lang = await get_user_language(cb.from_user.id)
        
        admin_pages.pop(cb.from_user.id, None)
        admin_prev_pages.pop(cb.from_user.id, None)
        user_pages[cb.from_user.id] = "main"
        
        points = await get_points(cb.from_user.id)
        points_word = await get_points_word()
        me = await bot.get_me()
        invite_link = f"https://t.me/{me.username}?start={cb.from_user.id}"
        username_display = f"@{cb.from_user.username}" if cb.from_user.username else f"ID: {cb.from_user.id}"
        
        if lang == "ar":
            text = (
                f"🎁 <b>بوت الجوائز والمكافآت</b> 🎁\n\n"
                f"👋 مرحباً <b>{cb.from_user.first_name}</b>\n"
                f"👤 {username_display}\n\n"
                f"اجمع {points_word} واحصل على جوائز مذهلة بسهولة.\n\n"
                f"🔗 <b>رابط الدعوة الخاص بك:</b>\n"
                f"<code>{invite_link}</code>\n"
                f"انسخ هذا الرابط وشاركه مع أصدقاءك لتحصل على {points_word} مع كل صديق ينضم!\n\n"
                f"📌 <b>كيف يعمل البوت؟</b>\n"
                f"1️⃣ ادعُ أصدقاءك برابطك الخاص\n"
                f"2️⃣ احصل على {points_word} عن كل صديق ينضم\n"
                f"3️⃣ استبدل {points_word}ك بـ ⭐ نجوم تيليجرام و 🎮 بطاقات Google Play\n\n"
                f"🎁 كل صديق تقوم بدعوته يمكنك الحصول على <b>1 {points_word}</b>\n\n"
                f"💰 رصيدك الحالي: <b>{points_display(points)}</b> {points_word}\n"
            )
        else:
            text = (
                f"🎁 <b>Бот награды и подарки</b> 🎁\n\n"
                f"👋 Привет <b>{cb.from_user.first_name}</b>\n"
                f"👤 {username_display}\n\n"
                f"Собирайте {points_word} и получайте удивительные награды легко.\n\n"
                f"🔗 <b>Ваша реферальная ссылка:</b>\n"
                f"<code>{invite_link}</code>\n"
                f"Скопируйте эту ссылку и поделитесь ею с друзьями, чтобы получить {points_word} за каждого присоединившегося друга!\n\n"
                f"📌 <b>Как это работает?</b>\n"
                f"1️⃣ Пригласите своих друзей по вашей личной ссылке\n"
                f"2️⃣ Получайте {points_word} за каждого присоединившегося друга\n"
                f"3️⃣ Обменивайте {points_word} на ⭐ звезды Telegram и 🎮 карты Google Play\n\n"
                f"🎁 За каждого приглашённого друга вы получаете <b>1 {points_word}</b>\n\n"
                f"💰 Ваш баланс: <b>{points_display(points)}</b> {points_word}\n"
            )
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))
        await cb.answer()

    @dp.callback_query(F.data.startswith("cat:"))
    async def category_handler(cb: types.CallbackQuery):
        category = cb.data.split(":")[1]
        lang = await get_user_language(cb.from_user.id)
        points = await get_points(cb.from_user.id)
        points_word = await get_points_word()

        if category == "all":
            products = await list_products()
        elif category == "stars":
            products = await list_products("stars")
        elif category == "play":
            products = await list_products("play")
        else:
            products = []

        if not products:
            await cb.message.edit_text(
                "📭 لا توجد منتجات في هذا القسم" if lang == "ar" else "📭 Нет товаров в этой категории",
                reply_markup=back_to_shop_kb(lang)
            )
            return await cb.answer()

        buttons = []
        for p in products:
            pid, cat, name_ar, name_ru, price, stock = p
            pname = get_product_name(name_ar, name_ru, lang)
            emoji = "⭐" if cat == "stars" else "🎮"
            stock_txt = stock_indicator(stock)
            
            if points >= price and stock > 0:
                btn_text = f"{emoji} {pname} | {price} {points_word}"
            else:
                btn_text = f"🔒 {pname} | {price} {points_word}"
            
            buttons.append([InlineKeyboardButton(text=btn_text, callback_data=f"prod:{pid}")])
        
        buttons.append([InlineKeyboardButton(text=get_text("back_shop", lang), callback_data="menu:shop")])
        
        await cb.message.edit_text(
            f"📦 {'المنتجات المتاحة' if lang == 'ar' else 'Доступные товары'}:\n"
            f"💰 {get_text('my_points', lang)}: <b>{points}</b> {points_word}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )
        await cb.answer()

    @dp.callback_query(F.data.startswith("prod:"))
    async def product_handler(cb: types.CallbackQuery):
        pid = int(cb.data.split(":")[1])
        lang = await get_user_language(cb.from_user.id)
        product = await get_product(pid)

        if not product:
            await cb.answer("❌ المنتج غير موجود" if lang == "ar" else "❌ Товар не найден", show_alert=True)
            return

        _, cat, name_ar, name_ru, price, stock = product
        pname = get_product_name(name_ar, name_ru, lang)
        points = await get_points(cb.from_user.id)
        points_word = await get_points_word()

        text = (
            f"📦 <b>{pname}</b>\n\n"
            f"💰 {'السعر' if lang == 'ar' else 'Цена'}: <b>{price}</b> {points_word}\n"
            f"📊 {stock_indicator(stock)}\n\n"
            f"💵 {'رصيدك' if lang == 'ar' else 'Ваш баланс'}: <b>{points}</b> {points_word}\n"
        )

        if points >= price and stock > 0:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("buy_now", lang), callback_data=f"buy:{pid}")],
                [InlineKeyboardButton(text=get_text("back_shop", lang), callback_data="menu:shop")]
            ])
        else:
            needed = price - points
            text += f"\n🔒 {'تحتاج' if lang == 'ar' else 'Вам нужно'} <b>{needed}</b> {points_word} {'إضافية' if lang == 'ar' else 'ещё'}"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=get_text("back_shop", lang), callback_data="menu:shop")]
            ])

        await cb.message.edit_text(text, reply_markup=kb)
        await cb.answer()

    @dp.callback_query(F.data.startswith("buy:"))
    async def buy_handler(cb: types.CallbackQuery):
        pid = int(cb.data.split(":")[1])
        lang = await get_user_language(cb.from_user.id)
        product = await get_product(pid)

        if not product:
            await cb.answer("❌ المنتج غير موجود" if lang == "ar" else "❌ Товар не найден", show_alert=True)
            return

        _, cat, name_ar, name_ru, price, stock = product
        pname = get_product_name(name_ar, name_ru, lang)
        points = await get_points(cb.from_user.id)

        if points < price:
            await cb.answer("❌ رصيدك غير كافٍ" if lang == "ar" else "❌ Недостаточно очков", show_alert=True)
            return

        if stock <= 0:
            await cb.answer("❌ المنتج نفذ" if lang == "ar" else "❌ Товар закончился", show_alert=True)
            return

        code = await get_available_code(pid)
        if not code:
            await cb.answer("❌ لا توجد أكواد متاحة" if lang == "ar" else "❌ Нет доступных кодов", show_alert=True)
            return

        code_id, code_text = code
        await add_points(cb.from_user.id, -price)
        await mark_code_used(code_id)
        await decrement_stock(pid)
        await add_transaction(cb.from_user.id, pid, code_text)

        await cb.message.edit_text(
            f"🎉 {'تم الشراء بنجاح!' if lang == 'ar' else 'Покупка успешна!'}\n\n"
            f"📦 {'المنتج' if lang == 'ar' else 'Товар'}: <b>{pname}</b>\n"
            f"🔑 {'الكود' if lang == 'ar' else 'Код'}:\n<code>{code_text}</code>\n\n"
            f"{'احتفظ بالكود في مكان آمن!' if lang == 'ar' else 'Сохраните код в безопасном месте!'}",
            reply_markup=back_to_shop_kb(lang)
        )
        await cb.answer()

    @dp.callback_query(F.data == "admin_panel")
    async def admin_panel_handler(cb: types.CallbackQuery):
        if not await is_admin_or_moderator(cb.from_user.id):
            await cb.answer("❌ ليس لديك صلاحية", show_alert=True)
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ تعيين كلمة نقاط", callback_data="admin_setword"),
                InlineKeyboardButton(text="🔢 تعيين نقاط الدخول", callback_data="admin_entrypoints")
            ],
            [
                InlineKeyboardButton(text="👤 تعيين حساب المطور", callback_data="admin_setdev"),
                InlineKeyboardButton(text="🎁 صنع روابط تمويل", callback_data="admin_giftlink")
            ],
            [
                InlineKeyboardButton(text="📦 جميع السلع", callback_data="admin_productsmenu"),
                InlineKeyboardButton(text="📦 جميع المنتجات", callback_data="admin_allproducts")
            ],
            [
                InlineKeyboardButton(text="🏪 أقسام المتجر", callback_data="admin_categories"),
                InlineKeyboardButton(text="🎟️ الخصم", callback_data="admin_coupons")
            ],
            [
                InlineKeyboardButton(text="🎁 صنع رابط هدايا", callback_data="admin_giftlink2"),
                InlineKeyboardButton(text="📤 إرسال نقاط", callback_data="admin_broadcast")
            ],
            [InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin_stats")],
            [InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="admin_settings")],
            [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="exit_admin:")]
        ])
        
        admin_pages[cb.from_user.id] = "main"
        await cb.message.edit_text(
            f"⚙️ <b>لوحة التحكم</b>\n"
            f"👋 مرحباً أيها المسؤول\n\n"
            f"📌 اختر الإجراء المطلوب:",
            reply_markup=kb)
        await cb.answer()

    @dp.callback_query(F.data.startswith("admin_"))
    async def admin_cb(cb: types.CallbackQuery):
        global bot
        action = cb.data.split("_", 1)[1]
        uid = cb.from_user.id
        if not await is_admin_or_moderator(uid):
            return await cb.answer("❌ ليس لديك صلاحية", show_alert=True)

        if action == "stats":
            async with aiosqlite.connect(DB_PATH) as db:
                cur = await db.execute("SELECT COUNT(*) FROM users")
                users_count = (await cur.fetchone())[0]
                cur = await db.execute("SELECT COUNT(*) FROM products")
                products_count = (await cur.fetchone())[0]
                cur = await db.execute("SELECT COUNT(*) FROM transactions")
                transactions_count = (await cur.fetchone())[0]
                cur = await db.execute("SELECT SUM(points) FROM users")
                total_points = (await cur.fetchone())[0] or 0

            text = (f"📊 <b>إحصائيات البوت</b>\n"
                    f"👥 عدد المستخدمين: <b>{users_count}</b>\n"
                    f"📦 عدد المنتجات: <b>{products_count}</b>\n"
                    f"🛒 عدد المعاملات: <b>{transactions_count}</b>\n"
                    f"إجمالي النقاط: <b>{total_points}</b>\n")
            await cb.message.edit_text(text, reply_markup=back_to_admin_kb())
            return await cb.answer()

        elif action == "setword":
            admin_pending[uid] = {"action": "setword"}
            await cb.message.edit_text(
                f"✏️ <b>تعيين كلمة النقاط</b>\n"
                f"أرسل الكلمة التي تريد استخدامها:\n"
                f"مثال: نقطة، نقاط، ستار",
                reply_markup=back_to_admin_kb())

        elif action == "giftlink" or action == "giftlink2":
            admin_pending[uid] = {"action": "giftlink", "step": "points"}
            await cb.message.edit_text(
                f"🎁 <b>إنشاء رابط هدايا</b>\n"
                f"📝 <b>الخطوة 1/2:</b>\n"
                f"كم نقطة لكل استخدام للرابط؟",
                reply_markup=back_to_admin_kb())

        elif action == "broadcast":
            admin_pending[uid] = {"action": "broadcast"}
            await cb.message.edit_text(
                f"📤 <b>إرسال نقاط للجميع</b>\n"
                f"كم نقطة تريد إضافتها لكل المستخدمين؟",
                reply_markup=back_to_admin_kb())

        elif action == "settings":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="👮 إدارة المشرفين", callback_data="admin_modmenu"),
                    InlineKeyboardButton(text="🔐 إدارة الحظر", callback_data="admin_banmenu")
                ],
                [
                    InlineKeyboardButton(text="📤 إرسال نقاط", callback_data="admin_broadcast"),
                    InlineKeyboardButton(text="🎁 الهديّة اليومية", callback_data="admin_dailygift")
                ],
                [InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")]
            ])
            await cb.message.edit_text(
                f"⚙️ <b>الإعدادات والإدارة</b>\n\n"
                f"👮 <b>إدارة المشرفين</b> - أضف أو احذف مشرفين\n"
                f"🔐 <b>إدارة الحظر</b> - حظر أو فك حظر المستخدمين\n\n"
                f"📤 <b>إرسال نقاط</b> - إضافة نقاط لجميع المستخدمين\n"
                f"🎁 <b>الهديّة اليومية</b> - تعديل مبلغ الهديّة اليومية\n\n"
                f"👇 اختر الإجراء المطلوب:",
                reply_markup=kb)

        elif action == "dailygift":
            gift_amount = await get_daily_gift_amount()
            admin_pending[uid] = {"action": "setdailygift"}
            await cb.message.edit_text(
                f"🎁 <b>تعديل كمية الهديّة اليومية</b>\n"
                f"الكمية الحالية: <b>{gift_amount}</b>\n\n"
                f"أرسل الكمية الجديدة (رقم فقط):",
                reply_markup=back_to_admin_kb())

        elif action == "mainmenu":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ تعيين كلمة نقاط", callback_data="admin_setword"),
                    InlineKeyboardButton(text="🔢 تعيين نقاط الدخول", callback_data="admin_entrypoints")
                ],
                [
                    InlineKeyboardButton(text="👤 تعيين حساب المطور", callback_data="admin_setdev"),
                    InlineKeyboardButton(text="🎁 صنع روابط تمويل", callback_data="admin_giftlink")
                ],
                [
                    InlineKeyboardButton(text="📦 جميع السلع", callback_data="admin_productsmenu"),
                    InlineKeyboardButton(text="📦 جميع المنتجات", callback_data="admin_allproducts")
                ],
                [
                    InlineKeyboardButton(text="🏪 أقسام المتجر", callback_data="admin_categories"),
                    InlineKeyboardButton(text="🎟️ الخصم", callback_data="admin_coupons")
                ],
                [
                    InlineKeyboardButton(text="🎁 صنع رابط هدايا", callback_data="admin_giftlink2"),
                    InlineKeyboardButton(text="📤 إرسال نقاط", callback_data="admin_broadcast")
                ],
                [InlineKeyboardButton(text="📊 الإحصائيات", callback_data="admin_stats")],
                [InlineKeyboardButton(text="⚙️ الإعدادات", callback_data="admin_settings")],
                [InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="exit_admin:")]
            ])
            await cb.message.edit_text(
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"
                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)

        elif action == "modmenu":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="⬆️ ترقية", callback_data="admin_promotemod"),
                    InlineKeyboardButton(text="⬇️ إزالة", callback_data="admin_demotemod")
                ],
                [InlineKeyboardButton(text="📋 قائمة المشرفين", callback_data="admin_listmods")],
                [InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")]
            ])
            await cb.message.edit_text(
                f"👮 <b>إدارة فريق العمل</b>\n\n"
                f"⬆️ <b>ترقية</b> - جعل مستخدم مشرفاً على البوت\n"
                f"⬇️ <b>إزالة</b> - إزالة مشرف من فريق العمل\n\n"
                f"📋 <b>قائمة المشرفين</b> - عرض جميع المشرفين الحاليين\n\n"
                f"👇 اختر الإجراء المطلوب:",
                reply_markup=kb)

        elif action == "banmenu":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🚫 حظر", callback_data="admin_banuser"),
                    InlineKeyboardButton(text="✅ فك حظر", callback_data="admin_unbanuser")
                ],
                [InlineKeyboardButton(text="📋 قائمة المحظورين", callback_data="admin_listbanned")],
                [InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")]
            ])
            await cb.message.edit_text(
                f"🚫 <b>إدارة الحظر والقيود</b>\n\n"
                f"🚫 <b>حظر</b> - منع مستخدم من استخدام البوت\n"
                f"✅ <b>فك حظر</b> - السماح لمستخدم بالعودة\n\n"
                f"📋 <b>قائمة المحظورين</b> - عرض جميع المستخدمين المحظورين\n\n"
                f"👇 اختر الإجراء المطلوب:",
                reply_markup=kb)

        elif action == "promotemod":
            admin_pending[uid] = {"action": "promotemod"}
            await cb.message.edit_text(
                f"⬆️ <b>ترقية مشرف</b>\n"
                f"أرسل ID المستخدم الذي تريد ترقيته لمشرف:",
                reply_markup=back_to_admin_kb())

        elif action == "demotemod":
            admin_pending[uid] = {"action": "demotemod"}
            await cb.message.edit_text(
                f"⬇️ <b>إزالة مشرف</b>\n"
                f"أرسل ID المشرف الذي تريد إزالته:",
                reply_markup=back_to_admin_kb())

        elif action == "listmods":
            mods = await get_moderators()
            if not mods:
                await cb.message.edit_text(
                    "📭 لا يوجد مشرفين حالياً",
                    reply_markup=back_to_admin_kb())
            else:
                text = f"👮 <b>قائمة المشرفين</b>\n\n"
                for m in mods:
                    user_id, promoted_date = m
                    text += f"🟢 <code>{user_id}</code>\n"
                await cb.message.edit_text(text, reply_markup=back_to_admin_kb())

        elif action == "banuser":
            admin_pending[uid] = {"action": "banuser"}
            await cb.message.edit_text(
                f"🚫 <b>حظر مستخدم</b>\n"
                f"أرسل ID المستخدم الذي تريد حظره:",
                reply_markup=back_to_admin_kb())

        elif action == "unbanuser":
            admin_pending[uid] = {"action": "unbanuser"}
            await cb.message.edit_text(
                f"✅ <b>فك حظر مستخدم</b>\n"
                f"أرسل ID المستخدم الذي تريد فك حظره:",
                reply_markup=back_to_admin_kb())

        elif action == "listbanned":
            banned = await get_banned_users()
            if not banned:
                await cb.message.edit_text(
                    "✅ لا يوجد مستخدمين محظورين",
                    reply_markup=back_to_admin_kb())
            else:
                text = f"📋 <b>قائمة المحظورين</b>\n\n"
                for b in banned:
                    user_id, ban_date, reason = b
                    text += f"🔴 <code>{user_id}</code>\n"
                await cb.message.edit_text(text, reply_markup=back_to_admin_kb())

        elif action == "entrypoints":
            admin_pending[uid] = {"action": "entrypoints"}
            await cb.message.edit_text(
                f"🔢 <b>تعيين نقاط الدخول</b>\n"
                f"كم نقطة يحصل عليها المستخدم الجديد عند التسجيل؟",
                reply_markup=back_to_admin_kb())

        elif action == "setdev":
            admin_pending[uid] = {"action": "setdev"}
            await cb.message.edit_text(
                f"👤 <b>تعيين حساب المطور</b>\n"
                f"أرسل معرف المطور/الدعم:\n"
                f"مثال: @username",
                reply_markup=back_to_admin_kb())

        elif action == "allproducts":
            products = await list_products()
            if not products:
                await cb.message.edit_text(
                    "📭 لا توجد منتجات",
                    reply_markup=back_to_admin_kb())
            else:
                buttons = []
                for p in products:
                    pid, cat, name_ar, name_ru, price, stock = p
                    pname = get_product_name(name_ar, name_ru, "ar")
                    emoji = "⭐" if cat == "stars" else "🎮"
                    buttons.append([
                        InlineKeyboardButton(
                            text=f"{emoji} {pname}",
                            callback_data="noop")
                    ])
                    buttons.append([
                        InlineKeyboardButton(
                            text=f"💎 السعر: {price} نقطة",
                            callback_data="noop"),
                        InlineKeyboardButton(
                            text=f"📦 الكمية: {stock}",
                            callback_data="noop")
                    ])
                buttons.append([
                    InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")
                ])
                await cb.message.edit_text(
                    f"📦 <b>جميع المنتجات ({len(products)})</b>",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

        elif action == "categories":
            await cb.message.edit_text(
                f"🏪 <b>أقسام المتجر</b>\n\n"
                f"⭐ نجوم تيليجرام\n"
                f"🎮 بطاقات Google Play\n"
                f"📦 كل المنتجات",
                reply_markup=back_to_admin_kb())

        elif action == "coupons":
            await cb.message.edit_text(
                f"🎟️ <b>كودات الخصم</b>\n\n"
                f"هذه الميزة قريباً...",
                reply_markup=back_to_admin_kb())

        elif action == "productsmenu":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ إضافة منتج نجوم", callback_data="admin_addstars")],
                [InlineKeyboardButton(text="➕ إضافة منتج Google Play", callback_data="admin_addplay")],
                [InlineKeyboardButton(text="✏️ تعديل المنتجات الموجودة", callback_data="admin_editproducts")],
                [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_mainmenu")]
            ])
            await cb.message.edit_text(
                f"📦 <b>إدارة المنتجات والسلع</b>\n\n"
                f"🎯 اختر العملية المطلوبة:",
                reply_markup=kb)

        elif action == "addstars":
            admin_pending[uid] = {"action": "addstars", "step": "name"}
            await cb.message.edit_text(
                f"⭐ <b>إضافة منتج نجوم جديد</b>\n"
                f"📝 <b>الخطوة 1/3:</b>\n"
                f"أرسل اسم المنتج:",
                reply_markup=back_to_admin_kb())

        elif action == "addplay":
            admin_pending[uid] = {"action": "addplay", "step": "name"}
            await cb.message.edit_text(
                f"🎮 <b>إضافة منتج Google Play جديد</b>\n"
                f"📝 <b>الخطوة 1/3:</b>\n"
                f"أرسل اسم المنتج:",
                reply_markup=back_to_admin_kb())

        elif action == "editproducts":
            products = await list_products()
            if not products:
                await cb.message.edit_text(
                    f"📦 <b>تعديل المنتجات</b>\n"
                    f"📭 لا توجد منتجات حالياً",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_productsmenu")]
                    ]))
            else:
                text = f"📦 <b>جميع المنتجات</b>\n\n"
                kb_buttons = []
                for pid, cat, name_ar, name_ru, price, stock in products:
                    pname = get_product_name(name_ar, name_ru, "ar")
                    emoji = "⭐" if cat == "stars" else "🎮"
                    text += f"{emoji} {pname} - {price} نقطة (الكمية: {stock})\n"
                    kb_buttons.append([
                        InlineKeyboardButton(text=f"✏️ {pname}", callback_data=f"admin_editprod:{pid}")
                    ])
                kb_buttons.append([
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_productsmenu")
                ])
                await cb.message.edit_text(
                    text,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))

        elif action.startswith("editprod:"):
            pid = int(action.split(":")[1])
            product = await get_product(pid)
            if not product:
                await cb.message.edit_text(
                    "❌ المنتج غير موجود",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_productsmenu")]
                    ]))
            else:
                pid, cat, name_ar, name_ru, price, stock = product[:6]
                pname = get_product_name(name_ar, name_ru, "ar")
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✏️ تعديل الاسم", callback_data=f"admin_editprodname:{pid}")],
                    [InlineKeyboardButton(text="💰 تعديل السعر", callback_data=f"admin_editprodprice:{pid}")],
                    [InlineKeyboardButton(text="📦 تعديل الكمية", callback_data=f"admin_editprodstock:{pid}")],
                    [InlineKeyboardButton(text="🗑️ حذف المنتج", callback_data=f"admin_delprod:{pid}")],
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_productsmenu")]
                ])
                await cb.message.edit_text(
                    f"📦 <b>تعديل المنتج</b>\n"
                    f"📝 الاسم: <b>{name_ar}</b>\n"
                    f"💰 السعر: <b>{price}</b>\n"
                    f"📊 الكمية: <b>{stock}</b>",
                    reply_markup=kb)

        elif action.startswith("editprodname:"):
            pid = int(action.split(":")[1])
            admin_pending[uid] = {"action": "editprodname", "pid": pid}
            await cb.message.edit_text(
                f"✏️ <b>تعديل اسم المنتج</b>\n"
                f"أرسل الاسم الجديد:",
                reply_markup=back_to_admin_kb())

        elif action.startswith("editprodprice:"):
            pid = int(action.split(":")[1])
            admin_pending[uid] = {"action": "editprodprice", "pid": pid}
            await cb.message.edit_text(
                f"💰 <b>تعديل سعر المنتج</b>\n"
                f"أرسل السعر الجديد (بالنقاط):",
                reply_markup=back_to_admin_kb())

        elif action.startswith("editprodstock:"):
            pid = int(action.split(":")[1])
            admin_pending[uid] = {"action": "editprodstock", "pid": pid}
            await cb.message.edit_text(
                f"📦 <b>تعديل كمية المنتج</b>\n"
                f"أرسل الكمية الجديدة:",
                reply_markup=back_to_admin_kb())

        elif action.startswith("delprod:"):
            pid = int(action.split(":")[1])
            await remove_product(pid)
            await cb.message.edit_text(
                f"🗑️ <b>تم حذف المنتج!</b>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_productsmenu")]
                ]))

        await cb.answer()

    @dp.message()
    async def handle_admin_input(message: types.Message):
        global bot
        uid = message.from_user.id
        if uid not in admin_pending:
            return

        data = admin_pending[uid]
        action = data.get("action")
        step = data.get("step")
        text = message.text

        try:
            if action == "setword":
                await set_points_word(text)
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تغيير كلمة النقاط إلى: <b>{text}</b>",
                    reply_markup=back_to_admin_kb())

            elif action == "setdailygift":
                amount = int(text)
                if amount <= 0:
                    await message.reply("❌ يجب أن تكون الكمية أكبر من 0")
                    return
                await set_daily_gift_amount(amount)
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تعديل كمية الهديّة اليومية: <b>{amount}</b>\n\n"
                    f"المستخدمون سيحصلون على <b>{amount}</b> في الهديّة اليومية!",
                    reply_markup=back_to_admin_kb())

            elif action == "giftlink":
                if step == "points":
                    pts = int(text)
                    admin_pending[uid]["points"] = pts
                    admin_pending[uid]["step"] = "uses"
                    await message.reply(
                        f"✅ {pts} نقطة لكل استخدام\n\n"
                        f"📝 <b>الخطوة 2/2:</b>\n"
                        f"كم مرة يمكن استخدام الرابط؟",
                        reply_markup=back_to_admin_kb())
                elif step == "uses":
                    uses = int(text)
                    pts = data["points"]
                    me = await bot.get_me()
                    link = await create_gift_link(pts, uses, me.username)
                    admin_pending.pop(uid)
                    await message.reply(
                        f"🎁 <b>تم إنشاء رابط الهدية!</b>\n\n"
                        f"🔗 الرابط:\n<code>{link}</code>\n\n"
                        f"💰 النقاط: <b>{pts}</b> لكل استخدام\n"
                        f"🔄 الاستخدامات: <b>{uses}</b> مرة",
                        reply_markup=back_to_admin_kb())

            elif action == "broadcast":
                pts = int(text)
                async with aiosqlite.connect(DB_PATH) as db:
                    cur = await db.execute("SELECT user_id FROM users")
                    users = await cur.fetchall()
                    for u in users:
                        await add_points(u[0], pts)
                admin_pending.pop(uid)
                await message.reply(
                    f"🎉 <b>تم إرسال النقاط!</b>\n"
                    f"✅ تم إضافة <b>{pts}</b> نقطة لـ <b>{len(users)}</b> مستخدم",
                    reply_markup=back_to_admin_kb())

            elif action == "promotemod":
                try:
                    target_id = int(text)
                    await promote_moderator(target_id)
                    admin_pending.pop(uid)
                    await message.reply(
                        f"✅ تم ترقية المستخدم <code>{target_id}</code> لمشرف!",
                        reply_markup=back_to_admin_kb())
                except ValueError:
                    await message.reply("❌ يرجى إرسال ID صحيح (أرقام فقط)")

            elif action == "demotemod":
                try:
                    target_id = int(text)
                    await demote_moderator(target_id)
                    admin_pending.pop(uid)
                    await message.reply(
                        f"✅ تم إزالة المشرف <code>{target_id}</code>!",
                        reply_markup=back_to_admin_kb())
                except ValueError:
                    await message.reply("❌ يرجى إرسال ID صحيح (أرقام فقط)")

            elif action == "banuser":
                try:
                    target_id = int(text)
                    await ban_user(target_id)
                    admin_pending.pop(uid)
                    await message.reply(
                        f"🚫 تم حظر المستخدم <code>{target_id}</code>!",
                        reply_markup=back_to_admin_kb())
                except ValueError:
                    await message.reply("❌ يرجى إرسال ID صحيح (أرقام فقط)")

            elif action == "unbanuser":
                try:
                    target_id = int(text)
                    await unban_user(target_id)
                    admin_pending.pop(uid)
                    await message.reply(
                        f"✅ تم فك حظر المستخدم <code>{target_id}</code>!",
                        reply_markup=back_to_admin_kb())
                except ValueError:
                    await message.reply("❌ يرجى إرسال ID صحيح (أرقام فقط)")

            elif action == "entrypoints":
                global ENTRY_POINTS
                ENTRY_POINTS = int(text)
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تعيين نقاط الدخول: <b>{text}</b> نقطة",
                    reply_markup=back_to_admin_kb())

            elif action == "setdev":
                global DEV_CONTACT
                DEV_CONTACT = text
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تعيين حساب المطور: <b>{text}</b>",
                    reply_markup=back_to_admin_kb())

            elif action in ["addstars", "addplay"]:
                category = "stars" if action == "addstars" else "play"
                if step == "name":
                    admin_pending[uid]["name"] = text
                    admin_pending[uid]["step"] = "price"
                    await message.reply(
                        f"📝 <b>الخطوة 2/3:</b>\n"
                        f"أرسل سعر المنتج (بالنقاط):",
                        reply_markup=back_to_admin_kb())
                elif step == "price":
                    price = int(text)
                    admin_pending[uid]["price"] = price
                    admin_pending[uid]["step"] = "stock"
                    await message.reply(
                        f"📝 <b>الخطوة 3/3:</b>\n"
                        f"أرسل الكمية المتاحة:",
                        reply_markup=back_to_admin_kb())
                elif step == "stock":
                    stock = int(text)
                    name = data["name"]
                    price = data["price"]
                    await add_product(category, name, price, stock)
                    admin_pending.pop(uid)
                    emoji = "⭐" if category == "stars" else "🎮"
                    await message.reply(
                        f"✅ <b>تم إضافة المنتج!</b>\n\n"
                        f"{emoji} الاسم: <b>{name}</b>\n"
                        f"💰 السعر: <b>{price}</b> نقطة\n"
                        f"📦 الكمية: <b>{stock}</b>",
                        reply_markup=back_to_admin_kb())

            elif action == "editprodname":
                pid = data["pid"]
                await update_product_name(pid, text)
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تعديل اسم المنتج إلى: <b>{text}</b>",
                    reply_markup=back_to_admin_kb())

            elif action == "editprodprice":
                pid = data["pid"]
                price = int(text)
                await update_product_price(pid, price)
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تعديل سعر المنتج إلى: <b>{price}</b> نقطة",
                    reply_markup=back_to_admin_kb())

            elif action == "editprodstock":
                pid = data["pid"]
                stock = int(text)
                await update_product_stock(pid, stock)
                admin_pending.pop(uid)
                await message.reply(
                    f"✅ تم تعديل كمية المنتج إلى: <b>{stock}</b>",
                    reply_markup=back_to_admin_kb())

        except Exception as e:
            logging.error(f"Error in handle_admin_input: {e}")
            await message.reply("❌ حدث خطأ، حاول مرة أخرى")

    @dp.callback_query(F.data.startswith("lang:"))
    async def change_language(cb: types.CallbackQuery):
        global bot
        new_lang = cb.data.split(":", 1)[1]
        await set_user_language(cb.from_user.id, new_lang)
        
        points = await get_points(cb.from_user.id)
        points_word = await get_points_word()
        me = await bot.get_me()
        invite_link = f"https://t.me/{me.username}?start={cb.from_user.id}"
        username_display = f"@{cb.from_user.username}" if cb.from_user.username else f"ID: {cb.from_user.id}"
        
        user_pages[cb.from_user.id] = "main"
        
        if new_lang == "ar":
            text = (
                f"🎁 <b>بوت الجوائز والمكافآت</b> 🎁\n\n"
                f"👋 مرحباً <b>{cb.from_user.first_name}</b>\n"
                f"👤 {username_display}\n\n"
                f"✅ تم تغيير اللغة إلى العربية!\n\n"
                f"اجمع {points_word} واحصل على جوائز مذهلة بسهولة.\n\n"
                f"🔗 <b>رابط الدعوة الخاص بك:</b>\n"
                f"<code>{invite_link}</code>\n\n"
                f"💰 رصيدك الحالي: <b>{points_display(points)}</b> {points_word}\n"
            )
        else:
            text = (
                f"🎁 <b>Бот награды и подарки</b> 🎁\n\n"
                f"👋 Привет <b>{cb.from_user.first_name}</b>\n"
                f"👤 {username_display}\n\n"
                f"✅ Язык изменен на русский!\n\n"
                f"Собирайте {points_word} и получайте удивительные награды легко.\n\n"
                f"🔗 <b>Ваша реферальная ссылка:</b>\n"
                f"<code>{invite_link}</code>\n\n"
                f"💰 Ваш баланс: <b>{points_display(points)}</b> {points_word}\n"
            )
        
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), new_lang))
        await cb.answer(get_text("lang_changed", new_lang))

    @dp.callback_query(F.data == "noop")
    async def noop_handler(cb: types.CallbackQuery):
        await cb.answer()


async def main():
    global bot, dp
    
    if PROXY_URL:
        session = AiohttpSession(proxy=PROXY_URL)
        bot = Bot(token=API_TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))
    else:
        bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    dp = Dispatcher()
    
    register_handlers(dp)
    
    await init_db()
    print("✅ Bot is running...")
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
