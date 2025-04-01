import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

API_TOKEN = "7001360321:AAHhd9M39ShJwgCW0gWghOe62J8nZTvQTCc"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class Registration(StatesGroup):
    full_name = State()
    phone_number = State()

def save_user(full_name, phone_number):
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []
    
    users.append({"full_name": full_name, "phone_number": phone_number})
    
    with open("users.json", "w", encoding="utf-8") as file:
        json.dump(users, file, indent=4, ensure_ascii=False)

def get_registered_users():
    try:
        with open("users.json", "r", encoding="utf-8") as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []
    
    return users

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="\U0001F4DA Kurslar"), KeyboardButton(text="\U0001F4DE Bog‘lanish"), KeyboardButton(text="\U0001F4DF Maktab haqida")],
    ],
    resize_keyboard=True
)

courses_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="\U0001F1EC\U0001F1E7 Ingliz tili"), KeyboardButton(text="\U0001F1F7\U0001F1FA Rus tili")],
        [KeyboardButton(text="\U0001F1F8\U0001F1E6 Arab tili"), KeyboardButton(text="\U0001F4BB Informatika")],
        [KeyboardButton(text="\U0001F9EC Biologiya"), KeyboardButton(text="\U0001F9EA Kimyo")],
        [KeyboardButton(text="\U0001F4D0 Matematika"), KeyboardButton(text="\U0001F9E0 Mental arifmetika")],
        [KeyboardButton(text="\U0001F517 Ro‘yxatdan o‘tish")],
        [KeyboardButton(text="\U0001F519 Orqaga")],
    ],
    resize_keyboard=True
)

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="\U0001F519 Orqaga")]],
    resize_keyboard=True
)

teachers = {
    "\U0001F1EC\U0001F1E7 Ingliz tili": "O‘qituvchi: @english_teacher\nTelefon: +998 90 123 45 67",
    "\U0001F1F7\U0001F1FA Rus tili": "O‘qituvchi: @russian_teacher\nTelefon: +998 91 234 56 78",
    "\U0001F1F8\U0001F1E6 Arab tili": "O‘qituvchi: @arabic_teacher\nTelefon: +998 93 345 67 89",
    "\U0001F4BB Informatika": "O‘qituvchi: Akramov Azamatjon\nTelefon: +998 99 640 04 04",
    "\U0001F9EC Biologiya": "O‘qituvchi: @biology_teacher\nTelefon: +998 95 567 89 01",
    "\U0001F9EA Kimyo": "O‘qituvchi: @chemistry_teacher\nTelefon: +998 96 678 90 12",
    "\U0001F4D0 Matematika": "O‘qituvchi: @math_teacher\nTelefon: +998 97 789 01 23",
    "\U0001F9E0 Mental arifmetika": "O‘qituvchi: @mental_math_teacher\nTelefon: +998 98 890 12 34",
}

@dp.message(lambda message: message.text in ["/start", "/help"])
async def send_welcome(message: types.Message):
    await message.answer("Assalomu aleykum Sun way edu city xususiy maktabiga xush kelibsiz!", reply_markup=main_keyboard)

@dp.message(lambda message: message.text == "\U0001F4DA Kurslar")
async def show_courses(message: types.Message):
    await message.answer("Qaysi kurs sizni qiziqtiradi?", reply_markup=courses_keyboard)

@dp.message(lambda message: message.text == "\U0001F4DE Bog‘lanish")
async def contact(message: types.Message):
    await message.answer("Biz bilan bog‘lanish uchun: +998 99 914 95 95")
    
@dp.message(lambda message: message.text == "\U0001F4DF Maktab haqida")
async def contact(message: types.Message):
    await message.answer("Biz Sun Way maktabi jamoasi liderlarni yetishtirib chiqarishdan charchoq bilmasdan xarakat qiladi!")
    
@dp.message(lambda message: message.text == "\U0001F519 Orqaga")
async def back_to_main(message: types.Message):
    await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=main_keyboard)

@dp.message(lambda message: message.text in teachers.keys())
async def course_info(message: types.Message):
    await message.answer(f"📘 {message.text} kursi haqida ma’lumot:\n{teachers[message.text]}", reply_markup=back_keyboard)

@dp.message(lambda message: message.text == "\U0001F517 Ro‘yxatdan o‘tish")
async def start_registration(message: types.Message, state: FSMContext):
    await message.answer("Iltimos, ismingiz va familiyangizni kiriting:")
    await state.set_state(Registration.full_name)

@dp.message(Registration.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Endi telefon raqamingizni yuboring:", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    ))
    await state.set_state(Registration.phone_number)

@dp.message(Registration.phone_number, lambda message: message.contact)
async def get_phone_number(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    full_name = user_data["full_name"]
    phone_number = message.contact.phone_number
    save_user(full_name, phone_number)
    await message.answer(f"Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!\n\nIsm: {full_name}\nTelefon: {phone_number}", reply_markup=main_keyboard)
    await state.clear()

@dp.message(lambda message: message.text == "/users")
async def show_users(message: types.Message):
    users = get_registered_users()
    if not users:
        await message.answer("Hali hech kim ro‘yxatdan o‘tmagan.")
        return
    user_list = "\n\n".join([f"👤 {user['full_name']}\n📞 {user['phone_number']}" for user in users])
    await message.answer(f"📋 Ro‘yxatdan o‘tgan foydalanuvchilar:\n\n{user_list}")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
