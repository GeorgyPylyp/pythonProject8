from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/weather"),
            KeyboardButton(text="/start"),
        ],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="виберіть дію з меню",
    selective=True,

)
