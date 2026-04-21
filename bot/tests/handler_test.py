from pytest_mock import mocker
from unittest.mock import AsyncMock
from handlers.word_learn_handlers import handle_answer, check_daily_limit
from handlers.user_handlers import handle_callback
from entities.models import *
import pytest
from datetime import datetime, timedelta, timezone, date


# ============ CHECK_DAILY_LIMIT тесты  =====================

# Проверяю что лимит еще есть
@pytest.mark.asyncio
async def test_check_daily_limit(mocker, db):
    user = User(first_name="Alex", telegram_id=123)
    db.add(user)
    db.commit()

    now = str(date.today())

    data = {'last_date': "2026-01-01"}
    mock_daily =  mocker.patch("handlers.word_learn_handlers.get_daily", return_value=data, new_callable=AsyncMock)

    result = await check_daily_limit(tg_id=user.telegram_id)

    assert result is False


# Проверка что лимит исчерпан
@pytest.mark.asyncio
async def test_check_daily_limit_true(mocker):
    
    today = str(date.today())

    mocker.patch(
        "handlers.word_learn_handlers.get_daily",
        return_value={"last_date": today},
        new_callable=AsyncMock
    )

    result = await check_daily_limit(tg_id=123)

    assert result is True


# ============ HANDLE_CALLBACK тесты =====================


# Проверяем что все функции правильно вызываются
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action, expected_call", 
    [
        ("set_lvl_A1", "handle_set_level"),
        ("set_mode_test", "handle_set_mode"),
        ("set_word_count_10", "handle_set_words"),
        ("answer_1_2_3", "handle_answer"),
        ("set_repeat", "start_repeat_session"),
        ("choose_level", "send_message"),
        ("choose_mode", "send_message"),
        ("set_learning", "start_learning"),
        ("start_dialogue", "start_dialogue"),
        ("set_practise_yes", "Yes_practise"),
        ("set_practise_no", "No_practise")
    ]
)
async def test_handle_callback_success(mocker, db, action, expected_call):
    tg_id = 123
    callback = {
        "from": {"id":tg_id},
        "data": action
    }
    mocks = {
        "handle_set_level": mocker.patch("handlers.user_handlers.handle_set_level", new_callable=AsyncMock),
        "handle_set_mode": mocker.patch("handlers.user_handlers.handle_set_mode", new_callable=AsyncMock),
        "handle_set_words": mocker.patch("handlers.user_handlers.handle_set_words", new_callable=AsyncMock),
        "handle_answer": mocker.patch("handlers.user_handlers.handle_answer", new_callable=AsyncMock),
        "start_repeat_session": mocker.patch("handlers.user_handlers.start_repeat_session", new_callable=AsyncMock),
        "send_message": mocker.patch("handlers.user_handlers.send_message", new_callable=AsyncMock),
        "start_learning": mocker.patch("handlers.user_handlers.start_learning", new_callable=AsyncMock),
        "start_dialogue": mocker.patch("handlers.user_handlers.start_dialogue", new_callable=AsyncMock),
        "Yes_practise": mocker.patch("handlers.user_handlers.Yes_practise", new_callable=AsyncMock),
        "No_practise": mocker.patch("handlers.user_handlers.No_practise", new_callable=AsyncMock),
    }

    await handle_callback(callback=callback, db=db)

    mocks[expected_call].assert_called_once()

    for name, mock in mocks.items():
        if name != expected_call:
            mock.assert_not_called()


# ============ HANDLE_ANSWER тесты (там куча строк) =============


# Правильный ответ при обучении
@pytest.mark.asyncio
async def test_handle_answer_success(mocker, db):
    tg_id = 123

    session_data = {
        "words": [
            {"id": 125, "word": "agree", "translation": "соглашаться", "example": "I agree"},
            {"id": 330, "word": "medicine", "translation": "Лекарство", "example": "Take medicine"},
            {"id": 160, "word": "information", "translation": "информация", "example": "I need info"},
            {"id": 149, "word": "enough", "translation": "достаточно", "example": "Enough time"},
            {"id": 135, "word": "choose", "translation": "выбирать", "example": "Choose color"},
        ],
        "current_index": 4,
        "options": ['Доброжелательный', 'Может быть', 'выбирать', 'да']
    }

    callback = {
        "from":{"id": tg_id},
        "data": "answer_learn_135_2",
        "message": {"message_id": 1}
    }

    mocker.patch("handlers.word_learn_handlers.get_session", return_value=session_data, new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.edit_message_keyboard", new_callable=AsyncMock)
    
    mock_send_message = mocker.patch("handlers.word_learn_handlers.send_message", new_callable=AsyncMock)
    mock_save_word_to_db = mocker.patch("handlers.word_learn_handlers.WordService.save_word_to_db")
    mock_process = mocker.patch("handlers.word_learn_handlers.WordService.process_answer")
    mock_finish = mocker.patch("handlers.word_learn_handlers.finish_learning")
    mock_delete = mocker.patch("handlers.word_learn_handlers.redis_client.delete", new_callable=AsyncMock)
    mock_set_practise = mocker.patch("handlers.word_learn_handlers.set_practise", new_callable=AsyncMock)
    mock_practise_question = mocker.patch("handlers.word_learn_handlers.send_practise_question", new_callable=AsyncMock)

    user = User(first_name="Test", telegram_id=123)
    db.add(user)
    db.commit()

    await handle_answer(callback=callback, db=db)

    mock_save_word_to_db.assert_called_once()
    mock_process.assert_not_called()
    mock_finish.assert_called_once()
    mock_delete.assert_called_once()

    mock_send_message.assert_any_call(chat_id=tg_id, text="✅ Правильно!")

    mock_send_message.assert_any_call(chat_id=tg_id, text="Поздравляю, ты прошел все слова!")


# Правильный ответ при повторении
@pytest.mark.asyncio
async def test_handle_answer_repeat_success(mocker, db):
    now = datetime.now(timezone.utc)

    user = User(first_name="Test", telegram_id=123)
    db.add(user)
    db.commit()

    word1 = User_words(
        user_id=user.id,
        word_id=149,
        status=Word_Status.LEARNING,
        repetition_stage=1,
        next_review_date=now - timedelta(days=1)
    )

    word2 = User_words(
        user_id=user.id,
        word_id=135,
        status=Word_Status.LEARNING,
        repetition_stage=1,
        next_review_date=now - timedelta(days=1)
    )

    word3 = User_words(
        user_id=user.id,
        word_id=160,
        status=Word_Status.LEARNING,
        repetition_stage=2,
        next_review_date=now - timedelta(days=1)
    )

    word4 = User_words(
        user_id=user.id,
        word_id=330,
        status=Word_Status.LEARNING,
        repetition_stage=1,
        next_review_date=now - timedelta(days=1)
    )

    word5 = User_words(
        user_id=user.id,
        word_id=125,
        status=Word_Status.LEARNING,
        repetition_stage=3,
        next_review_date=now - timedelta(days=1)
    )
    db.add_all([word1, word2, word3, word4, word5])
    db.commit()

    tg_id = 123

    session_data = {
        "words": [
            {"id": 125, "word": "agree", "translation": "соглашаться", "example": "I agree"},
            {"id": 330, "word": "medicine", "translation": "Лекарство", "example": "Take medicine"},
            {"id": 160, "word": "information", "translation": "информация", "example": "I need info"},
            {"id": 149, "word": "enough", "translation": "достаточно", "example": "Enough time"},
            {"id": 135, "word": "choose", "translation": "выбирать", "example": "Choose color"},
        ],
        "current_index": 3,
        "options": ['Доброжелательный', 'Может быть', 'достаточно', 'да']
    }

    callback = {
        "from":{"id": tg_id},
        "data": "answer_repeat_149_2",
        "message": {"message_id": 1}
    }

    mocker.patch("handlers.word_learn_handlers.get_repeat_session", return_value=session_data, new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.edit_message_keyboard", new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.redis_client.delete", new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.set_repeat_session",new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.send_word_repeat", new_callable=AsyncMock)

    mock_send_message = mocker.patch("handlers.word_learn_handlers.send_message", new_callable=AsyncMock)
    mock_save_word_to_db = mocker.patch("handlers.word_learn_handlers.WordService.save_word_to_db")
    mock_process = mocker.patch("handlers.word_learn_handlers.WordService.process_answer")
    mock_finish = mocker.patch("handlers.word_learn_handlers.finish_learning")
    mock_set_practise = mocker.patch("handlers.word_learn_handlers.set_practise", new_callable=AsyncMock)
    mock_practise_question = mocker.patch("handlers.word_learn_handlers.send_practise_question", new_callable=AsyncMock)

    

    await handle_answer(callback=callback, db=db)

    mock_process.assert_called_once()
    mock_send_message.assert_any_call(chat_id=tg_id, text="✅ Правильно!")
    mock_save_word_to_db.assert_not_called()
    mock_finish.assert_not_called()
    mock_set_practise.assert_not_called()
    mock_practise_question.assert_not_called()


# Неправильный ответ при обучении
@pytest.mark.asyncio
async def test_handle_answer_incorrect(mocker, db):
    tg_id = 123

    session_data = {
        "words": [
            {"id": 125, "word": "agree", "translation": "соглашаться", "example": "I agree"},
            {"id": 330, "word": "medicine", "translation": "Лекарство", "example": "Take medicine"},
            {"id": 160, "word": "information", "translation": "информация", "example": "I need info"},
            {"id": 149, "word": "enough", "translation": "достаточно", "example": "Enough time"},
            {"id": 135, "word": "choose", "translation": "выбирать", "example": "Choose color"},
        ],
        "current_index": 4,
        "options": ['Доброжелательный', 'Может быть', 'выбирать', 'да']
    }

    callback = {
        "from":{"id": tg_id},
        "data": "answer_learn_135_1",
        "message": {"message_id": 1}
    }

    mocker.patch("handlers.word_learn_handlers.get_session", return_value=session_data, new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.edit_message_keyboard", new_callable=AsyncMock)
    
    mock_send_message = mocker.patch("handlers.word_learn_handlers.send_message", new_callable=AsyncMock)
    mock_save_word_to_db = mocker.patch("handlers.word_learn_handlers.WordService.save_word_to_db")
    mock_process = mocker.patch("handlers.word_learn_handlers.WordService.process_answer")
    mock_finish = mocker.patch("handlers.word_learn_handlers.finish_learning")
    mock_delete = mocker.patch("handlers.word_learn_handlers.redis_client.delete", new_callable=AsyncMock)
    mock_set_practise = mocker.patch("handlers.word_learn_handlers.set_practise", new_callable=AsyncMock)
    mock_practise_question = mocker.patch("handlers.word_learn_handlers.send_practise_question", new_callable=AsyncMock)

    user = User(first_name="Test", telegram_id=123)
    db.add(user)
    db.commit()

    await handle_answer(callback=callback, db=db)

    mock_save_word_to_db.assert_not_called()
    mock_process.assert_not_called()
    mock_finish.assert_called_once()
    mock_delete.assert_called_once()
    mock_practise_question.assert_called_once()
    mock_set_practise.assert_called_once()

    mock_send_message.assert_any_call(chat_id=tg_id, text="Поздравляю, ты прошел все слова!")


# Проверка правильного ответа при повторении
@pytest.mark.asyncio
async def test_handle_answer_repeat_success(mocker, db):
    now = datetime.now(timezone.utc)

    user = User(first_name="Test", telegram_id=123)
    db.add(user)
    db.commit()

    word1 = User_words(
        user_id=user.id,
        word_id=149,
        status=Word_Status.LEARNING,
        repetition_stage=1,
        next_review_date=now - timedelta(days=1)
    )

    word2 = User_words(
        user_id=user.id,
        word_id=135,
        status=Word_Status.LEARNING,
        repetition_stage=3,
        next_review_date=now - timedelta(days=1)
    )

    word3 = User_words(
        user_id=user.id,
        word_id=160,
        status=Word_Status.LEARNING,
        repetition_stage=2,
        next_review_date=now - timedelta(days=1)
    )

    word4 = User_words(
        user_id=user.id,
        word_id=330,
        status=Word_Status.LEARNING,
        repetition_stage=1,
        next_review_date=now - timedelta(days=1)
    )

    word5 = User_words(
        user_id=user.id,
        word_id=125,
        status=Word_Status.LEARNING,
        repetition_stage=3,
        next_review_date=now - timedelta(days=1)
    )
    db.add_all([word1, word2, word3, word4, word5])
    db.commit()

    tg_id = 123

    session_data = {
        "words": [
            {"id": 125, "word": "agree", "translation": "соглашаться", "example": "I agree"},
            {"id": 330, "word": "medicine", "translation": "Лекарство", "example": "Take medicine"},
            {"id": 160, "word": "information", "translation": "информация", "example": "I need info"},
            {"id": 149, "word": "enough", "translation": "достаточно", "example": "Enough time"},
            {"id": 135, "word": "choose", "translation": "выбирать", "example": "Choose color"},
        ],
        "current_index": 3,
        "options": ['Доброжелательный', 'Может быть', 'достаточно', 'да']
    }

    callback = {
        "from":{"id": tg_id},
        "data": "answer_repeat_149_1",
        "message": {"message_id": 1}
    }

    mocker.patch("handlers.word_learn_handlers.get_repeat_session", return_value=session_data, new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.edit_message_keyboard", new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.redis_client.delete", new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.set_repeat_session",new_callable=AsyncMock)
    mocker.patch("handlers.word_learn_handlers.send_word_repeat", new_callable=AsyncMock)

    mock_send_message = mocker.patch("handlers.word_learn_handlers.send_message", new_callable=AsyncMock)
    mock_save_word_to_db = mocker.patch("handlers.word_learn_handlers.WordService.save_word_to_db")
    mock_process = mocker.patch("handlers.word_learn_handlers.WordService.process_answer")
    mock_finish = mocker.patch("handlers.word_learn_handlers.finish_learning")
    mock_set_practise = mocker.patch("handlers.word_learn_handlers.set_practise", new_callable=AsyncMock)
    mock_practise_question = mocker.patch("handlers.word_learn_handlers.send_practise_question", new_callable=AsyncMock)

    await handle_answer(callback=callback, db=db)

    mock_process.assert_called_once()
    assert word1.status == Word_Status.LEARNING
    mock_save_word_to_db.assert_not_called()
    mock_finish.assert_not_called()
    mock_set_practise.assert_not_called()
    mock_practise_question.assert_not_called()

