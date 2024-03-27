from typing import List, Type

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types.web_app_info import WebAppInfo


def cost_calculation_keyboard():
    button_1 = KeyboardButton(text="Рассчитать стоимость")
    keyboard = ReplyKeyboardMarkup(keyboard=[[button_1]], resize_keyboard=True)
    return keyboard


def create_reply_kb(
        items: List[str],
        width: int = 3,
        one_time_keyboard=False,
        resize_keyboard=True
) -> ReplyKeyboardMarkup:
    kb_builder = ReplyKeyboardBuilder()
    items_buttons: List[KeyboardButton] = list()
    for item in items:
        items_buttons.append(KeyboardButton(text=item))
    kb_builder.row(*items_buttons, width=width)
    return kb_builder.as_markup(
        one_time_keyboard=one_time_keyboard,
        resize_keyboard=resize_keyboard
    )


def create_inline_kb(
        items: List[str],
        buttons_call_back: Type[CallbackData],
        page_buttons_call_back: Type[CallbackData],
        page_number: int = 0,
        item_per_page: int = 5,
        width: int = 2,
        cancel: bool = False,
        back: bool = False,
        cancel_text: str = 'Cancel'
) -> InlineKeyboardMarkup:
    start_idx = page_number * item_per_page
    end_idx = start_idx + item_per_page

    kb_builder = InlineKeyboardBuilder()

    items_buttons: List[InlineKeyboardButton] = list()
    for item in items[start_idx:end_idx]:
        items_buttons.append(
            InlineKeyboardButton(
                text=item,
                callback_data=buttons_call_back(
                    item=item
                ).pack()
            )
        )
    kb_builder.row(*items_buttons, width=width)
    pages_buttons: List[InlineKeyboardButton] = list()
    if page_number != 0:
        pages_buttons.append(
            InlineKeyboardButton(
                text="←",
                callback_data=page_buttons_call_back(
                    page_number=page_number - 1,
                    cancel=0,
                    back=0
                ).pack()
            )
        )

    if back:
        pages_buttons.append(
            InlineKeyboardButton(
                text='Back',
                callback_data=page_buttons_call_back(
                    page_number=page_number,
                    cancel=0,
                    back=1
                ).pack()
            )
        )

    if cancel:
        pages_buttons.append(
            InlineKeyboardButton(
                text=cancel_text,
                callback_data=page_buttons_call_back(
                    page_number=page_number,
                    cancel=1,
                    back=0
                ).pack()
            )
        )

    if not end_idx >= len(items):
        pages_buttons.append(
            InlineKeyboardButton(
                text="→",
                callback_data=page_buttons_call_back(
                    page_number=page_number + 1,
                    cancel=0,
                    back=0
                ).pack()
            )
        )
    if pages_buttons:
        kb_builder.row(*pages_buttons)
    return kb_builder.as_markup()
