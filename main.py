import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
from os import getenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import requests
import datetime

from aiogram.fsm.state import State, StatesGroup

# from regweather import Form


from inline import main_kb

from comands import set_comands

class Form(StatesGroup):
    city = State()



class BotBase:
    def __init__(self, token, parse_mode=ParseMode.HTML):
        self.token = token
        self.bot = Bot(token=self.token, parse_mode=parse_mode)
        self.dp = Dispatcher()


    async def start(self):
        await self.dp.start_polling(self.bot)


class WeatherBot(BotBase):
    def __init__(self, token, weather_token, ):
        super().__init__(token)
        self.weather_token = weather_token
        self.router = Router()
        self.fotn=Form()

        self.router.message.register(self.command_start_handler, CommandStart())
        self.router.message.register(self.send_weather, Command("weather"))
        self.router.message.register(self.get_weather, Form.city)

        self.dp.include_router(self.router)

    async def command_start_handler(self, message: Message, bot: Bot):
        await message.reply(
            "Цей телеграм-бот призначений для отримання погоди у певному місті.\nЩоб розпочати, напишіть команду /weather",reply_markup=main_kb
        )


class WeatherBotFSM(WeatherBot):


    async def send_weather(self, message: Message, state: FSMContext):
        await state.set_state(Form.city)
        await message.reply("Введіть локацію:")



    async def get_weather(self, message: Message, state: FSMContext):
        city = message.text
        await state.update_data(city=city)
        try:
            r = requests.get(
                f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_token}&units=metric&lang=uk'
            )
            data = r.json()

            city_name = data['name']
            cur_weather = data['main']['temp']
            feels_like = data['main']['feels_like']
            sky = data['weather'][0]['description']
            humidity = data['main']['humidity']
            pressure = data['main']['pressure']
            wind = data['wind']['speed']
            sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
            sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
            length_of_day = sunset_timestamp - sunrise_timestamp

            await message.reply(
                f"Сьогодні: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f'Погода в місті: {city_name}\n'
                f'Температура: {cur_weather}°C\n'
                f'Відчувається як: {feels_like}°C\n'
                f'Небо: {sky}\n'
                f'Вологість: {humidity}%\n'
                f'Тиск: {pressure} мм\n'
                f'Швидкість вітру: {wind} м/сек\n'
                f'Схід сонця: {sunrise_timestamp.strftime("%H:%M:%S")}\n'
                f'Захід сонця: {sunset_timestamp.strftime("%H:%M:%S")}\n'
                f'Довжина дня: {length_of_day}\n'
            )
        except Exception as e:
            await message.reply(f"Я не знаю місто {city} ️")

        await state.clear()




if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")
    TOKEN = os.getenv("BOT_TOKEN")


    bot = WeatherBotFSM(TOKEN, WEATHER_TOKEN,)
    asyncio.run(bot.start())