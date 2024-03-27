from aiogram.filters.state import State, StatesGroup


class CostCalculateStates(StatesGroup):
    type_of_stairs = State()
    opening = State()
    height_from_floor_to_floor = State()
    fence = State()
    k = State()
    rounding = State()