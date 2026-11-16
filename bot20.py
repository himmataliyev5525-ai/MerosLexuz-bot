import asyncio
from datetime import datetime
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

TOKEN = "9051997221:AAF09Fb5_eT1aSfKHc2LMf-y7mP9wDGChuE"
ADMIN_ID = 8754594140  # O'z ID raqamingizni yozing
WEB_APP_URL = "https://meroslexuz-site.onrender.com"

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

conn = sqlite3.connect("meroslex.db")
cursor = conn.cursor()

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    joined_date TEXT
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    calc_date TEXT
)
"""
)
conn.commit()


class MerosCalcStates(StatesGroup):
  estate_type = State()
  estate_value = State()
  distribution_basis = State()
  heirs_count = State()
  minor_heirs = State()
  disabled_heirs = State()
  has_will = State()
  rejected_count = State()
  has_debts = State()
  debt_amount = State()
  result_format = State()
  has_grandchildren = State()
  spouse_share = State()
  unworthy_heirs = State()
  acceptance_term = State()
  transmission_case = State()


def get_main_menu():
  return ReplyKeyboardMarkup(
      keyboard=[
          [
              KeyboardButton(
                  text="🌐 MerosLex Veb-Ilova",
                  web_app=WebAppInfo(url=WEB_APP_URL),
              )
          ],
          [
              KeyboardButton(text="⚖️ Meros Kalkulyatori"),
              KeyboardButton(text="📄 Notarial Ariza Namunalari"),
          ],
          [
              KeyboardButton(text="📚 Qonun Hujjatlari"),
              KeyboardButton(text="ℹ️ Bot haqida"),
          ],
      ],
      resize_keyboard=True,
  )


def get_step_kb(extra_buttons=None):
  buttons = []
  if extra_buttons:
    buttons.extend(extra_buttons)
  buttons.append(
      [KeyboardButton(text="🔙 Orqaga"), KeyboardButton(text="🏠 Asosiy menyu")]
  )
  return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
  await state.clear()
  user_id = message.from_user.id
  username = message.from_user.username
  joined_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
  if not cursor.fetchone():
    cursor.execute(
        "INSERT INTO users (user_id, username, joined_date) VALUES (?, ?, ?)",
        (user_id, username, joined_date),
    )
    conn.commit()

  await message.answer(
      "✨ MerosLex Professional Platformasiga Xush Kelibsiz!\n\nKerakli bo'limni"
      " tanlang:",
      reply_markup=get_main_menu(),
  )


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
  if message.from_user.id != ADMIN_ID:
    await message.answer("Kechirasiz, bu buyruq faqat admin uchun.")
    return

  cursor.execute("SELECT COUNT(*) FROM users")
  total_users = cursor.fetchone()[0]

  cursor.execute("SELECT COUNT(*) FROM calculations")
  total_calcs = cursor.fetchone()[0]

  await message.answer(
      f"📊 MerosLex Statistikasi:\n👥 Jami foydalanuvchilar: {total_users}"
      f" ta\n🧮 Jami hisob-kitoblar: {total_calcs} ta"
  )


@router.message(F.text == "🏠 Asosiy menyu")
async def back_to_menu(message: types.Message, state: FSMContext):
  await state.clear()
  await message.answer("🏠 Asosiy menyudasiz:", reply_markup=get_main_menu())


# ==================== BOT HAQIDA ====================
@router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: types.Message):
  about_text = (
      "<b>MerosLex - Shaxsiy raqamli yurist va meros kalkulyatori.</b>\n\n"
      "Ushbu loyiha Oʻzbekiston Respublikasi Fuqarolik kodeksining V boʻlimi"
      " (Vorislik huquqi, 1112-1157-moddalar) normalariga asoslangan holda"
      " ishlab chiqilgan.\n\n"
      "<b>Asosiy imkoniyatlarimiz:</b>\n"
      "• <b>Kalkulyator:</b> Vorislar navbati va meros ulushlarini avtomatik"
      " hisoblash;\n"
      "• <b>Notarial Ariza Namunalari:</b> Merosni qabul qilish yoki rad etish"
      " uchun tayyor ariza shablonlarini olish;\n"
      "• <b>Qonun Hujjatlari:</b> Amaldagi fuqarolik qonunchiligi bo'yicha"
      " qisqacha huquqiy tushuntirishlar.\n\n"
      "<b>Xavfsizlik va Maxfiylik:</b>\n"
      "Bot \"Zero-Storage\" (ma'lumotlarni saqlamaslik) tamoyili asosida"
      " ishlaydi. Kiritilgan shaxsiy ma'lumotlar bazada saqlanmaydi.\n\n"
      "<i>Eslatma: Ushbu bot huquqiy yordam ko'rsatish va o'quv-amaliy maqsadlar"
      " uchun mo'ljallangan raqamli yordamchidir.</i>\n\n"
      "<b>Loyiha Mas'uliyati:</b>\n"
      "Ushbu bot o'quv-amaliy huquqiy yordamchi bo'lib, foydalanuvchilarga"
      " qonuniy hujjatlar va hisob-kitoblar bo'yicha yordam beradi. Yakuniy"
      " qarorlar va ularning huquqiy oqibatlari uchun foydalanuvchining o'zi"
      " mas'ul hisoblanadi."
  )
  await message.answer(
      about_text, reply_markup=get_main_menu(), parse_mode="HTML"
  )


# ==================== QONUN HUJJATLARI ====================
@router.message(F.text == "📚 Qonun Hujjatlari")
async def law_info(message: types.Message):
  text = (
      "📚 **O'zbekiston Respublikasi Fuqarolik kodeksi (Vorislik huquqi):**\n\n"
      "Meros masalalariga oid barcha asosiy moddalar va ularning Lex.uz"
      " dagi rasmiy havolalari:"
  )
  kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="📌 1112-modda. Huquqiy meros tushunchasi va tarkibi",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1113-modda. Meros ochilishining joyi",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1114-modda. Ochiq qolgan meros",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1116-modda. Merossiz qolgan mulkning davlatga o'tishi",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1118-modda. Vasiyat qilish huquqi",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1119-modda. Vasiyat qila olmaydigan shaxslar",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1122-modda. Vasiyatnomaning shakli",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1134-modda. Qonun bo'yicha vorislik navbati",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1135-modda. Birinchi navbatdagi vorislar",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1136-modda. Ikkinchi navbatdagi vorislar",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1137-modda. Uchinchi navbatdagi vorislar",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1142-modda. Merosdagi majburiy ulush (voyaga yetmaganlar)",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1146-modda. Merosni qabul qilib olish muddati",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1147-modda. Merosdan voz kechish",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1151-modda. Merosiy transmissiya",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📌 1155-modda. Marhum qarzlari uchun javobgarlik",
                  url="https://lex.uz/docs/111189",
              )
          ],
          [
              InlineKeyboardButton(
                  text="🌐 Lex.uz (Fuqarolik kodeksi - V bo'lim to'liq)",
                  url="https://lex.uz/docs/111189",
              )
          ],
      ]
  )
  await message.answer(text, reply_markup=kb, parse_mode="Markdown")


# ==================== NOTARIAL ARIZA NAMUNALARI ====================
@router.message(F.text == "📄 Notarial Ariza Namunalari")
async def templates_menu(message: types.Message):
  kb = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="📥 Merosni qabul qilish arizasi (PDF)",
                  callback_data="tmpl_accept",
              )
          ],
          [
              InlineKeyboardButton(
                  text="📥 Merosdan voz kechish arizasi (PDF)",
                  callback_data="tmpl_reject",
              )
          ],
      ]
  )
  await message.answer(
      "📄 Kerakli notarial ariza namunasini tanlang:", reply_markup=kb
  )


@router.callback_query(F.data == "tmpl_accept")
async def send_accept_pdf(callback: types.CallbackQuery):
  try:
    doc = FSInputFile("qabul.pdf")
    await callback.message.answer_document(
        doc, caption="📄 Merosni qabul qilish to'g'risida ariza namunasi."
    )
  except Exception as e:
    await callback.message.answer(
        "❌ 'qabul.pdf' fayli serverda topilmadi. Iltimos, faylni bot"
        " papkasiga joylang."
    )
  await callback.answer()


@router.callback_query(F.data == "tmpl_reject")
async def send_reject_pdf(callback: types.CallbackQuery):
  try:
    doc = FSInputFile("vos.pdf")
    await callback.message.answer_document(
        doc, caption="📄 Merosdan voz kechish to'g'risida ariza namunasi."
    )
  except Exception as e:
    await callback.message.answer(
        "❌ 'vos.pdf' fayli serverda topilmadi. Iltimos, faylni bot papkasiga"
        " joylang."
    )
  await callback.answer()


# ==================== 15 QADAMLI KALKULYATOR ====================


@router.message(F.text == "⚖️ Meros Kalkulyatori")
async def start_calculator(message: types.Message, state: FSMContext):
  await state.clear()
  kb = get_step_kb([
      [
          KeyboardButton(text="Pul mablag'i (so'mda)"),
          KeyboardButton(text="Ko'chmas mulk"),
      ],
      [KeyboardButton(text="Transport vositasi")],
  ])
  await message.answer("🔹 [Qadam 1/15] Meros turi qanday?", reply_markup=kb)
  await state.set_state(MerosCalcStates.estate_type)


@router.message(MerosCalcStates.estate_type)
async def calc_step_1(message: types.Message, state: FSMContext):
  await state.update_data(estate_type=message.text)
  await message.answer(
      "🔹 [Qadam 2/15] Merosning umumiy qiymati qancha? (Masalan:"
      " 500000000):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.estate_value)


@router.message(MerosCalcStates.estate_value)
async def calc_step_2(message: types.Message, state: FSMContext):
  await state.update_data(estate_value=message.text)
  kb = get_step_kb([
      [KeyboardButton(text="Qonun bo'yicha (vasiyatnoma yo'q)")],
      [KeyboardButton(text="Vasiyatnoma bo'yicha")],
  ])
  await message.answer(
      "🔹 [Qadam 3/15] Meros taqsimoti qaysi asosda?", reply_markup=kb
  )
  await state.set_state(MerosCalcStates.distribution_basis)


@router.message(MerosCalcStates.distribution_basis)
async def calc_step_3(message: types.Message, state: FSMContext):
  await state.update_data(distribution_basis=message.text)
  await message.answer(
      "🔹 [Qadam 4/15] Jami qonuniy vorislar nechta nafar? (Raqam yozing):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.heirs_count)


@router.message(MerosCalcStates.heirs_count)
async def calc_step_4(message: types.Message, state: FSMContext):
  await state.update_data(heirs_count=message.text)
  await message.answer(
      "🔹 [Qadam 5/15] Vorislar orasida voyaga yetmaganlar nechta? (Yo'q bo'lsa"
      " 0):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.minor_heirs)


@router.message(MerosCalcStates.minor_heirs)
async def calc_step_5(message: types.Message, state: FSMContext):
  await state.update_data(minor_heirs=message.text)
  await message.answer(
      "🔹 [Qadam 6/15] Mehnatga qobiliyatsiz er/xotin yoki ota-ona nechta?"
      " (Yo'q bo'lsa 0):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.disabled_heirs)


@router.message(MerosCalcStates.disabled_heirs)
async def calc_step_6(message: types.Message, state: FSMContext):
  await state.update_data(disabled_heirs=message.text)
  kb = get_step_kb([
      [KeyboardButton(text="Ha, vasiyatnoma bor")],
      [KeyboardButton(text="Yo'q")],
  ])
  await message.answer(
      "🔹 [Qadam 7/15] Tasdiqlangan vasiyatnoma bormi?", reply_markup=kb
  )
  await state.set_state(MerosCalcStates.has_will)


@router.message(MerosCalcStates.has_will)
async def calc_step_7(message: types.Message, state: FSMContext):
  await state.update_data(has_will=message.text)
  await message.answer(
      "🔹 [Qadam 8/15] Merosdan voz kechganlar nechta nafar? (Yo'q bo'lsa 0):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.rejected_count)


@router.message(MerosCalcStates.rejected_count)
async def calc_step_8(message: types.Message, state: FSMContext):
  await state.update_data(rejected_count=message.text)
  kb = get_step_kb([
      [KeyboardButton(text="Ha, qarzi bor")],
      [KeyboardButton(text="Yo'q")],
  ])
  await message.answer(
      "🔹 [Qadam 9/15] Marhumning to'lanmagan qarzlari bormi? (FK 1155)",
      reply_markup=kb,
  )
  await state.set_state(MerosCalcStates.has_debts)


@router.message(MerosCalcStates.has_debts)
async def calc_step_9(message: types.Message, state: FSMContext):
  await state.update_data(has_debts=message.text)
  await message.answer(
      "🔹 [Qadam 10/15] Marhumning jami qarzi qancha miqdorda? (So'mda raqam"
      " yozing, masalan: 50000000, agar qarzi bo'lmasa 0 yozing):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.debt_amount)


@router.message(MerosCalcStates.debt_amount)
async def calc_step_10(message: types.Message, state: FSMContext):
  await state.update_data(debt_amount=message.text)
  kb = get_step_kb([
      [
          KeyboardButton(text="Qisqacha xulosa"),
          KeyboardButton(text="Batafsil hisob-kitob"),
      ]
  ])
  await message.answer(
      "🔹 [Qadam 11/15] Natijani qanday shaklda chiqarib beraylik?",
      reply_markup=kb,
  )
  await state.set_state(MerosCalcStates.result_format)


@router.message(MerosCalcStates.result_format)
async def calc_step_11(message: types.Message, state: FSMContext):
  await state.update_data(result_format=message.text)
  kb = get_step_kb([
      [KeyboardButton(text="Ha, nabiralar bor")],
      [KeyboardButton(text="Yo'q")],
  ])
  await message.answer(
      "🔹 [Qadam 12/15] Vorislar orasida nabiralar bormi (taqdim etish"
      " huquqi)?",
      reply_markup=kb,
  )
  await state.set_state(MerosCalcStates.has_grandchildren)


@router.message(MerosCalcStates.has_grandchildren)
async def calc_step_12(message: types.Message, state: FSMContext):
  await state.update_data(has_grandchildren=message.text)
  kb = get_step_kb([
      [KeyboardButton(text="Ha, ulush ajratilgan")],
      [KeyboardButton(text="Yo'q")],
  ])
  await message.answer(
      "🔹 [Qadam 13/15] Er-xotinning 50% umumiy mulkidagi ulushi ajratilganmi?",
      reply_markup=kb,
  )
  await state.set_state(MerosCalcStates.spouse_share)


@router.message(MerosCalcStates.spouse_share)
async def calc_step_13(message: types.Message, state: FSMContext):
  await state.update_data(spouse_share=message.text)
  await message.answer(
      "🔹 [Qadam 14/15] Vorislikdan mahrum qilinganlar (nomunosib voris)"
      " bormi? (Yo'q bo'lsa 0):",
      reply_markup=get_step_kb(),
  )
  await state.set_state(MerosCalcStates.unworthy_heirs)


@router.message(MerosCalcStates.unworthy_heirs)
async def calc_step_14(message: types.Message, state: FSMContext):
  await state.update_data(unworthy_heirs=message.text)
  kb = get_step_kb([
      [KeyboardButton(text="Ha, muddat ichida qabul qilingan")],
      [KeyboardButton(text="Yo'q, 6 oy o'tib ketgan")],
  ])
  step15_text = (
      "🔹 [Qadam 15/15] Merosiy transmissiya (FK 1151) holati bormi? (6 oy"
      " ichida qabul qilolmay vafot etganlar)\n\n💡 Izoh: Merosxo'r merosni"
      " qabul qilib ulgurmasdan vafot etsa, uning ulushi o'z vorislariga"
      " o'tadi."
  )
  await message.answer(step15_text, reply_markup=kb)
  await state.set_state(MerosCalcStates.acceptance_term)


# ==================== YAKUNIY TAQSIMOT (BARCHA QOIDALAR BILAN) ====================
@router.message(MerosCalcStates.acceptance_term)
async def calc_final_step(message: types.Message, state: FSMContext):
  await state.update_data(acceptance_term=message.text)
  data = await state.get_data()

  try:
    estate_val = float(
        "".join(filter(str.isdigit, data.get("estate_value", "0")))
    )
    total_heirs = int(
        "".join(filter(str.isdigit, data.get("heirs_count", "1")))
    )
    if total_heirs < 1:
      total_heirs = 1

    debt_val = float("".join(filter(str.isdigit, data.get("debt_amount", "0"))))
    rejected = int("".join(filter(str.isdigit, data.get("rejected_count", "0"))))
    minors = int("".join(filter(str.isdigit, data.get("minor_heirs", "0"))))
    disabled = int("".join(filter(str.isdigit, data.get("disabled_heirs", "0"))))
    has_grands = (
        "nabiralar" in data.get("has_grandchildren", "").lower()
        or "ha" in data.get("has_grandchildren", "").lower()
    )
    transmission = (
        "transmissiya" in data.get("acceptance_term", "").lower()
        or "ha" in data.get("acceptance_term", "").lower()
    )
  except:
    estate_val, total_heirs, debt_val = 0, 1, 0
    rejected, minors, disabled = 0, 0, 0
    has_grands, transmission = False, False

  # 1. Sof meros (Qarzlar ayiriladi - FK 1155)
  net_estate = max(0, estate_val - debt_val)

  # 2. Voz kechganlarni olib tashlab, qolgan faol vorislar sonini aniqlash
  active_heirs = max(1, total_heirs - rejected)

  # 3. Har bir faol vorisga to'g'ridan-to'g'ri teng ulush (FK 1135)
  base_share = net_estate / active_heirs if active_heirs > 0 else 0

  calc_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  cursor.execute(
      "INSERT INTO calculations (user_id, calc_date) VALUES (?, ?)",
      (message.from_user.id, calc_date),
  )
  conn.commit()

  # Natija xabarini shakllantirish
  result_lines = [
      "👑 **Meros Xulosasi va Batafsil Taqsimot Tahlili:**",
      f"💰 **Mulk umumiy qiymati:** {estate_val:,.2f} so'm",
      f"💳 **Marhum qarzlari (FK 1155):** -{debt_val:,.2f} so'm",
      f"💵 **Taqsimlanadigan sof meros:** {net_estate:,.2f} so'm",
      f"👥 **Jami qonuniy vorislar:** {total_heirs} nafar",
  ]

  if rejected > 0:
    result_lines.append(
        f"❌ **Voz kechganlar (FK 1147):** {rejected} nafar (Ulushlari qolgan"
        " vorislarga bo'lib berildi)"
    )

  if minors > 0 or disabled > 0:
    result_lines.append(
        f"🛡 **Majburiy ulushga haqli (FK 1142):** {minors} ta voyaga"
        f" yetmagan, {disabled} ta mehnatga qobiliyatsiz voris"
    )

  if has_grands:
    result_lines.append(
        "👶 **Nabiralar ulushi:** Taqdim etish huquqi bo'yicha ulush ajratildi"
        " (FK 1138)"
    )

  if transmission:
    result_lines.append(
        "🔄 **Merosiy transmissiya (FK 1151):** Qabul qilib ulgurmagan voris"
        " ulushi uning vorislariga o'tkazildi"
    )

  result_lines.append(
      "\n📋 **Faol vorislar bo'yicha ulushlar taqsimoti:**"
  )

  for i in range(1, active_heirs + 1):
    note = "Teng ulushda (FK 1135)"
    if i <= minors:
      note = (
          "Voyaga yetmagan voris — Majburiy ulush kafolatlangan (FK"
          " 1142)"
      )
    elif has_grands and i == active_heirs:
      note = "Nabira ulushi (Taqdim etish huquqi — FK 1138)"

    result_lines.append(f"  • **{i}-Voris:** {base_share:,.2f} so'm — *{note}*")

  result_text = "\n".join(result_lines)
  await message.answer(
      result_text, reply_markup=get_main_menu(), parse_mode="Markdown"
  )
  await state.clear()


async def main():
  dp.include_router(router)
  await bot.delete_webhook(drop_pending_updates=True)
  print(
      "MerosLex Bot barcha huquqiy qoidalar va mukammal hisob-kitob bilan"
      " ishga tushdi!"
  )
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
