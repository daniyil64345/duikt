

from aiogram import Router, F, types , Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from filters.chat_types import ChatTypeFilter
from keyboards.keyboard import navigation, del_kbd
from database.engine import get_all_categories, show_something, buy
from bot_main import ADMINS

user_router = Router()
user_router.message.filter(ChatTypeFilter(chat_types=["private"]))

# --------------------------- STATES ---------------------------
class BuyProduct(StatesGroup):
    selected_product = State()
    number_of_room = State()


# --------------------------- START ---------------------------
@user_router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Вітаємо в боті ДУІКТ МАРКЕТ!\n"
        "Тут можна переглядати товари та робити покупки.\n"
        "Почніть з /menu або скористайтеся кнопками нижче."
    )

@user_router.message(Command("menu"))
async def show_main_menu(message: Message):
    await message.answer("Основне меню", reply_markup=navigation)


# --------------------------- КАТЕГОРІЇ ---------------------------
async def show_categories(callback: CallbackQuery, categories: list, to_menu: bool = True):
    """Показує клавіатуру категорій з кнопкою назад"""
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}")] for cat in categories
        ] + [[
            InlineKeyboardButton(
                text="Повернутись до меню" if to_menu else "Повернутись до категорій",
                callback_data="return_menu" if to_menu else "return_categories"
            )
        ]]
    )
    await callback.message.answer("Оберіть категорію:", reply_markup=inline_kb)
    if not categories:
        await callback.message.answer("немає категорій")


@user_router.message(F.text == "🛍 Переглянути товари")
async def show_categories_from_message(message: Message, state: FSMContext):
    
    categories = await get_all_categories()
    print(f"Категорії: {categories}")
    print(f"Тип: {type(categories)}")
    
    if not categories:
        await message.answer("❌ Категорій немає в базі даних")
        return
    await state.update_data(categories=categories)
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}")] for cat in categories
        ] + [[InlineKeyboardButton(text="Назад", callback_data="return_menu")]]
    )
   
    await message.answer("🔹 Ось меню для перегляду товарів:", reply_markup=inline_kb)


@user_router.callback_query(F.data == "wait")
async def wait_show_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    categories = data.get("categories", [])
    await show_categories(callback, categories, to_menu=True)


@user_router.callback_query(F.data.startswith("cat_"))
async def choose_category(callback: CallbackQuery, state: FSMContext):
    category = callback.data.replace("cat_", "")
    products = await show_something(category)

    if not products:
        await callback.message.answer(f"⚠️ У категорії <b>{category}</b> поки що немає товарів.", parse_mode="HTML")
        return

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=name, callback_data=f"product_{category}_{row_id}")]
            for row_id, name, price, photo, quantity in products
        ] + [[InlineKeyboardButton(text="Повернутись до категорій", callback_data="wait")]]
    )
    await callback.message.answer(f"📦 <b>{category}</b>\nОберіть товар:", parse_mode="HTML", reply_markup=inline_kb)


# --------------------------- ТОВАР ---------------------------
@user_router.callback_query(F.data.startswith("product_"))
async def choose_product(callback: CallbackQuery, state: FSMContext):
    _, category, product_id = callback.data.split("_")
    product_id = int(product_id)

    products = await show_something(category)
    selected = next((p for p in products if p[0] == product_id), None)

    if not selected:
        await callback.answer("❌ Товар не знайдено.", show_alert=True)
        return

    row_id, name, price, photo, quantity = selected
    await state.update_data(selected_product={
        "id": row_id,
        "name": name,
        "price": price,
        "category": category,
        "quantity": quantity
    })

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Додати до кошика", callback_data=f"shopify|yes|{category}|{row_id}"),
                InlineKeyboardButton(text="Ні, скасувати", callback_data="wait")
            ]
        ]
    )

    text = f"<b>{name}</b>\n💰 Ціна: {price} грн"
    if photo:
        await callback.message.answer_photo(photo=photo, caption=text, parse_mode="HTML", reply_markup=inline_kb)
    else:
        await callback.message.answer(text, parse_mode="HTML", reply_markup=inline_kb)


# --------------------------- ДОБАВИТИ В КОШИК ---------------------------
@user_router.callback_query(F.data.startswith("shopify"))
async def process_add(callback: CallbackQuery, state: FSMContext):
    _, answer, category, product_id = callback.data.split("|")
    data = await state.get_data()
    if answer == "yes":
        cart = data.get("cart", [])
        cart.append(data.get("selected_product"))
        await state.update_data(cart=cart)
        inline_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Сформувати чек", callback_data="show_cart"),
                    InlineKeyboardButton(text="Ще вибираю", callback_data="wait")
                ]
            ]
        )
        await callback.message.answer("✅ Товар додано до кошика.", reply_markup=inline_kb)
    else:
        await callback.message.answer("Товар не додано.", reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Повернутись до категорій", callback_data="wait")]]
        ))


# --------------------------- ПОКАЗ ЧЕКА ---------------------------
@user_router.callback_query(F.data == "show_cart")
async def vubirashki(callback: CallbackQuery, state: FSMContext):
    choice = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Самовивіз", callback_data="sam_reshu"),
                InlineKeyboardButton(text = "Доставка", callback_data="prinesite")
            ]
        ]
    )

    await callback.message.answer("Виберіть будь ласка спосіб доставлення вашого замовлення до вас перед тим як сформувати чек", reply_markup= choice)

@user_router.callback_query(F.data == "prinesite")
async def dostavka(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введіть номер кімнати")
    await state.set_state(BuyProduct.number_of_room)


@user_router.message(BuyProduct.number_of_room)
async def get_roon(message: Message, state: FSMContext):
    await state.update_data(number_of_room = message.text)
    choicee = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text = "Так , підтверджую інформацію", callback_data="prinesite_tovar_pz"),
                InlineKeyboardButton(text = "Ні , увести заново", callback_data="prinesite"),
            ]
        ]
    )
    await message.answer("Чи підтверджуєте ви інформацію?", reply_markup=choicee)
    


@user_router.callback_query(F.data == "sam_reshu")
async def show_cart(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    number_of_room = data.get("number_of_room")
    cart = data.get("cart", [])

    if not cart:
        await callback.message.answer("Ваш кошик наразі порожній")
        return

    total = sum(int(item["price"]) for item in cart)
    text = "🧾 <b>Ваш чек:</b>\n\n" + "\n".join(
        [f"{i+1}. {item['name']} — {item['price']} грн" for i, item in enumerate(cart)]
    ) + f"\n\n💰 Разом: {total} грн"

    for item in cart:
        await buy(item["category"], item["id"])
    
    text_admin = "🧾 <b>Ваш чек:</b>\n\n" + "\n".join(
    [f"{i+1}. {item['name']} — {item['price']} грн.\nКількість товару: {item['quantity']-1}" 
     for i, item in enumerate(cart)]
    ) + f"\n\n💰 Разом: {total} грн\nКімната: {'Самовивіз'}"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.message.answer(
    "Ваш чек надійшов адміністратору. Підходьте до кімнати 21/1"
)

    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                f"🧾 Нове замовлення від @{callback.from_user.username or 'користувача'}:\n\n{text_admin}",
                parse_mode="HTML"
            )
        except Exception as e:
            # Якщо адмін не запустив бота - пропускаємо
            print(f"⚠️ Не вдалось відправити адміну {admin_id}: {e}")
            continue
    await state.update_data(cart=[])


@user_router.callback_query(F.data == "prinesite_tovar_pz")
async def show_cart_pz(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    number_of_room = data.get("number_of_room")
    cart = data.get("cart", [])

    if not cart:
        await callback.message.answer("Ваш кошик наразі порожній")
        return

    total = sum(int(item["price"]) for item in cart)
    text = "🧾 <b>Ваш чек:</b>\n\n" + "\n".join(
        [f"{i+1}. {item['name']} — {item['price']} грн." for i, item in enumerate(cart)]
    ) + f"\n\n💰 Разом: {total+10} грн. +10 гривень за доставку"

    for item in cart:
        await buy(item["category"], item["id"])
    
    text_admin = "🧾 <b>Ваш чек:</b>\n\n" + "\n".join(
    [f"{i+1}. {item['name']} — {item['price']} грн.\nКількість товару: {item['quantity']-1}" 
     for i, item in enumerate(cart)]
    ) + f"\n\n💰 Разом: {total} грн\nКімната: {number_of_room}"

    await callback.message.answer(text, parse_mode="HTML")
    await callback.message.answer(
    "Ваш чек надійшов адміністратору. Спочатку оплатіть товар за реквізитами\n" 
    "Картки:\nПриват- 5169360027385685\n"
    "Моно- 4874070050925773\n"
    "Після оплати очікуйте на доставку до вашої кімнати"
)

    for admin_id in ADMINS:
        try:
            await bot.send_message(
                admin_id,
                f"🧾 Нове замовлення від @{callback.from_user.username or 'користувача'}:\n\n{text_admin}",
                parse_mode="HTML"
            )
        except Exception as e:
            # Якщо адмін не запустив бота - пропускаємо
            print(f"⚠️ Не вдалось відправити адміну {admin_id}: {e}")
            continue

    await state.clear()

# --------------------------- ПОВЕРНЕННЯ ---------------------------
@user_router.callback_query(F.data == "return_menu")
async def return_menu(callback: CallbackQuery):
    await callback.message.answer("Повертаємось до головного меню", reply_markup=navigation)

@user_router.callback_query(F.data == "return_categories")
async def return_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    categories = data.get("categories", [])
    await show_categories(callback, categories, to_menu=False)


# --------------------------- КОНТАКТИ ---------------------------
@user_router.message(F.text == "💬 Контактна інформація")
async def contact_info(message: Message):
    await message.answer(
        "<b>Власник магазину:</b> @Duikt_market\n"
        "<b>Кімната:</b> 21:1\n"
        "<b>Технічні проблеми з ботом:</b> @floxyz",
        parse_mode="HTML"
    )

@user_router.message(Command("help"))
async def help_command(message: Message):
    await message.answer("Якщо у вас виникли проблеми, можна зробити замовлення напряму і підійти до кімнати 21/1.")


@user_router.message(Command("contact"))
async def help_command(message: Message):
    await message.answer(
        "<b>Власник магазину:</b> @Duikt_market\n"
        "<b>Кімната:</b> 21:1\n"
        "<b>Технічні проблеми з ботом:</b> @floxyz",
        parse_mode="HTML"
    )

# --------------------------- ПОВЕРНЕННЯ ДО МЕНЮ ---------------------------
@user_router.message(F.text == "Назад до меню")
async def back_to_menu(message: Message):
    await message.answer("Повертаємось назад до меню", reply_markup=navigation)
