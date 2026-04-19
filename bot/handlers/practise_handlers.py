from handlers.redis_handlers import get_practise, get_session_practise, set_session_practise
from db.config import redis_client
from telegram import send_message, edit_message_keyboard
from entities.keyboards import Practise_keyboard
from AI.ai_practise import *

# Вопрос хочет ли закрепить материал (Да/Нет)
async def send_practise_question(tg_id: int):
    
    return await send_message(
        chat_id=tg_id, 
        text="Хочешь закрепить материал, через перевод предложений?", 
        reply_markup=Practise_keyboard
    )


# Если пользователь не захотел закреплять слова
async def No_practise(callback, tg_id: int):

    await edit_message_keyboard(chat_id=tg_id, message_id=callback["message"]["message_id"], reply_markup=None)

    data = await get_practise(tg_id=tg_id)

    if not data:
        return None
    
    await redis_client.delete(f"practise:{tg_id}")

    return await send_message(chat_id=tg_id, text="Ну хорошо, в следующий раз!")


# Основная логика выдачи задачи для пользователя
async def send_next_task(tg_id: int):
    data = await get_session_practise(tg_id=tg_id)

    if not data:
        return await send_message(chat_id=tg_id, text="⏰ Сессия уже истекла")

    index = data["index"]
    tasks = data["tasks"]

    if index >= len(tasks):
        await redis_client.delete(f"practise_session:{tg_id}")
        return await send_message(
            chat_id=tg_id,
            text="Поздравляю! Ты попрактиковал все слова!"
        )

    task = tasks[index]

    text = "\n".join(
        f"{i+1}. {s}" for i, s in enumerate(task["ru_sentences"])
    )

    await send_message(chat_id=tg_id, text=f"✍️ Используй это слово: {task['word']}")
    return await send_message(
        chat_id=tg_id,
        text=text
    )



# Если пользователь нажал что хочет попрактиковать слова (Да)
async def Yes_practise(callback, tg_id:int):
    await edit_message_keyboard(chat_id=tg_id, message_id=callback["message"]["message_id"], reply_markup=None)

    data = await get_practise(tg_id=tg_id)

    if not data:
        return await send_message(chat_id=tg_id, text="⏰ Сессия уже истекла")
    
    words = [w["word"] for w in data["words"]]

    generated = await generate_sentences(words=words)

    if not generated:
        return await send_message(chat_id=tg_id, text="Ошибка генерации, пожалуйста попробуйте позже")
    
    
    session = {
        "tasks": generated,
        "index": 0
    }

    await set_session_practise(tg_id=tg_id, data=session)

    return await send_next_task(tg_id=tg_id)


async def handle_practise_answer(tg_id: int, user_text: str):
    data = await get_session_practise(tg_id=tg_id)

    if not data:
        return await send_message(chat_id=tg_id, text="Сессия не найдена")

    index = data["index"]
    task = data["tasks"][index]

    result = await check_translation(
        word=task["word"],
        ru_sentences=task["ru_sentences"],
        user_answer=user_text
    )

    data["index"] += 1   # 👈 ВАЖНО: только 1 слово за раз

    await set_session_practise(tg_id=tg_id, data=data)

    await send_message(chat_id=tg_id, text=result)

    return await send_next_task(tg_id=tg_id)