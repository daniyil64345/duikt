from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove ,
                           InlineKeyboardMarkup, InlineKeyboardButton)


navigation = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛍 Переглянути товари"),
            KeyboardButton(text="💬 Контактна інформація")
            
        ],
    ],
    resize_keyboard=True, 
    input_field_placeholder="🔹 Обери дію з меню"
)


del_kbd = ReplyKeyboardRemove()

meun = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1)Напої"),
            KeyboardButton(text="2)Печиво")
        ],
        [
            KeyboardButton(text="3)Снеки"),
            KeyboardButton(text="4)Солодке")
        ],
        [
            KeyboardButton(text="5)Цукерки та круасани"),
            KeyboardButton(text="6)Чіпси")
        ],
        [
            KeyboardButton(text="7)Всі товари"),
            KeyboardButton(text="8)Назад до меню")
        ]
    ],
    resize_keyboard=True, 
    input_field_placeholder="🔹 Обери дію з меню"
)
del_menu = ReplyKeyboardRemove()

something = InlineKeyboardMarkup(

    inline_keyboard=[
        [
            InlineKeyboardButton(text="Додати в корзину 🛒", callback_data="add_to_cart"),
        ],
    ]
)

admin_menu = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text = "Додати товар"),
            KeyboardButton(text = "Змінити товар")
        ],
        [
            KeyboardButton(text = "Додати фото"),
            KeyboardButton(text = "Видалити товар") 
            
        ],
        [
            KeyboardButton(text = "Додати категорію"),
            KeyboardButton(text = "Видалити категорію")
        ],
        [
            KeyboardButton(text = "Запланувати закриття магазину")
        ]
    ],
    resize_keyboard=True, 
    input_field_placeholder="🔹 Обери дію з меню"
)

del_smth = ReplyKeyboardRemove()
