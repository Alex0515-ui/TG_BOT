from datetime import datetime, timezone, timedelta
from services.word_service import WordService
from entities.models import User, User_words, Word_Status


# ====================== SAVE_WORD_TO_DB тесты ===================

# Успешное сохранение нового слова 
def test_save_word_creates_new(db):
    user = User(telegram_id=123, first_name="Almas")
    db.add(user)
    db.commit()

    word = WordService.save_word_to_db(db=db, tg_id=123, word_id=1)

    assert word is not None
    assert word.user_id == user.id
    assert word.word_id == 1
    assert word.repetition_stage == 0
    assert word.status == Word_Status.LEARNING
    assert word.next_review_date is not None

# Проверка на дубликат, чтобы дважды в БД не сохранялось
def test_save_word_duplicate(db):
    user = User(telegram_id=123, first_name="Sasha")
    db.add(user)
    db.commit()

    word1 = WordService.save_word_to_db(db=db, tg_id=123, word_id=1)
    word2 = WordService.save_word_to_db(db=db, tg_id=123, word_id=1)

    assert word1.id == word2.id
    assert db.query(User_words).count() == 1


# =============== PROCESS_ANSWER метод тесты ===================

# Успешный прогресс пользователя
def test_process_answer_correct_progress(db):
    user = User(telegram_id=123, first_name="Alehandro")
    db.add(user)
    db.commit()

    word = User_words(
        user_id=user.id,
        word_id=1,
        status=Word_Status.LEARNING,
        repetition_stage=1
    )
    db.add(word)
    db.commit()

    WordService.process_answer(db=db, word=word, correct=True)

    assert word.repetition_stage == 2
    assert word.status == Word_Status.LEARNING
    assert word.next_review_date is not None

# Полное изучение слова
def test_process_answer_learned(db):
    user = User(telegram_id=123, first_name="Alexandra")
    db.add(user)
    db.commit()

    word = User_words(
        user_id=user.id,
        word_id=1,
        status=Word_Status.LEARNING,
        repetition_stage=3
    )
    db.add(word)
    db.commit()

    WordService.process_answer(db=db, word=word, correct=True)

    assert word.status == Word_Status.LEARNED
    assert word.next_review_date is None

# Обнуление прогресса, если юзер ответил неправильно
def test_process_answer_incorrect(db):
    user = User(telegram_id=123, first_name="Alex")
    db.add(user)
    db.commit()

    word = User_words(
        user_id=user.id,
        word_id=1,
        status=Word_Status.LEARNING,
        repetition_stage=3
    )
    db.add(word)
    db.commit()

    WordService.process_answer(db=db, word=word, correct=False)

    assert word.repetition_stage == 0
    assert word.status == Word_Status.LEARNING
    assert word.next_review_date is not None


# ===== GET_WORDS_TO_REPEAT тесты ===================


# Проверяем что даты не слишком ранние для повторения
def test_get_words_to_repeat_filters_by_date(db):
    user = User(telegram_id=123, first_name="Test")
    db.add(user)
    db.commit()

    fixed_now = datetime(2026, 1, 1, tzinfo=timezone.utc)

    word1 = User_words(
        user_id=user.id,
        word_id=1,
        next_review_date=fixed_now - timedelta(days=1)
    )

    word2 = User_words(
        user_id=user.id,
        word_id=2,
        next_review_date=fixed_now + timedelta(days=1)
    )

    db.add_all([word1, word2])
    db.commit()

    result = WordService.get_words_to_repeat(db=db, tg_id=123, now=fixed_now)

    assert len(result) == 1
    assert result[0].word_id == 1