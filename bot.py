# bot.py
# pip install aiogram aiosqlite
# python bot.py

import asyncio
import aiosqlite
from typing import Optional, List
from aiogram import Bot, Dispatcher, types, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from datetime import datetime
import logging
import os

# ====== CONFIG ======
API_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
DB_PATH = "bot_database.db"
INVITER_POINTS = 1
ADMIN_USERNAME = "@ii58n"
POINTS_WORD = "نقاط"
ENTRY_POINTS = 0
DEV_CONTACT = "@ii58n"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# نظام تتبع الصفحات السابقة
user_pages: dict = {}
admin_pages: dict = {}
admin_prev_pages: dict = {}  # لحفظ الصفحة السابقة

# ================= TRANSLATIONS =================

TRANSLATIONS = {
    "ar": {
        "welcome": "👋 مرحباً بك في البوت!",
        "shop": "🛍️ المتجر",
        "profile": "👤 معلومات حسابك",
        "leaderboard": "المتصدرين",
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
    
    # تلقائي: كشف لغة الهاتف
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
    """اختر اسم المنتج بناءً على لغة المستخدم"""
    if language == "ru" and name_ru:
        return name_ru
    return name_ar


async def get_points_word() -> str:
    """جلب كلمة النقاط من قاعدة البيانات"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT value FROM settings WHERE key='points_word'")
            result = await cur.fetchone()
            return result[0] if result else "نقاط"
    except:
        return "نقاط"


async def set_points_word(word: str):
    """حفظ كلمة النقاط في قاعدة البيانات"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings(key, value) VALUES('points_word', ?)", (word,))
        await db.commit()


async def get_daily_gift_amount() -> int:
    """جلب كمية الهديّة اليومية من قاعدة البيانات"""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT value FROM settings WHERE key='daily_gift_amount'")
            result = await cur.fetchone()
            return int(result[0]) if result else 1
    except:
        return 1


async def set_daily_gift_amount(amount: int):
    """حفظ كمية الهديّة اليومية في قاعدة البيانات"""
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
            (user_id, datetime.utcnow().isoformat(), reason))
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
            (user_id, datetime.utcnow().isoformat()))
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
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        last_claim_date = last_claim.replace(hour=0, minute=0, second=0, microsecond=0)
        
        return last_claim_date < today


async def claim_daily_gift(user_id: int) -> bool:
    if not await can_claim_daily_gift(user_id):
        return False
    
    gift_amount = await get_daily_gift_amount()
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO daily_gifts(user_id, last_claim_date) VALUES(?,?)",
            (user_id, datetime.utcnow().isoformat()))
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
    import random
    import string
    link_code = ''.join(
        random.choices(string.ascii_letters + string.digits, k=8))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO gift_links(link_code, points_per_use, max_uses, created_date) VALUES(?,?,?,?)",
            (link_code, points, max_uses, datetime.utcnow().isoformat()))
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
            (user_id, lid, datetime.utcnow().isoformat()))
        await db.commit()
        return (True, f"تم إضافة {points} نقطة!")


# ================= USERS =================


async def ensure_user(user_id: int, inviter: Optional[int] = None) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id=?",
                               (user_id, ))
        if not await cur.fetchone():
            await db.execute(
                "INSERT INTO users(user_id, points, inviter, join_date) VALUES(?,?,?,?)",
                (user_id, 0, inviter, datetime.utcnow().isoformat()))
            await db.commit()
            return True
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
        await db.execute(
            "UPDATE products SET stock = stock - 1 WHERE id=? AND stock>0",
            (pid, ))
        await db.commit()


async def add_product(category: str,
                      name: str,
                      name_ru: str,
                      price: int,
                      stock: int,
                      button_id: Optional[int] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO products(category,name,name_ru,price_points,stock,button_id) VALUES(?,?,?,?,?,?)",
            (category, name, name_ru, price, stock, button_id))
        await db.commit()


async def notify_all_users_new_product(product_name: str, price: int, category: str):
    """إرسال إشعار لجميع المستخدمين عند إضافة منتج جديد"""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users")
        users = await cur.fetchall()
    
    notification_text = f"""
🆕 <b>منتج جديد متاح!</b>

🛍️ <b>المنتج:</b> {product_name}
السعر: {price} نقطة
📂 <b>القسم:</b> {category}

👉 اذهب إلى المتجر الآن لشراء المنتج!
    """.strip()
    
    failed_count = 0
    for user in users:
        try:
            await bot.send_message(user[0], notification_text)
            await asyncio.sleep(0.05)  # تأخير بسيط لتجنب حظر البوت
        except Exception as e:
            failed_count += 1
            logging.warning(f"فشل إرسال إشعار للمستخدم {user[0]}: {e}")
    
    logging.info(f"تم إرسال إشعار المنتج الجديد لـ {len(users) - failed_count} من {len(users)} مستخدم")


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


async def update_product_name_ru(pid: int, new_name_ru: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE products SET name_ru=? WHERE id=?",
                         (new_name_ru, pid))
        await db.commit()


# ================= CODES =================


async def add_codes(product_id: int, codes: List[str]):
    async with aiosqlite.connect(DB_PATH) as db:
        for c in codes:
            c2 = c.strip()
            if not c2:
                continue
            await db.execute(
                "INSERT OR IGNORE INTO codes(product_id,code_text,used) VALUES(?,?,0)",
                (product_id, c2))
        await db.commit()


async def get_unused_code(product_id: int) -> Optional[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, code_text FROM codes WHERE product_id=? AND used=0 LIMIT 1",
            (product_id, ))
        row = await cur.fetchone()

        if row:
            cid, code = row
            await db.execute("UPDATE codes SET used=1 WHERE id=?", (cid, ))
            await db.commit()
            return code

    return None


async def record_transaction(user_id: int, product_id: int,
                             delivered_text: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO transactions(user_id,product_id,timestamp,delivered_text) VALUES(?,?,?,?)",
            (user_id, product_id, datetime.utcnow().isoformat(),
             delivered_text))
        await db.commit()


# ================= KEYBOARDS =================


def main_menu_kb(is_admin_user: bool = False, lang: str = "ar"):
    buttons = [
        [InlineKeyboardButton(text=get_text("shop", lang), callback_data="menu:shop")],
        [
            InlineKeyboardButton(text=get_text("profile", lang), callback_data="menu:profile"),
            InlineKeyboardButton(text=get_text("invite", lang),
                                 callback_data="menu:invite")
        ],
        [
            InlineKeyboardButton(text=f"⭐ {get_text('daily_gift', lang)}", callback_data="menu:daily_gift")
        ],
        [
            InlineKeyboardButton(text=get_text("help", lang), callback_data="menu:help")
        ]
    ]

    if is_admin_user:
        buttons.append([
            InlineKeyboardButton(text=get_text("control_panel", lang),
                                 callback_data="admin_mainmenu")
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def category_kb(lang: str = "ar"):
    buttons = [[
        InlineKeyboardButton(text=get_text("stars", lang), callback_data="cat:stars")
    ],
               [
                   InlineKeyboardButton(text=get_text("play", lang),
                                        callback_data="cat:play")
               ],
               [
                   InlineKeyboardButton(text=get_text("all_products", lang),
                                        callback_data="cat:all")
               ],
               [
                   InlineKeyboardButton(text=get_text("back", lang),
                                        callback_data="back:")
               ]]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def product_kb(pid: int, price: int, user_points: int, lang: str = "ar"):
    can_buy = user_points >= price
    if can_buy:
        buy_text = get_text("buy_now", lang)
    else:
        needed = price - user_points
        buy_text = f"{get_text('no_points', lang)} {needed} {get_text('points', lang)}"

    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=buy_text,
            callback_data=f"buy:{pid}" if can_buy else "cant_buy")
    ], [InlineKeyboardButton(text=get_text("back_shop", lang), callback_data="back:")]
                                                 ])


def back_to_main_kb(lang: str = "ar"):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=get_text("back", lang),
                             callback_data="back:")
    ]])


def back_kb(lang: str = "ar"):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=get_text("back", lang),
                             callback_data="back:")
    ]])


def back_to_admin_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن",
                             callback_data="admin_mainmenu")
    ]])


# ================= START =================


@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    lang = await get_user_language(user_id)
    
    if await is_user_banned(user_id):
        banned_text = get_text("banned", lang)
        contact_text = get_text("contact_admin", lang)
        await message.reply(f"{banned_text}\n\n{contact_text}: {ADMIN_USERNAME}")
        return

    text = message.text or ""
    args = text.partition(" ")[2].strip()

    gift_code = None
    inviter = None

    if args.startswith("gift_"):
        gift_code = args
    elif args.isdigit():
        inviter = int(args)

    new_user = await ensure_user(user_id, inviter)

    # إرسال إشعار للإدارة عند تسجيل مستخدم جديد
    logging.info(f"new_user: {new_user}, user_id: {user_id}, ADMIN_ID: {ADMIN_ID}")
    if new_user:
        total_users = await get_total_users()
        banned_users = await get_banned_users_count()
        user_profile_link = f"<a href='tg://user?id={user_id}'>{message.from_user.first_name}</a>"
        user_info = f"""
🆕 <b>مستخدم جديد تسجل!</b>

👤 الاسم: {user_profile_link}
🆔 المعرّف: <code>{message.from_user.id}</code>
📱 اليوزر: @{message.from_user.username or 'بدون يوزر'}
⏰ الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}

📊 <b>إحصائيات البوت الحالية:</b>
👥 إجمالي المستخدمين: <b>{total_users}</b>
🚫 المستخدمين المحظورين: <b>{banned_users}</b>
        """.strip()
        try:
            logging.info(f"محاولة إرسال إشعار للـ ADMIN_ID {ADMIN_ID}")
            result = await bot.send_message(ADMIN_ID, user_info)
            logging.info(f"تم إرسال الإشعار بنجاح: {result.message_id}")
        except Exception as e:
            logging.error(f"خطأ في إرسال الإشعار للـ {ADMIN_ID}: {e}")
            import traceback
            logging.error(traceback.format_exc())

    if gift_code:
        logging.info(f"محاولة استخدام رابط هدايا: {gift_code}")
        success, gift_msg = await use_gift_link(message.from_user.id,
                                                gift_code)
        logging.info(f"نتيجة استخدام الرابط: success={success}, msg={gift_msg}")
        if success:
            await message.reply(f"🎉 <b>رابط الهدايا!</b>\n"
                                 f"✅ {gift_msg}\n"
                                 f"شكراً لاستخدامك!")
            
            # إرسال إشعار للإدارة عند استخدام رابط الهدايا
            user_total_points = await get_points(message.from_user.id)
            gift_user_link = f"<a href='tg://user?id={message.from_user.id}'>{message.from_user.first_name}</a>"
            gift_notification = f"""
🎁 <b>تم استخدام رابط هدايا!</b>

👤 المستخدم: {gift_user_link}
🆔 المعرّف: <code>{message.from_user.id}</code>
📱 اليوزر: @{message.from_user.username or 'بدون يوزر'}

الرسالة: {gift_msg}
إجمالي النقاط: <b>{user_total_points}</b>
⏰ الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
            """.strip()
            try:
                logging.info(f"محاولة إرسال إشعار الهدايا للـ {ADMIN_ID}")
                result = await bot.send_message(ADMIN_ID, gift_notification)
                logging.info(f"تم إرسال إشعار الهدايا بنجاح: {result.message_id}")
            except Exception as e:
                logging.error(f"خطأ في إرسال إشعار الهدايا: {e}")
                import traceback
                logging.error(traceback.format_exc())
    elif new_user and inviter and inviter != message.from_user.id:
        await ensure_user(inviter)
        await add_points(inviter, INVITER_POINTS)
        points_word = await get_points_word()
        try:
            await bot.send_message(
                inviter, f"🎉 <b>مبروك!</b>\n\n"

                f"صديقك <b>{message.from_user.first_name}</b> انضم عبر رابط دعوتك!\n"
                f"➕ حصلت على <b>{INVITER_POINTS}</b> {points_word}")
        except:
            pass

    points = await get_points(message.from_user.id)
    points_word = await get_points_word()
    
    # كشف لغة الهاتف التلقائية
    phone_lang = message.from_user.language_code or "ar"
    lang = await get_user_language(message.from_user.id, phone_lang)
    
    # إذا كان مستخدم جديد وكان هاتفه روسي أو عربي، تعيين اللغة تلقائياً
    if new_user and phone_lang:
        if phone_lang.startswith("ru"):
            lang = "ru"
            await set_user_language(message.from_user.id, "ru")
        elif phone_lang.startswith("ar"):
            lang = "ar"
            await set_user_language(message.from_user.id, "ar")
    
    # الحصول على رابط الدعوة
    me = await bot.get_me()
    invite_link = f"https://t.me/{me.username}?start={message.from_user.id}"
    username_display = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    if lang == "ar":
        welcome_text = (
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
        welcome_text = (
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
    await message.reply(welcome_text,
                         reply_markup=main_menu_kb(
                             is_admin(message.from_user.id), lang))


# ================= MENU HANDLERS =================


@dp.callback_query(F.data.startswith("menu:"))
async def menu_handler(cb: types.CallbackQuery):
    action = cb.data.split(":", 1)[1]
    lang = await get_user_language(cb.from_user.id)

    if action == "main":
        # تسجيل الصفحة الحالية
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
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))  # type: ignore

    elif action == "shop":
        user_pages[cb.from_user.id] = "shop"
        points = await get_points(cb.from_user.id)
        points_word = await get_points_word()
        text = (f"{get_text('store', lang)}\n"
                f"{get_text('my_points', lang)}: <b>{points_display(points)}</b> {points_word}\n\n"
                f"{get_text('choose_category', lang)}:")
        await cb.message.edit_text(text, reply_markup=category_kb(lang))  # type: ignore

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
        
        # تسجيل الصفحة
        user_pages[cb.from_user.id] = "profile"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text("leaderboard", lang), callback_data="menu:leaderboard")],
            [InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")]
        ])
        await cb.message.edit_text(text, reply_markup=kb)  # type: ignore

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
        await cb.message.edit_text(text, reply_markup=back_to_main_kb(lang))  # type: ignore

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
        await cb.message.edit_text(text, reply_markup=back_to_main_kb(lang))  # type: ignore

    elif action == "daily_gift":
        user_pages[cb.from_user.id] = "daily_gift"
        can_claim = await can_claim_daily_gift(cb.from_user.id)
        gift_amount = await get_daily_gift_amount()
        if can_claim:
            text = f"{get_text('daily_gift_title', lang)}\n✨ {'تهانينا! هديّتك اليومية متاحة الآن!' if lang == 'ar' else 'Поздравляем! Ваш ежедневный подарок готов!'}\n\n🎉 {'اضغط للحصول على' if lang == 'ar' else 'Нажмите для получения'} <b>{gift_amount} €</b>"
            kb = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=get_text("get_gift", lang), callback_data="claim_daily_gift")
            ], [
                InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")
            ]])
        else:
            text = f"{get_text('daily_gift_title', lang)}\n{get_text('gift_already_claimed', lang)}!"
            kb = back_to_main_kb(lang)
        await cb.message.edit_text(text, reply_markup=kb)  # type: ignore

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
    """معالج زر الرجوع - يرجع إلى آخر صفحة"""
    lang = await get_user_language(cb.from_user.id)
    
    # فحص الصفحة الحالية - هل هي صفحة عادية أم صفحة إدمن
    last_user_page = user_pages.get(cb.from_user.id, None)
    is_in_user_page = last_user_page is not None and last_user_page != "main"
    
    # إذا كان في صفحة عادية (ليست القائمة الرئيسية)
    if is_in_user_page:
        # رجع للقائمة الرئيسية دائماً من الصفحات العادية
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
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))  # type: ignore
        await cb.answer()
        return
    
    # تحقق إذا كان هذا مسؤول وفي صفحة إدمن
    if await is_admin_or_moderator(cb.from_user.id):
        last_admin_page = admin_prev_pages.get(cb.from_user.id, "main")
        if last_admin_page == "main":
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ تعيين كلمة نقاط",
                                         callback_data="admin_setword"),
                    InlineKeyboardButton(text="🔢 تعيين نقاط الدخول",
                                         callback_data="admin_entrypoints")
                ],
                [
                    InlineKeyboardButton(text="👤 تعيين حساب المطور",
                                         callback_data="admin_setdev"),
                    InlineKeyboardButton(text="🎁 صنع روابط تمويل",
                                         callback_data="admin_giftlink")
                ],
                [
                    InlineKeyboardButton(text="📦 جميع السلع",
                                         callback_data="admin_productsmenu"),
                    InlineKeyboardButton(text="📦 جميع المنتجات",
                                         callback_data="admin_allproducts")
                ],
                [
                    InlineKeyboardButton(text="🏪 أقسام المتجر",
                                         callback_data="admin_categories"),
                    InlineKeyboardButton(text="🎟️ الخصم",
                                         callback_data="admin_coupons")
                ],
                [
                    InlineKeyboardButton(text="🎁 صنع رابط هدايا",
                                         callback_data="admin_giftlink2"),
                    InlineKeyboardButton(text="📤 إرسال نقاط",
                                         callback_data="admin_broadcast")
                ],
                [
                    InlineKeyboardButton(text="📊 الإحصائيات",
                                         callback_data="admin_stats")
                ],
                [
                    InlineKeyboardButton(text="⚙️ الإعدادات",
                                         callback_data="admin_settings")
                ],
                [
                    InlineKeyboardButton(text="🔙 القائمة الرئيسية",
                                         callback_data="exit_admin:")
                ]
            ])
            await cb.message.edit_text(  # type: ignore
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"
                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)
        elif last_admin_page == "settings":
            admin_prev_pages[cb.from_user.id] = "main"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ تعيين كلمة نقاط",
                                         callback_data="admin_setword"),
                    InlineKeyboardButton(text="🔢 تعيين نقاط الدخول",
                                         callback_data="admin_entrypoints")
                ],
                [
                    InlineKeyboardButton(text="👤 تعيين حساب المطور",
                                         callback_data="admin_setdev"),
                    InlineKeyboardButton(text="🎁 صنع روابط تمويل",
                                         callback_data="admin_giftlink")
                ],
                [
                    InlineKeyboardButton(text="📦 جميع السلع",
                                         callback_data="admin_productsmenu"),
                    InlineKeyboardButton(text="📦 جميع المنتجات",
                                         callback_data="admin_allproducts")
                ],
                [
                    InlineKeyboardButton(text="🏪 أقسام المتجر",
                                         callback_data="admin_categories"),
                    InlineKeyboardButton(text="🎟️ الخصم",
                                         callback_data="admin_coupons")
                ],
                [
                    InlineKeyboardButton(text="🎁 صنع رابط هدايا",
                                         callback_data="admin_giftlink2"),
                    InlineKeyboardButton(text="📤 إرسال نقاط",
                                         callback_data="admin_broadcast")
                ],
                [
                    InlineKeyboardButton(text="📊 الإحصائيات",
                                         callback_data="admin_stats")
                ],
                [
                    InlineKeyboardButton(text="⚙️ الإعدادات",
                                         callback_data="admin_settings")
                ],
                [
                    InlineKeyboardButton(text="🔙 القائمة الرئيسية",
                                         callback_data="exit_admin:")
                ]
            ])
            admin_pages[cb.from_user.id] = "main"
            await cb.message.edit_text(  # type: ignore
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"
                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)
        elif last_admin_page in ["banmenu", "modmenu", "manageproducts"]:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="✏️ تعيين كلمة نقاط",
                                         callback_data="admin_setword"),
                    InlineKeyboardButton(text="🔢 تعيين نقاط الدخول",
                                         callback_data="admin_entrypoints")
                ],
                [
                    InlineKeyboardButton(text="👤 تعيين حساب المطور",
                                         callback_data="admin_setdev"),
                    InlineKeyboardButton(text="🎁 صنع روابط تمويل",
                                         callback_data="admin_giftlink")
                ],
                [
                    InlineKeyboardButton(text="📦 جميع السلع",
                                         callback_data="admin_productsmenu"),
                    InlineKeyboardButton(text="📦 جميع المنتجات",
                                         callback_data="admin_allproducts")
                ],
                [
                    InlineKeyboardButton(text="🏪 أقسام المتجر",
                                         callback_data="admin_categories"),
                    InlineKeyboardButton(text="🎟️ الخصم",
                                         callback_data="admin_coupons")
                ],
                [
                    InlineKeyboardButton(text="🎁 صنع رابط هدايا",
                                         callback_data="admin_giftlink2"),
                    InlineKeyboardButton(text="📤 إرسال نقاط",
                                         callback_data="admin_broadcast")
                ],
                [
                    InlineKeyboardButton(text="📊 الإحصائيات",
                                         callback_data="admin_stats")
                ],
                [
                    InlineKeyboardButton(text="⚙️ الإعدادات",
                                         callback_data="admin_settings")
                ],
                [
                    InlineKeyboardButton(text="🔙 القائمة الرئيسية",
                                         callback_data="exit_admin:")
                ]
            ])
            await cb.message.edit_text(  # type: ignore
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"
                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)
        else:
            await cb.answer()
            return
        await cb.answer()
        return


@dp.callback_query(F.data == "exit_admin:")
async def exit_admin_handler(cb: types.CallbackQuery):
    """معالج للخروج من لوحة التحكم والعودة للقائمة الرئيسية"""
    lang = await get_user_language(cb.from_user.id)
    
    # حذف التتبع
    admin_pages.pop(cb.from_user.id, None)
    admin_prev_pages.pop(cb.from_user.id, None)
    user_pages[cb.from_user.id] = "main"
    
    # عرض القائمة الرئيسية
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
    try:
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))  # type: ignore
    except Exception as e:
        logging.warning(f"خطأ في تحديث الرسالة: {e}")
        await cb.answer("✅ تم الخروج من لوحة الإدمن", show_alert=False)
    await cb.answer()
    
    last_page = user_pages.get(cb.from_user.id, "main")
    
    if last_page == "main":
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
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))  # type: ignore
    elif last_page == "shop":
        points = await get_points(cb.from_user.id)
        points_word = await get_points_word()
        text = (f"{get_text('store', lang)}\n"
                f"{get_text('my_points', lang)}: <b>{points_display(points)}</b> {points_word}\n\n"
                f"{get_text('choose_category', lang)}:")
        await cb.message.edit_text(text, reply_markup=category_kb(lang))  # type: ignore
    elif last_page == "profile":
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
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=get_text("leaderboard", lang), callback_data="menu:leaderboard")],
            [InlineKeyboardButton(text=get_text("back", lang), callback_data="back:")]
        ])
        await cb.message.edit_text(text, reply_markup=kb)  # type: ignore
    elif last_page in ["leaderboard", "invite", "daily_gift", "help"]:
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
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))  # type: ignore
    else:
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
        await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), lang))  # type: ignore
    
    await cb.answer()


@dp.callback_query(F.data == "claim_daily_gift")
async def claim_daily_gift_cb(cb: types.CallbackQuery):
    lang = await get_user_language(cb.from_user.id)
    success = await claim_daily_gift(cb.from_user.id)
    
    if success:
        points = await get_points(cb.from_user.id)
        gift_amount = await get_daily_gift_amount()
        text = (f"🎉 {'<b>تم الحصول على الهديّة!</b>' if lang == 'ar' else '<b>Подарок получен!</b>'}\n"
                f"✨ {'لقد حصلت على' if lang == 'ar' else 'Вы получили'} <b>{gift_amount} €</b>!\n\n"
                f"💰 {'رصيدك الحالي' if lang == 'ar' else 'Ваш баланс'}: <b>{points_display(points)}</b> €\n")
        await cb.message.edit_text(text, reply_markup=back_to_main_kb(lang))
        msg = "✅ تم الحصول على الهديّة!" if lang == "ar" else "✅ Подарок получен!"
        await cb.answer(msg, show_alert=True)
    else:
        msg = "⏰ تم استلام الهديّة بالفعل اليوم!" if lang == "ar" else "⏰ Вы уже получили подарок сегодня!"
        await cb.answer(msg, show_alert=True)


# ================= COMMANDS =================


@dp.message(Command("profile"))
async def profile_cmd(message: types.Message):
    stats = await get_user_stats(message.from_user.id)

    rank = "🥉 مبتدئ"
    if stats["points"] >= 100:
        rank = "💎 ماسي"
    elif stats["points"] >= 50:
        rank = "🥇 ذهبي"
    elif stats["points"] >= 20:
        rank = "🥈 فضي"

    text = (f"👤 <b>حسابي</b>\n"
            f"🆔 المعرف: <code>{message.from_user.id}</code>\n"
            f"👤 الاسم: <b>{message.from_user.first_name}</b>\n\n"
            f"📊 <b>الإحصائيات</b>\n"            f"النقاط: <b>{stats['points']}</b>\n 💰"
            f"🏅 الرتبة: {rank}\n"
            f"👥 الأصدقاء المدعوين: <b>{stats['invited_count']}</b>\n"
            f"🛒 عدد المشتريات: <b>{stats['purchases']}</b>\n")
    await message.reply(text, reply_markup=back_to_admin_kb())


@dp.message(Command("invite"))
async def invite_cmd(message: types.Message):
    me = await bot.get_me()
    stats = await get_user_stats(message.from_user.id)
    points_word = await get_points_word()

    invite_link = f"https://t.me/{me.username}?start={message.from_user.id}"

    points_word = await get_points_word()
    text = (
        f"👥 <b>دعوة الأصدقاء</b>\n"
        f"🎁 ادعُ أصدقاءك واحصل على <b>{INVITER_POINTS} {points_word}</b>\n"
        f"   لكل صديق ينضم عبر رابطك!\n\n"
        f"🔗 <b>رابط دعوتك:</b>\n"
        f"<code>{invite_link}</code>\n\n"

        f"👆 انقر على الرابط لنسخه\n"
        f"📊 أصدقاؤك المدعوين: <b>{stats['invited_count']}</b>\n"
        f"{points_word} الدعوة المكتسبة: <b>{stats['invited_count'] * INVITER_POINTS}</b>"
    )
    await message.reply(text, reply_markup=back_to_admin_kb())


@dp.message(Command("lang"))
async def lang_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang:ar"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")
        ]
    ])
    
    lang = await get_user_language(message.from_user.id)
    text = get_text("select_lang", lang)
    await message.reply(text, reply_markup=kb)


@dp.callback_query(F.data.startswith("lang:"))
async def change_language(cb: types.CallbackQuery):
    new_lang = cb.data.split(":", 1)[1]
    await set_user_language(cb.from_user.id, new_lang)
    
    points = await get_points(cb.from_user.id)
    if new_lang == "ar":
        text = (
            f"🎁 <b>بوت الجوائز والمكافآت</b> 🎁\n\n"
            f"👋 مرحباً <b>{cb.from_user.first_name}</b>!\n"
            f"اجمع € واحصل على جوائز مذهلة بسهولة.\n\n"
            f"📌 <b>كيف يعمل البوت؟</b>\n"
            f"1️⃣ ادعُ أصدقاءك برابطك الخاص\n"
            f"2️⃣ احصل على € عن كل صديق ينضم\n"
            f"3️⃣ استبدل €ك بـ ⭐ نجوم تيليجرام و 🎮 بطاقات Google Play\n\n"
            f"🎁 كل صديق تقوم بدعوته يمكنك الحصول على <b>1 €</b>\n\n"
            f"💰 رصيدك الحالي: <b>{points_display(points)}</b> €\n"
        )
    else:
        text = (
            f"🎁 <b>Бот награды и подарки</b> 🎁\n\n"
            f"👋 Привет <b>{cb.from_user.first_name}</b>!\n"
            f"Собирайте € и получайте удивительные награды легко.\n\n"
            f"📌 <b>Как это работает?</b>\n"
            f"1️⃣ Пригласите своих друзей по вашей личной ссылке\n"
            f"2️⃣ Получайте € за каждого присоединившегося друга\n"
            f"3️⃣ Обменивайте € на ⭐ звезды Telegram и 🎮 карты Google Play\n\n"
            f"🎁 За каждого приглашённого друга вы получаете <b>1 €</b>\n\n"
            f"💰 Ваш баланс: <b>{points_display(points)}</b> €\n"
        )
    
    await cb.message.edit_text(text, reply_markup=main_menu_kb(is_admin(cb.from_user.id), new_lang))  # type: ignore
    await cb.answer()


@dp.message(Command("redeem"))
async def redeem_cmd(message: types.Message):
    text = message.text.strip()
    parts = text.split()

    if len(parts) < 2:
        await message.reply(f"🎁 <b>استرجاع رابط الهدايا</b>\n"
                             f"استخدم الأمر كالتالي:\n"
                             f"<code>/redeem الرابط</code>\n\n"

                             f"مثال:\n"
                             f"<code>/redeem AbcD1234</code>")
        return

    link_code = parts[1]
    success, message_text = await use_gift_link(message.from_user.id,
                                                link_code)

    if success:
        await message.reply(f"🎉 <b>تم بنجاح!</b>\n"
                             f"✅ {message_text}\n"
                             f"شكراً لاستخدامك هدايانا!")
    else:
        await message.reply(f"❌ <b>خطأ!</b>\n"
                             f"{message_text}")


# ================= CATEGORY =================


async def products_list_kb(products: list, category: str, language: str = "ar"):
    buttons = []
    points_word = await get_points_word()

    buttons.append([
        InlineKeyboardButton(text="💵 السعر", callback_data="header_info"),
        InlineKeyboardButton(text="ℹ️ الاسم", callback_data="header_info")
    ])

    for p in products:
        pid, cat, name_ar, name_ru, price, stock = p
        pname = get_product_name(name_ar, name_ru, language)
        buttons.append([
            InlineKeyboardButton(text=f"{price} {points_word}",
                                 callback_data=f"product:{pid}"),
            InlineKeyboardButton(text=f"{pname}",
                                 callback_data=f"product:{pid}")
        ])

    buttons.append([
        InlineKeyboardButton(text="🔙 رجوع للمتجر", callback_data="menu:shop")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.callback_query(F.data == "header_info")
async def header_info(cb: types.CallbackQuery):
    await cb.answer("اختر منتج للشراء 👇", show_alert=False)


@dp.callback_query(F.data == "noop")
async def noop_handler(cb: types.CallbackQuery):
    await cb.answer()  # لا تفعل شيء


@dp.callback_query(F.data.startswith("cat:"))
async def show_category(cb: types.CallbackQuery):
    name = cb.data.split(":", 1)[1]
    user_lang = await get_user_language(cb.from_user.id)
    user_pages[cb.from_user.id] = "shop"

    if name == "all":
        products = await list_products()
    elif name == "stars":
        products = await list_products("stars")
    else:
        products = await list_products(name)

    user_points = await get_points(cb.from_user.id)

    if not products:
        await cb.message.edit_text(
            f"🔥 - العروض التي يقدمها البوت ، 🔥\n"
            f"📭 لا توجد منتجات في هذا القسم حالياً\n\n"

            f"🔔 تابعنا لتكون أول من يعلم!",
            reply_markup=await category_kb())
        return await cb.answer()

    points_word = await get_points_word()
    products_text = (f"🔥 - العروض التي يقدمها البوت ، 🔥\n\n"

                     f"رصيدك: <b>{points_display(user_points)}</b> {points_word}\n\n"

                     f"👇 اختر المنتج للشراء:")

    await cb.message.edit_text(products_text,  # type: ignore
                               reply_markup=await products_list_kb(products, name, user_lang))
    await cb.answer()


# ================= PRODUCT DETAILS =================


@dp.callback_query(F.data.startswith("product:"))
async def show_product(cb: types.CallbackQuery):
    pid = int(cb.data.split(":", 1)[1])
    product = await get_product(pid)
    user_lang = await get_user_language(cb.from_user.id)
    user_pages[cb.from_user.id] = "shop"
    points_word = await get_points_word()

    if not product:
        return await cb.answer("❌ المنتج غير موجود", show_alert=True)

    _, cat, name_ar, name_ru, price, stock = product
    pname = get_product_name(name_ar, name_ru, user_lang)
    user_points = await get_points(cb.from_user.id)

    category_emoji = "⭐" if cat == "stars" else "🎮"
    category_name = "نجوم تيليجرام" if cat == "stars" else "Google Play"

    can_buy = user_points >= price and stock > 0

    text = (f"{category_emoji} <b>تفاصيل المنتج</b>\n"
            f"📦 <b>المنتج:</b> {pname}\n"
            f"📂 <b>القسم:</b> {category_name}\n"
            f"السعر: {price} {points_word}\n"
            f"📦 <b>الكمية:</b> {stock_indicator(stock)}\n"
            f"رصيدك: {points_display(user_points)} {points_word}\n\n")

    if stock <= 0:
        text += "❌ <b>عذراً، المنتج نفذ من المخزون</b>"
    elif user_points < price:
        text += f"🔒 <b>تحتاج {price - user_points} {points_word} إضافية</b>\n"
        text += f"💡 ادعُ أصدقاءك لتحصل على {points_word}!"
    else:
        text += "✅ <b>يمكنك شراء هذا المنتج!</b>"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ تأكيد الشراء" if can_buy else "🔒 غير متاح",
                callback_data=f"buy:{pid}" if can_buy else "cant_buy")
        ],
                         [
                             InlineKeyboardButton(
                                 text=f"🔙 رجوع لقسم {category_name}",
                                 callback_data=f"cat:{cat}")
                         ],
                         [
                             InlineKeyboardButton(text="🔙 رجوع",
                                                  callback_data="back:")
                         ]])

    await cb.message.edit_text(text, reply_markup=kb)  # type: ignore
    await cb.answer()


# ================= BUY =================


@dp.callback_query(F.data == "cant_buy")
async def cant_buy(cb: types.CallbackQuery):
    points_word = await get_points_word()
    await cb.answer(f"❌ {points_word}ك غير كافية! ادعُ أصدقاءك لتحصل على المزيد",
                    show_alert=True)


@dp.callback_query(F.data.startswith("buy:"))
async def buy(cb: types.CallbackQuery):
    pid = int(cb.data.split(":", 1)[1])
    product = await get_product(pid)

    if not product:
        return await cb.answer("❌ المنتج غير موجود", show_alert=True)

    _, cat, name, name_ru, price, stock = product

    if stock <= 0:
        return await cb.answer("❌ عذراً، المنتج نفذ من المخزون",
                               show_alert=True)

    user_points = await get_points(cb.from_user.id)

    if user_points < price:
        return await cb.answer(
            f"❌ تحتاج {price - user_points} نقطة إضافية للشراء",
            show_alert=True)

    delivered = name
    code_display = ""

    if cat == "play":
        delivered = f"{name}\n📞 تواصل معي للحصول على الكود"
        code_display = f"\n\n📞 <b>للحصول على الكود:</b>\n<b>تواصل معي: {DEV_CONTACT}</b>"

    ok = await add_points(cb.from_user.id, -price)
    if ok is False:
        return await cb.answer("❌ حدث خطأ أثناء خصم النقاط", show_alert=True)

    await decrement_stock(pid)
    await record_transaction(cb.from_user.id, pid, delivered)

    new_points = await get_points(cb.from_user.id)
    user_name = cb.from_user.first_name or "مستخدم"
    user_id = cb.from_user.id
    points_word = await get_points_word()

    success_text = (f"🎉 <b>تم الشراء بنجاح!</b>\n"
                    f"👤 <b>الاسم:</b> {user_name}\n"
                    f"🔢 <b>الـ ID:</b> <code>{user_id}</code>\n"
                    f"🛍️ <b>قام بشراء:</b> {name} 🧨\n"
                    f"💲 <b>بسعر:</b> {price} 🌟"
                    f"{code_display}\n"
                    f"💳 <b>رصيدك الجديد:</b> {points_display(new_points)}\n"
                    f"📞 <b>للدعم والتواصل:</b> {ADMIN_USERNAME}\n"
                    f"✨ شكراً لتعاملك معنا!")

    await cb.message.edit_text(success_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[  # type: ignore
        InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
    ]]))
    await cb.answer("✅ تمت العملية بنجاح!")
    
    # إرسال إشعار للإدارة عند الشراء
    buyer_profile_link = f"<a href='tg://user?id={user_id}'>{user_name}</a>"
    purchase_notification = f"""
🛒 <b>عملية شراء جديدة!</b>

👤 المشتري: {buyer_profile_link}
🆔 معرف المستخدم: <code>{user_id}</code>
📱 اليوزر: @{cb.from_user.username or 'بدون يوزر'}

🛍️ المنتج المشترى: <b>{name}</b>
💎 السعر: <b>{price} {points_word}</b>
النقاط المتبقية: <b>{points_display(new_points)}</b>

⏰ الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()
    try:
        await bot.send_message(ADMIN_ID, purchase_notification)
    except Exception as e:
        logging.error(f"خطأ في إرسال إشعار الشراء: {e}")


# ================= ADMIN =================


def is_admin(uid: int) -> bool:
    return uid == ADMIN_ID


async def is_admin_or_moderator(uid: int) -> bool:
    if uid == ADMIN_ID:
        return True
    return await is_moderator(uid)


admin_pending = {}


@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not await is_admin_or_moderator(message.from_user.id):
        return await message.reply("❌ بدوس لي في الي ملكش فيه 😆🤍")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ تعيين كلمة نقاط",
                                 callback_data="admin_setword"),
            InlineKeyboardButton(text="🔢 تعيين نقاط الدخول",
                                 callback_data="admin_entrypoints")
        ],
        [
            InlineKeyboardButton(text="👤 تعيين حساب المطور",
                                 callback_data="admin_setdev"),
            InlineKeyboardButton(text="🎁 صنع روابط تمويل",
                                 callback_data="admin_giftlink")
        ],
        [
            InlineKeyboardButton(text="📦 جميع السلع",
                                 callback_data="admin_productsmenu"),
            InlineKeyboardButton(text="📦 جميع المنتجات",
                                 callback_data="admin_allproducts")
        ],
        [
            InlineKeyboardButton(text="🏪 أقسام المتجر",
                                 callback_data="admin_categories"),
            InlineKeyboardButton(text="🎟️ الخصم",
                                 callback_data="admin_coupons")
        ],
        [
            InlineKeyboardButton(text="🎁 صنع رابط هدايا",
                                 callback_data="admin_giftlink2"),
            InlineKeyboardButton(text="📤 إرسال نقاط",
                                 callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton(text="🛑 حظر مستخدم",
                                 callback_data="admin_banmenu"),
            InlineKeyboardButton(text="👮 المشرفين",
                                 callback_data="admin_modmenu")
        ],
        [
            InlineKeyboardButton(text="📊 الإحصائيات",
                                 callback_data="admin_stats")
        ],
        [
            InlineKeyboardButton(text="⚙️ الإعدادات",
                                 callback_data="admin_settings")
        ],
        [
            InlineKeyboardButton(text="🔙 القائمة الرئيسية",
                                 callback_data="back:")
        ]
    ])

    is_main_admin = message.from_user.id == ADMIN_ID
    role_text = "المسؤول الرئيسي" if is_main_admin else "مشرف البوت"
    text = (f"⚙️ <b>لوحة التحكم</b>\n"
            f"👋 مرحباً أيها {role_text}\n\n"

            f"📌 اختر الإجراء المطلوب:")
    await message.reply(text, reply_markup=kb)


@dp.callback_query(F.data.startswith("adminprod:"))
async def admin_product_manage(cb: types.CallbackQuery):
    if not await is_admin_or_moderator(cb.from_user.id):
        return await cb.answer("❌ بدوس لي في الي ملكش فيه 😆🤍", show_alert=True)

    pid = int(cb.data.split(":", 1)[1])
    product = await get_product(pid)

    if not product:
        return await cb.answer("❌ المنتج غير موجود", show_alert=True)

    _, cat, name, price, stock = product
    cat_name = "نجوم" if cat == "stars" else "Google Play"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ تعديل الاسم",
                                 callback_data=f"prodsettings:name:{pid}")
        ],
        [
            InlineKeyboardButton(text="💎 تعديل السعر",
                                 callback_data=f"prodsettings:price:{pid}")
        ],
        [
            InlineKeyboardButton(text="📊 تعديل الكمية",
                                 callback_data=f"prodsettings:stock:{pid}")
        ],
        [
            InlineKeyboardButton(text="🗑️ حذف المنتج",
                                 callback_data=f"prodsettings:delete:{pid}")
        ],
        [
            InlineKeyboardButton(text="🔙 رجوع",
                                 callback_data="admin_manageproducts")
        ]
    ])

    await cb.message.edit_text(  # type: ignore
        f"📦 <b>إدارة المنتج</b>\n"
        f"🆔 ID: <code>{pid}</code>\n"
        f"📦 الاسم: <b>{name}</b>\n"
        f"💎 السعر: <b>{price}</b> نقطة\n"
        f"📊 الكمية: <b>{stock}</b>\n"
        f"📂 القسم: <b>{cat_name}</b>\n\n"

        f"اختر الإجراء المطلوب:",
        reply_markup=kb)
    await cb.answer()


@dp.callback_query(F.data.startswith("prodsettings:"))
async def product_settings_cb(cb: types.CallbackQuery):
    if not await is_admin_or_moderator(cb.from_user.id):
        return await cb.answer("❌ بدوس لي في الي ملكش فيه 😆🤍", show_alert=True)

    parts = cb.data.split(":")
    action = parts[1]
    pid = int(parts[2])
    uid = cb.from_user.id

    if action == "name":
        admin_pending[uid] = {"action": "editname_ar", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"✏️ <b>تعديل اسم المنتج</b>\n"
            f"<b>الخطوة 1/2:</b> أرسل الاسم الجديد <b>بالعربية</b>:",
            reply_markup=back_to_admin_kb())

    elif action == "price":
        admin_pending[uid] = {"action": "editprice", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"💎 <b>تعديل سعر المنتج</b>\n"
            f"أرسل السعر الجديد (بالنقاط):",
            reply_markup=back_to_admin_kb())

    elif action == "stock":
        admin_pending[uid] = {"action": "editstock", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"📊 <b>تعديل كمية المنتج</b>\n"
            f"أرسل الكمية الجديدة:",
            reply_markup=back_to_admin_kb())

    elif action == "delete":
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ نعم، احذف",
                                 callback_data=f"confirmdelete:{pid}"),
            InlineKeyboardButton(text="❌ إلغاء",
                                 callback_data=f"adminprod:{pid}")
        ]])
        await cb.message.edit_text(  # type: ignore
            f"⚠️ <b>تأكيد الحذف</b>\n"
            f"هل أنت متأكد من حذف هذا المنتج؟\n"
            f"سيتم حذف جميع الأكواد المرتبطة به أيضاً!",
            reply_markup=kb)

    await cb.answer()


@dp.callback_query(F.data.startswith("confirmdelete:"))
async def confirm_delete_product(cb: types.CallbackQuery):
    if not await is_admin_or_moderator(cb.from_user.id):
        return await cb.answer("❌ بدوس لي في الي ملكش فيه 😆🤍", show_alert=True)

    pid = int(cb.data.split(":", 1)[1])
    await remove_product(pid)

    await cb.message.edit_text(  # type: ignore
        f"🗑️ <b>تم حذف المنتج!</b>\n"
        f"تم حذف المنتج رقم <code>{pid}</code> وجميع أكواده بنجاح.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
        ]]))
    await cb.answer()


@dp.callback_query(F.data.startswith("admin_"))
async def admin_cb(cb: types.CallbackQuery):
    action = cb.data.split("_", 1)[1]
    uid = cb.from_user.id
    if not await is_admin_or_moderator(uid):
        return await cb.answer("❌ بدوس لي في الي ملكش فيه 😆🤍", show_alert=True)

    if action == "cancel":
        await cb.answer()
        return

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
        await cb.message.edit_text(text)  # type: ignore
        return await cb.answer()

    if action == "addstars":
        admin_pending[uid] = {"action": "addstars", "step": "name"}
        await cb.message.edit_text(  # type: ignore
            f"⭐ <b>إضافة منتج نجوم جديد</b>\n"
            f"📝 <b>الخطوة 1/3:</b>\n"
            f"أرسل اسم المنتج:",
            reply_markup=back_to_admin_kb())

    elif action == "addplay":
        admin_pending[uid] = {"action": "addplay", "step": "name"}
        await cb.message.edit_text(  # type: ignore
            f"🎮 <b>إضافة منتج Google Play جديد</b>\n"
            f"📝 <b>الخطوة 1/3:</b>\n"
            f"أرسل اسم المنتج:",
            reply_markup=back_to_admin_kb())

    elif action == "addpoints":
        admin_pending[uid] = {"action": "addpoints", "step": "user"}
        await cb.message.edit_text(  # type: ignore
            f"💰 <b>إضافة نقاط لمستخدم</b>\n"
            f"📝 <b>الخطوة 1/2:</b>\n"
            f"أرسل اسم المستخدم أو ID المستخدم الذي تريد إضافة النقاط إليه:",
            reply_markup=back_to_admin_kb())


    elif action == "setinviter":
        admin_pending[uid] = {"action": "setinviter", "step": "points"}
        await cb.message.edit_text(  # type: ignore
            f"🎁 <b>ضبط نقاط الدعوة</b>\n"
            f"أرسل عدد النقاط التي يحصل عليها الداعي عند دعوة صديق واحد:",
            reply_markup=back_to_admin_kb())

    elif action == "manageproducts":
        products = await list_products()
        if not products:
            await cb.message.edit_text("📭 لا توجد منتجات حالياً")
            return await cb.answer()

        buttons = []
        for p in products:
            pid, cat, name_ar, name_ru, price, stock = p
            pname = get_product_name(name_ar, name_ru, "ar")
            cat_emoji = "⭐" if cat == "stars" else "🎮"
            buttons.append([
                InlineKeyboardButton(
                    text=f"{cat_emoji} {pname} | {price} نقطة | متوفر: {stock}",
                    callback_data=f"adminprod:{pid}")
            ])
        buttons.append(
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")])

        admin_pages[cb.from_user.id] = "manageproducts"
        await cb.message.edit_text(  # type: ignore
            f"📦 <b>إدارة المنتجات</b>\n"
            f"اختر المنتج الذي تريد إدارته:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

    elif action == "settings":
        admin_prev_pages[cb.from_user.id] = admin_pages.get(cb.from_user.id, "main")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="👮 إدارة المشرفين",
                                     callback_data="admin_modmenu"),
                InlineKeyboardButton(text="🔐 إدارة الحظر",
                                     callback_data="admin_banmenu")
            ],
            [
                InlineKeyboardButton(text="📤 إرسال نقاط",
                                     callback_data="admin_broadcast"),
                InlineKeyboardButton(text="🎁 الهديّة اليومية",
                                     callback_data="admin_dailygift")
            ],
            [InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")]
        ])
        admin_pages[cb.from_user.id] = "settings"
        await cb.message.edit_text(  # type: ignore
            f"⚙️ <b>الإعدادات والإدارة</b>\n\n"
            f"👮 <b>إدارة المشرفين</b> - أضف أو احذف مشرفين\n"
            f"🔐 <b>إدارة الحظر</b> - حظر أو فك حظر المستخدمين\n\n"
            f"📤 <b>إرسال نقاط</b> - إضافة نقاط لجميع المستخدمين\n"
            f"🎁 <b>الهديّة اليومية</b> - تعديل مبلغ الهديّة اليومية\n\n"
            f"👇 اختر الإجراء المطلوب:",
            reply_markup=kb)

    elif action == "banmenu":
        admin_prev_pages[cb.from_user.id] = admin_pages.get(cb.from_user.id, "main")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🚫 حظر",
                                     callback_data="admin_banuser"),
                InlineKeyboardButton(text="✅ فك حظر",
                                     callback_data="admin_unbanuser")
            ],
            [
                InlineKeyboardButton(text="📋 قائمة المحظورين",
                                     callback_data="admin_listbanned")
            ],
            [InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")]
        ])
        admin_pages[cb.from_user.id] = "banmenu"
        await cb.message.edit_text(  # type: ignore
            f"🚫 <b>إدارة الحظر والقيود</b>\n\n"
            f"🚫 <b>حظر</b> - منع مستخدم من استخدام البوت\n"
            f"✅ <b>فك حظر</b> - السماح لمستخدم بالعودة\n\n"
            f"📋 <b>قائمة المحظورين</b> - عرض جميع المستخدمين المحظورين\n\n"
            f"👇 اختر الإجراء المطلوب:",
            reply_markup=kb)

    elif action == "modmenu":
        admin_prev_pages[cb.from_user.id] = admin_pages.get(cb.from_user.id, "main")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="⬆️ ترقية",
                                     callback_data="admin_promotemod"),
                InlineKeyboardButton(text="⬇️ إزالة",
                                     callback_data="admin_demotemod")
            ],
            [
                InlineKeyboardButton(text="📋 قائمة المشرفين",
                                     callback_data="admin_listmods")
            ],
            [InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")]
        ])
        admin_pages[cb.from_user.id] = "modmenu"
        await cb.message.edit_text(  # type: ignore
            f"👮 <b>إدارة فريق العمل</b>\n\n"
            f"⬆️ <b>ترقية</b> - جعل مستخدم مشرفاً على البوت\n"
            f"⬇️ <b>إزالة</b> - إزالة مشرف من فريق العمل\n\n"
            f"📋 <b>قائمة المشرفين</b> - عرض جميع المشرفين الحاليين\n\n"
            f"👇 اختر الإجراء المطلوب:",
            reply_markup=kb)

    elif action == "promotemod":
        admin_pending[uid] = {"action": "promotemod", "step": "user"}
        await cb.message.edit_text(  # type: ignore
            f"⬆️ <b>ترقية مشرف</b>\n"
            f"أرسل ID المستخدم الذي تريد ترقيته لمشرف:",
            reply_markup=back_to_admin_kb())

    elif action == "demotemod":
        admin_pending[uid] = {"action": "demotemod", "step": "user"}
        await cb.message.edit_text(  # type: ignore
            f"⬇️ <b>إزالة مشرف</b>\n"
            f"أرسل ID المشرف الذي تريد إزالته:",
            reply_markup=back_to_admin_kb())

    elif action == "listmods":
        mods = await get_moderators()
        if not mods:
            await cb.message.edit_text("📭 لا يوجد مشرفين حالياً",
                                   reply_markup=back_to_admin_kb())
            return await cb.answer()

        text = f"👮 <b>قائمة المشرفين</b>\n25\n\n"
        for m in mods:
            user_id, promoted_date = m
            text += f"🟢 <code>{user_id}</code>\n"

        await cb.message.edit_text(text, reply_markup=back_to_admin_kb())  # type: ignore

    elif action == "banuser":
        admin_pending[uid] = {"action": "banuser", "step": "user"}
        await cb.message.edit_text(  # type: ignore
            f"🚫 <b>حظر مستخدم</b>\n"
            f"أرسل ID المستخدم الذي تريد حظره:",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action == "unbanuser":
        admin_pending[uid] = {"action": "unbanuser", "step": "user"}
        await cb.message.edit_text(  # type: ignore
            f"✅ <b>فك حظر مستخدم</b>\n"
            f"أرسل ID المستخدم الذي تريد فك حظره:",
            reply_markup=back_to_admin_kb())

    elif action == "listbanned":
        banned = await get_banned_users()
        if not banned:
            await cb.message.edit_text("✅ لا يوجد مستخدمين محظورين")
            return await cb.answer()

        text = f"📋 <b>قائمة المحظورين</b>\n25\n\n"
        for b in banned:
            user_id, ban_date, reason = b
            text += f"🔴 <code>{user_id}</code>\n"

        await cb.message.edit_text(text)  # type: ignore

    elif action == "addbutton":
        admin_pending[uid] = {"action": "addbutton", "step": "name"}
        await cb.message.edit_text(  # type: ignore
            f"🌐 <b>إضافة زر جديد</b>\n"
            f"ما اسم الزر الجديد الذي تريد إضافته؟\n"
            f"مثال: تذويد السوشيال ميديا",
            reply_markup=back_to_admin_kb())

    elif action == "giftlink" or action == "giftlink2":
        admin_pending[uid] = {"action": "giftlink", "step": "points"}
        await cb.message.edit_text(
            f"🎁 <b>إنشاء رابط هدايا</b>\n"
            f"📝 <b>الخطوة 1/2:</b>\n"
            f"كم نقطة لكل استخدام للرابط؟",
            reply_markup=back_to_admin_kb())

    elif action == "setword":
        admin_pending[uid] = {"action": "setword"}
        await cb.message.edit_text(  # type: ignore
            f"✏️ <b>تعيين كلمة النقاط</b>\n"
            f"أرسل الكلمة التي تريد استخدامها:\n"
            f"مثال: نقطة، نقاط، ستار",
            reply_markup=back_to_admin_kb())

    elif action == "entrypoints":
        admin_pending[uid] = {"action": "entrypoints"}
        await cb.message.edit_text(  # type: ignore
            f"🔢 <b>تعيين نقاط الدخول</b>\n"
            f"كم نقطة يحصل عليها المستخدم الجديد عند التسجيل؟",
            reply_markup=back_to_admin_kb())

    elif action == "setdev":
        admin_pending[uid] = {"action": "setdev"}
        await cb.message.edit_text(  # type: ignore
            f"👤 <b>تعيين حساب المطور</b>\n"
            f"أرسل معرف المطور/الدعم:\n"
            f"مثال: @username",
            reply_markup=back_to_admin_kb())

    elif action == "dailygift":
        gift_amount = await get_daily_gift_amount()
        admin_pending[uid] = {"action": "setdailygift"}
        await cb.message.edit_text(
            f"🎁 <b>تعديل كمية الهديّة اليومية</b>\n"
            f"الكمية الحالية: <b>{gift_amount} €</b>\n\n"
            f"أرسل الكمية الجديدة (رقم فقط):",
            reply_markup=back_to_admin_kb())

    elif action == "allproducts":
        products = await list_products()
        if not products:
            await cb.message.edit_text(
                "📭 لا توجد منتجات",
                reply_markup=back_to_admin_kb())
            return await cb.answer()
        
        buttons = []
        for p in products:
            pid, cat, name_ar, name_ru, price, stock = p
            pname = get_product_name(name_ar, name_ru, "ar")
            emoji = "⭐" if cat == "stars" else "🎮"
            
            # إنشاء صفوف لكل منتج
            buttons.append([
                InlineKeyboardButton(
                    text=f"{emoji} <b>{pname}</b>",
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
                InlineKeyboardButton(
                    text="─" * 30,
                    callback_data="noop")
            ])
        
        buttons.append([
            InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")
        ])
        
        await cb.message.edit_text(  # type: ignore
            f"📦 <b>جميع المنتجات ({len(products)})</b>\n"
            f"اضغط على أي منتج لتعديله:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
        return await cb.answer()

    elif action == "categories":
        await cb.message.edit_text(
            f"🏪 <b>أقسام المتجر</b>\n"
            f"⭐ نجوم تيليجرام\n"
            f"🎮 بطاقات Google Play\n"
            f"📦 كل المنتجات",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action == "coupons":
        await cb.message.edit_text(
            f"🎟️ <b>كودات الخصم</b>\n"
            f"هذه الميزة قريباً...",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action == "broadcast":
        admin_pending[uid] = {"action": "broadcast"}
        await cb.message.edit_text(  # type: ignore
            f"📤 <b>إرسال نقاط للجميع</b>\n"
            f"كم نقطة تريد إضافتها لكل المستخدمين؟",
            reply_markup=back_to_admin_kb())

    elif action.startswith("editprod:"):
        pid = int(action.split(":")[1])
        product = await get_product(pid)
        if not product:
            await cb.message.edit_text(
                "❌ المنتج غير موجود",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع",
                                         callback_data="admin_productsmenu")
                ]]))
            return await cb.answer()

        pid, cat, name_ar, name_ru, price, stock = product[:6]
        pname = get_product_name(name_ar, name_ru, "ar")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ تعديل الاسم (عربي)",
                                     callback_data=f"admin_editprodname:{pid}")
            ],
            [
                InlineKeyboardButton(text="✏️ تعديل الاسم (روسي)",
                                     callback_data=f"admin_editprodname_ru:{pid}")
            ],
            [
                InlineKeyboardButton(
                    text="💰 تعديل السعر",
                    callback_data=f"admin_editprodprice:{pid}")
            ],
            [
                InlineKeyboardButton(
                    text="📦 تعديل الكمية",
                    callback_data=f"admin_editprodstock:{pid}")
            ],
            [
                InlineKeyboardButton(text="🗑️ حذف المنتج",
                                     callback_data=f"admin_delprod:{pid}")
            ],
            [
                InlineKeyboardButton(text="🔙 رجوع",
                                     callback_data="admin_productsmenu")
            ]
        ])
        await cb.message.edit_text(  # type: ignore
            f"📦 <b>تعديل المنتج</b>\n"
            f"📝 الاسم (عربي): <b>{name_ar}</b>\n"
            f"📝 الاسم (روسي): <b>{name_ru}</b>\n"
            f"💰 السعر: <b>{price}</b>\n"
            f"📊 الكمية: <b>{stock}</b>",
            reply_markup=kb)
        return await cb.answer()

    elif action.startswith("editprodname:"):
        pid = int(action.split(":")[1])
        admin_pending[uid] = {"action": "editprodname", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"✏️ <b>تعديل اسم المنتج</b>\n"
            f"أرسل الاسم الجديد:",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action.startswith("editprodname_ru:"):
        pid = int(action.split(":")[1])
        admin_pending[uid] = {"action": "editprodname_ru", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"✏️ <b>تعديل الاسم الروسي للمنتج</b>\n"
            f"أرسل الاسم الجديد <b>بالروسية</b>:",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action.startswith("editprodprice:"):
        pid = int(action.split(":")[1])
        admin_pending[uid] = {"action": "editprodprice", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"💰 <b>تعديل سعر المنتج</b>\n"
            f"أرسل السعر الجديد (بالنقاط):",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action.startswith("editprodstock:"):
        pid = int(action.split(":")[1])
        admin_pending[uid] = {"action": "editprodstock", "pid": pid}
        await cb.message.edit_text(  # type: ignore
            f"📦 <b>تعديل كمية المنتج</b>\n"
            f"أرسل الكمية الجديدة:",
            reply_markup=back_to_admin_kb())
        return await cb.answer()

    elif action.startswith("delprod:"):
        pid = int(action.split(":")[1])
        await remove_product(pid)
        await cb.message.edit_text(  # type: ignore
            f"🗑️ <b>تم حذف المنتج!</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 رجوع",
                                     callback_data="admin_productsmenu")
            ]]))
        return await cb.answer()

    elif action == "productsmenu":
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ إضافة منتج نجوم", callback_data="admin_addstars")],
            [InlineKeyboardButton(text="➕ إضافة منتج Google Play", callback_data="admin_addplay")],
            [InlineKeyboardButton(text="✏️ تعديل المنتجات الموجودة", callback_data="admin_editproducts")],
            [InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_back")]
        ])
        await cb.message.edit_text(  # type: ignore
            f"📦 <b>إدارة المنتجات والسلع</b>\n25\n\n"

            f"🎯 اختر العملية المطلوبة:",
            reply_markup=kb
        )
        return await cb.answer()
    
    elif action == "editproducts":
        products = await list_products()
        if not products:
            await cb.message.edit_text(
                f"📦 <b>تعديل المنتجات</b>\n"
                f"📭 لا توجد منتجات حالياً",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع",
                                         callback_data="admin_productsmenu")
                ]]))
        else:
            text = f"📦 <b>جميع المنتجات</b>\n\n"
            kb_buttons = []
            for pid, cat, name_ar, name_ru, price, stock in products:
                pname = get_product_name(name_ar, name_ru, "ar")
                emoji = "⭐" if cat == "stars" else "🎮"
                text += f"{emoji} {pname} - {price} نقطة (الكمية: {stock})\n"
                kb_buttons.append([
                    InlineKeyboardButton(text=f"✏️ {pname}",
                                         callback_data=f"admin_editprod:{pid}")
                ])
            kb_buttons.append([
                InlineKeyboardButton(text="🔙 رجوع", callback_data="admin_productsmenu")
            ])
            await cb.message.edit_text(  # type: ignore
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_buttons))
        return await cb.answer()

    elif action in ["back", "mainmenu"]:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ تعيين كلمة نقاط",
                                     callback_data="admin_setword"),
                InlineKeyboardButton(text="🔢 تعيين نقاط الدخول",
                                     callback_data="admin_entrypoints")
            ],
            [
                InlineKeyboardButton(text="👤 تعيين حساب المطور",
                                     callback_data="admin_setdev"),
                InlineKeyboardButton(text="🎁 صنع روابط تمويل",
                                     callback_data="admin_giftlink")
            ],
            [
                InlineKeyboardButton(text="📦 جميع السلع",
                                     callback_data="admin_productsmenu"),
                InlineKeyboardButton(text="📦 جميع المنتجات",
                                     callback_data="admin_allproducts")
            ],
            [
                InlineKeyboardButton(text="🏪 أقسام المتجر",
                                     callback_data="admin_categories"),
                InlineKeyboardButton(text="🎟️ الخصم",
                                     callback_data="admin_coupons")
            ],
            [
                InlineKeyboardButton(text="🎁 صنع رابط هدايا",
                                     callback_data="admin_giftlink2"),
                InlineKeyboardButton(text="📤 إرسال نقاط",
                                     callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton(text="📊 الإحصائيات",
                                     callback_data="admin_stats")
            ],
            [
                InlineKeyboardButton(text="⚙️ الإعدادات",
                                     callback_data="admin_settings")
            ],
            [
                InlineKeyboardButton(text="🔙 القائمة الرئيسية",
                                     callback_data="back:")
            ]
        ])
        admin_pages[cb.from_user.id] = "main"
        if action == "mainmenu":
            await cb.message.edit_text(
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"

                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)
        else:
            await cb.message.edit_text(  # type: ignore
                f"⚙️ <b>لوحة التحكم</b>\n"
                f"👋 مرحباً أيها المسؤول\n\n"

                f"📌 اختر الإجراء المطلوب:",
                reply_markup=kb)

    await cb.answer()


@dp.message()
async def handle_admin_input(message: types.Message):
    uid = message.from_user.id
    if uid not in admin_pending:
        return

    data = admin_pending[uid]
    action = data["action"]
    step = data.get("step", "")
    text = message.text.strip()

    try:
        if action in ["addstars", "addplay"]:
            category = "stars" if action == "addstars" else "play"
            category_name = "نجوم" if action == "addstars" else "Google Play"

            if step == "name":
                admin_pending[uid]["name"] = text
                admin_pending[uid]["step"] = "name_ru"
                await message.reply(
                    f"✅ تم تسجيل اسم المنتج (عربي): <b>{text}</b>\n\n"
                    f"📝 <b>الخطوة 2/4:</b>\n"
                    f"أرسل اسم المنتج بالروسية (Russian name):",
                    reply_markup=back_to_admin_kb())

            elif step == "name_ru":
                admin_pending[uid]["name_ru"] = text
                admin_pending[uid]["step"] = "price"
                await message.reply(
                    f"✅ تم تسجيل اسم المنتج (روسي): <b>{text}</b>\n\n"
                    f"📝 <b>الخطوة 3/4:</b>\n"
                    f"أرسل سعر المنتج (بالنقاط):",
                    reply_markup=back_to_admin_kb())

            elif step == "price":
                price = int(text)
                admin_pending[uid]["price"] = price
                admin_pending[uid]["step"] = "stock"
                await message.reply(
                    f"✅ تم تسجيل السعر: <b>{price}</b> نقطة\n\n"
                    f"📝 <b>الخطوة 4/4:</b>\n"
                    f"أرسل كمية توفر المنتج:",
                    reply_markup=back_to_admin_kb())

            elif step == "stock":
                stock = int(text)
                name = data["name"]
                name_ru = data["name_ru"]
                price = data["price"]

                admin_pending.pop(uid)

                await add_product(category, name, name_ru, price, stock)
                await notify_all_users_new_product(name, price, category_name)
                
                # عرض جميع المنتجات بعد الإضافة
                products = await list_products()
                buttons = []
                for p in products:
                    pid, cat, name_p, name_ru_p, price_p, stock_p = p
                    pname = get_product_name(name_p, name_ru_p, "ar")
                    emoji = "⭐" if cat == "stars" else "🎮"
                    
                    buttons.append([
                        InlineKeyboardButton(
                            text=f"{emoji} <b>{pname}</b>",
                            callback_data="noop")
                    ])
                    buttons.append([
                        InlineKeyboardButton(
                            text=f"💎 السعر: {price_p} نقطة",
                            callback_data="noop"),
                        InlineKeyboardButton(
                            text=f"📦 الكمية: {stock_p}",
                            callback_data="noop")
                    ])
                    buttons.append([
                        InlineKeyboardButton(
                            text="─" * 30,
                            callback_data="noop")
                    ])
                
                buttons.append([
                    InlineKeyboardButton(text="🔙 رجوع لوحة الإدمن", callback_data="admin_mainmenu")
                ])
                
                await message.reply(f"🎉 <b>تم إضافة المنتج بنجاح!</b>\n"
                                    f"📦 الاسم (عربي): <b>{name}</b>\n"
                                    f"📦 الاسم (روسي): <b>{name_ru}</b>\n"
                                    f"💎 السعر: <b>{price}</b> نقطة\n"
                                    f"📊 الكمية: <b>{stock}</b>\n"
                                    f"📂 القسم: <b>{category_name}</b>\n"
                                    f"📢 تم إرسال إشعار لجميع المستخدمين!\n\n"
                                    f"📦 <b>جميع المنتجات ({len(products)})</b>:",
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


        elif action == "addpoints":
            if step == "user":
                if text.startswith("@"):
                    admin_pending[uid]["username"] = text
                else:
                    admin_pending[uid]["user_id"] = int(text)

                admin_pending[uid]["step"] = "points"
                await message.reply(
                    f"✅ تم تحديد المستخدم: <b>{text}</b>\n\n"

                    f"📝 <b>الخطوة 2/2:</b>\n"
                    f"كم نقطة تريد إضافتها لهذا المستخدم؟",
                    reply_markup=back_to_admin_kb())

            elif step == "points":
                pts = int(text)

                if "user_id" in data:
                    user_id = data["user_id"]
                    user_display = str(user_id)
                else:
                    username = data["username"]
                    async with aiosqlite.connect(DB_PATH) as db:
                        cur = await db.execute(
                            "SELECT user_id FROM users WHERE user_id = ?",
                            (username.replace("@", ""), ))
                        row = await cur.fetchone()
                        if row:
                            user_id = row[0]
                        else:
                            user_id = int(username.replace("@", ""))
                    user_display = username

                admin_pending.pop(uid)

                await add_points(user_id, pts)
                await message.reply(f"🎉 <b>تم إضافة النقاط بنجاح!</b>\n"
                                    f"👤 المستخدم: <b>{user_display}</b>\n"
                                    f"💰 النقاط المضافة: <b>+{pts}</b>",
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                        InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                    ]]))

        elif action == "setinviter":
            global INVITER_POINTS
            INVITER_POINTS = int(text)
            admin_pending.pop(uid)
            await message.reply(f"🎉 <b>تم ضبط نقاط الدعوة!</b>\n"
                                f"🎁 نقاط كل دعوة: <b>{INVITER_POINTS}</b> نقطة",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "banuser":
            user_id = int(text)
            await ban_user(user_id)
            admin_pending.pop(uid)
            await message.reply(f"🚫 <b>تم حظر المستخدم!</b>\n"
                                f"👤 ID: <code>{user_id}</code>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "unbanuser":
            user_id = int(text)
            await unban_user(user_id)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم فك حظر المستخدم!</b>\n"
                                f"👤 ID: <code>{user_id}</code>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "promotemod":
            user_id = int(text)
            await promote_moderator(user_id)
            admin_pending.pop(uid)
            await message.reply(f"⬆️ <b>تم ترقية مشرف جديد!</b>\n"
                                f"👤 ID: <code>{user_id}</code>\n"
                                f"✨ تم ترقيته لمشرف بنجاح!",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "demotemod":
            user_id = int(text)
            # حماية: منع إزالة مالك البوت
            if user_id == ADMIN_ID:
                await message.reply(f"❌ <b>لا يمكن إزالة مالك البوت الحقيقي!</b>\n"
                                    f"👤 هذا هو مالك البوت الرئيسي ولا يمكن إزالة صلاحياته",
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                        InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                    ]]))
                # إرسال إشعار لمالك البوت
                try:
                    await bot.send_message(
                        ADMIN_ID,
                        f"⚠️ <b>محاولة إزالة صلاحياتك!</b>\n"
                        f"👤 <b>المستخدم الذي حاول:</b>\n"
                        f"<code>{uid}</code>\n"
                        f"👤 <b>الاسم:</b> {message.from_user.first_name}\n\n"
                        f"🔐 تم رفض الطلب تلقائياً لأنك مالك البوت!"
                    )
                except:
                    pass
                admin_pending.pop(uid, None)
                return
            
            await demote_moderator(user_id)
            admin_pending.pop(uid)
            await message.reply(f"⬇️ <b>تم إزالة المشرف!</b>\n"
                                f"👤 ID: <code>{user_id}</code>\n"
                                f"✨ تم إزالة صلاحياته بنجاح!",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))
            # إرسال إشعار لمالك البوت برقم ID من حاول الإزالة
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"📝 <b>تم إزالة مشرف!</b>\n"
                    f"🔴 <b>المشرف الذي تم إزالته:</b>\n"
                    f"<code>{user_id}</code>\n\n"
                    f"👤 <b>من قام بالإزالة:</b>\n"
                    f"<code>{uid}</code>\n"
                    f"👤 <b>الاسم:</b> {message.from_user.first_name}"
                )
            except:
                pass

        elif action == "editname_ar":
            pid = data["pid"]
            await update_product_name(pid, text)
            admin_pending[uid]["step"] = "editname_ru"
            admin_pending[uid]["name_ar"] = text
            await message.reply(f"✅ تم تسجيل الاسم العربي: <b>{text}</b>\n\n"
                                f"<b>الخطوة 2/2:</b> أرسل الاسم الجديد <b>بالروسية</b>:",
                                reply_markup=back_to_admin_kb())
        
        elif data.get("step") == "editname_ru":
            pid = data["pid"]
            await update_product_name_ru(pid, text)
            admin_pending.pop(uid)
            name_ar = data.get("name_ar", "")
            await message.reply(f"✅ <b>تم تعديل أسماء المنتج!</b>\n"
                                f"🇸🇦 الاسم العربي: <b>{name_ar}</b>\n"
                                f"🇷🇺 الاسم الروسي: <b>{text}</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "editprice":
            pid = data["pid"]
            new_price = int(text)
            await update_product_price(pid, new_price)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل سعر المنتج!</b>\n"
                                f"💎 السعر الجديد: <b>{new_price}</b> نقطة")

        elif action == "editstock":
            pid = data["pid"]
            new_stock = int(text)
            await update_product_stock(pid, new_stock)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل كمية المنتج!</b>\n"
                                f"📊 الكمية الجديدة: <b>{new_stock}</b>")

        elif action == "addbutton":
            pass

        elif action == "giftlink":
            if data.get("step") == "points":
                points = int(text)
                admin_pending[uid]["points"] = points
                admin_pending[uid]["step"] = "uses"
                await message.reply(
                    f"✅ تم تسجيل النقاط: <b>{points}</b>\n\n"

                    f"📝 <b>الخطوة 2/2:</b>\n"
                    f"كم شخص يمكنه استخدام هذا الرابط؟",
                    reply_markup=back_to_admin_kb())
            elif data.get("step") == "uses":
                max_uses = int(text)
                points = data["points"]
                me = await bot.get_me()
                full_link = await create_gift_link(points, max_uses,
                                                   me.username)
                admin_pending.pop(uid)
                await message.reply(
                    f"🎉 <b>تم إنشاء رابط الهدايا!</b>\n\n"

                    f"🎁 <b>الرابط:</b>\n<code>{full_link}</code>\n\n"

                    f"💰 النقاط لكل استخدام: <b>{points}</b>\n"
                    f"👥 عدد الاستخدامات: <b>{max_uses}</b>\n\n"

                    f"📤 شارك هذا الرابط مع المستخدمين!")

        elif action == "setword":
            await set_points_word(text)
            admin_pending.pop(uid)
            await message.reply(f"✅ تم تعيين كلمة النقاط: <b>{text}</b>\n\n"
                               f"سيتم استخدام هذه الكلمة في جميع رسائل البوت!",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                   InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                               ]]))

        elif action == "setdailygift":
            try:
                amount = int(text)
                if amount <= 0:
                    await message.reply("❌ يجب أن تكون الكمية أكبر من 0")
                    return
                await set_daily_gift_amount(amount)
                admin_pending.pop(uid)
                await message.reply(f"✅ تم تعديل كمية الهديّة اليومية: <b>{amount} €</b>\n\n"
                                   f"المستخدمون سيحصلون على <b>{amount} €</b> في الهديّة اليومية!",
                                   reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                       InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                   ]]))
            except:
                await message.reply("❌ أرسل رقماً صحيحاً فقط")

        elif action == "entrypoints":
            global ENTRY_POINTS
            ENTRY_POINTS = int(text)
            admin_pending.pop(uid)
            await message.reply(f"✅ تم تعيين نقاط الدخول: <b>{text}</b> نقطة",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                   InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                               ]]))

        elif action == "setdev":
            global DEV_CONTACT
            DEV_CONTACT = text
            admin_pending.pop(uid)
            await message.reply(f"✅ تم تعيين حساب المطور: <b>{text}</b>",
                               reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                   InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                               ]]))

        elif action == "editbtnname":
            btn_id = data["btn_id"]
            new_name = text
            await update_custom_button(btn_id, new_name)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل اسم الزر!</b>\n\n"

                                f"🎛️ الاسم الجديد: <b>{new_name}</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "addbtnprod":
            if step == "name":
                admin_pending[uid]["name"] = text
                admin_pending[uid]["step"] = "price"
                await message.reply(
                    f"✅ تم تسجيل الاسم: <b>{text}</b>\n\n"

                    f"📝 <b>الخطوة 2/3:</b>\n"
                    f"أرسل السعر (بالنقاط):",
                    reply_markup=back_to_admin_kb())
            elif step == "price":
                price = int(text)
                admin_pending[uid]["price"] = price
                admin_pending[uid]["step"] = "stock"
                await message.reply(
                    f"✅ تم تسجيل السعر: <b>{price}</b> نقطة\n\n"

                    f"📝 <b>الخطوة 3/3:</b>\n"
                    f"أرسل الكمية:",
                    reply_markup=back_to_admin_kb())
            elif step == "stock":
                stock = int(text)
                name = data["name"]
                price = data["price"]
                category = data["category"]
                btn_id = data["btn_id"]
                await add_product(category, name, price, stock, btn_id)
                await notify_all_users_new_product(name, price, category)
                admin_pending.pop(uid)
                await message.reply(f"🎉 <b>تم إضافة المنتج للزر!</b>\n\n"

                                    f"📦 الاسم: <b>{name}</b>\n"
                                    f"💰 السعر: <b>{price}</b> نقطة\n"
                                    f"📊 الكمية: <b>{stock}</b>\n"
                                    f"📢 تم إرسال إشعار لجميع المستخدمين!",
                                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                        InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                    ]]))

        elif action == "editprodname":
            pid = data["pid"]
            await update_product_name(pid, text)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل الاسم!</b>\n\n"

                                f"📦 الاسم الجديد: <b>{text}</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "editprodname_ru":
            pid = data["pid"]
            await update_product_name_ru(pid, text)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل الاسم الروسي!</b>\n\n"

                                f"📦 الاسم الجديد: <b>{text}</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "editprodprice":
            pid = data["pid"]
            new_price = int(text)
            await update_product_price(pid, new_price)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل السعر!</b>\n\n"

                                f"💰 السعر الجديد: <b>{new_price}</b> نقطة",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

        elif action == "editprodstock":
            pid = data["pid"]
            new_stock = int(text)
            await update_product_stock(pid, new_stock)
            admin_pending.pop(uid)
            await message.reply(f"✅ <b>تم تعديل الكمية!</b>\n\n"

                                f"📦 الكمية الجديدة: <b>{new_stock}</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                                ]]))

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
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🔙 رجوع", callback_data="back:")
                ]]))

    except ValueError:
        await message.reply("❌ <b>خطأ!</b>\n\nيرجى إرسال رقم صحيح.",
                            reply_markup=back_to_admin_kb())
    except Exception as e:
        admin_pending.pop(uid, None)
        await message.reply(f"❌ <b>حدث خطأ!</b>\n\nالتفاصيل: {e}")


# ================= RUN =================


async def main():
    await init_db()
    print("✅ Bot is running")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
