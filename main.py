import os
from time import sleep
import asyncio

from dotenv import load_dotenv
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from db import DataBase
from request import Scraper

# Take token from .env
load_dotenv() # Use for development only
TOKEN = os.getenv('TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Create bot
bot = Bot(TOKEN)
dp = Dispatcher(bot, loop=asyncio.get_event_loop())

# Connect to model
db = DataBase('db.sqlite3')

# Create scraper
scrap = Scraper()

#Main button
button_home = KeyboardButton('Home🏠')
kbs = ReplyKeyboardMarkup(resize_keyboard=True).add(button_home)

def my_marks(user_id):
    bts = InlineKeyboardMarkup()
    for item in db.get_identifier(user_id=user_id):
        bts.add(InlineKeyboardButton(item[1], callback_data=f'delete'))
    return bts


@dp.message_handler(commands=['start'])
@dp.message_handler(regexp='^Home')
async def main(message):
    await message.answer(
        ("Щоб відстежувати новий документ, "
        "введіть його id(наприклад:800101) у"
        " поле \"Написати повідомлення\".\n\n"
        "Щоб перестати відстежувати документ - "
        "натисніть на його id у списку нижче."),
        reply_markup = my_marks(message["from"].id),
        )
    await message.delete()

@dp.message_handler(regexp='^[0-9]+$')
async def add_identifier(message):
    if not db.get_identifier(message['from'].id).fetchone():
        mesg, *status = scrap.check(message.text)
        if mesg:
            db.add_identifier(message['from'].id, message.text, status[0])
            await message.answer(f"Додано зі статусом \"{mesg}\"", reply_markup = kbs)
        elif mesg == None:
            await message.answer("Сервер оффлайн, звернітся пізніше.", reply_markup = kbs)
        else:
            await message.answer("Дані некоректні чи застаріли", reply_markup = kbs)
    else:
        await message.answer("Ви вже відстежуєте документ", reply_markup = kbs)

@dp.callback_query_handler(text='delete')
async def delete(call):
    db.delete_record(call['from'].id)
    await call.message.answer('Документ більше не відстежується', reply_markup = kbs)
    
    
        


async def test():
    while(True):
        await asyncio.sleep(1)
        len = db.count().fetchone()[0]
        for i in range(1,len+1):
            print(i)
            await asyncio.sleep(100)
            obj = db.get_item(i-1, i)
            obj = obj.fetchone()
            rez, *status = scrap.check(obj[1])
            if rez:
                 if status[0] != obj[2]:
                    await bot.send_message(obj[0], f'Статус вашого документа оновлено \"{rez}\". Більш детальна інформація - http://passport.mfa.gov.ua/', reply_markup = kbs)
                    db.update_record(obj[0], status[0])
            elif rez == None:
                await bot.send_message(ADMIN_ID, 'Сервер не отвечает')
            else:
                await bot.send_message(obj[0], f'Запис про документ {obj[1]} застарів і був видалений.', reply_markup = kbs)
                db.delete_record(obj[0])
               


            
        


if __name__ == "__main__":
    dp.loop.create_task(test())  # Providing awaitable as an argument
    executor.start_polling(dp, skip_updates=True)