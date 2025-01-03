from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from crud_functions import *

connection = sqlite3.connect('prod_base.db')
cursor = connection.cursor()

initiate_db()

api = '7599924313:AAH-vWWTT0ILIqMU1ABPqRQDeCw5OnGUuz0'
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb0 = ReplyKeyboardMarkup(resize_keyboard=True)
button4 = KeyboardButton("Регистрация")
kb0.add(button4)

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.row(button, button2)
kb.add(button3)

kb1 = InlineKeyboardMarkup()
in_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
in_button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb1.row(in_button, in_button2)

kb2 = InlineKeyboardMarkup()
product1 = InlineKeyboardButton(text='Продукт1', callback_data="product_buying")
product2 = InlineKeyboardButton(text='Продукт2', callback_data="product_buying")
product3 = InlineKeyboardButton(text='Продукт3', callback_data="product_buying")
product4 = InlineKeyboardButton(text='Продукт4', callback_data="product_buying")
kb2.row(product1, product2, product3, product4)

kb3 = ReplyKeyboardMarkup(resize_keyboard=True)
button4 = KeyboardButton("Регистрация")
kb3.add(button4)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = State()

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Рассчитать норму калорий')],
        [KeyboardButton(text='Формулы расчёта')]
    ], resize_keyboard=True
)

@dp.message_handler(text=['/start'])
async def start(message):
    await message.answer(f'Привет! Я бот помогающий твоему здоровью.', reply_markup=kb0)

@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text) == False:
        await state.update_data(username=message.text)
        await message.answer('Введите свой email:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state=RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    await RegistrationState.age.set()
    await message.answer('Введите свой возраст:')


@dp.message_handler(state=RegistrationState.age)
async def set_age(message, state):
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    add_user(user_data["username"], user_data["email"], user_data["age"])
    await message.answer('Регистрация прошла успешно', reply_markup=kb)
    await state.finish()

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Информация о боте.')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb1)

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    for i in range(1, 5):
        with open(f"images/{i}.png", "rb") as img:
            await message.answer_photo(img)
        await message.answer("Выберите продукт для покупки: ", reply_markup=kb2)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer("10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) - 161")
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    norma = (10*int(data['weight'])+6.25*int(data['growth'])-5*int(data['age'])-161)
    await message.answer(f'Ваша норма каллорий: {norma}')
    await UserState.weight.set()
    await state.finish()

@dp.message_handler()
async def all_message(message):
    await message.answer(f'Введите команду /start, чтобы начать общение.')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
