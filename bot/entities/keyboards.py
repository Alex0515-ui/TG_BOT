from entities.models import Levels, Mode

# Главное меню кнопка
Main_menu_keyboard = {
    "keyboard": [ 
        [
            {"text": "Главное меню"}
        ]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": False
}

# Кнопки в главном меню
Menu_keyboard = {
    "inline_keyboard": [
        [
            {"text":"💬 Диалог с ИИ ассистентом", "callback_data": "start_dialogue"}
        ],
        [
            {"text": "📚 Учить слова", "callback_data": "set_learning"},
        ],
        [
            {"text": "⚙️ Выбрать режим", "callback_data": "choose_mode"},
        ],
        [
            {"text": "🎯 Выбрать уровень", "callback_data": "choose_level"},
        ]
    ]
}

# Выбор режима
Mode_keyboard = { 
    "inline_keyboard": [
        [
            {"text": f"{mode.name}", "callback_data": f"set_mode_{mode.name}"}
            for mode in Mode
        ]
        
    ]
    
}

# Выбор уровня
Level_keyboard = { 
    "inline_keyboard": [
        [
            {"text": f"{level.name}, ({level.value})", "callback_data": f"set_lvl_{level.name}"}
            for level in list(Levels)[i:i+2]
        ]
        for i in range(0, len(Levels), 2)
    ]
}

word_counts = [5, 10, 15, 20]

# Выбор количества слов для изучения
Word_count_keyboard = {
    "inline_keyboard" : [
        [
            {"text": f"{count} слов",
             "callback_data": f"set_word_count_{count}"}
            for count in word_counts
        ]
    ]
}

# Кнопка для повторения слов
Repeat_word_keyboard = {
    "inline_keyboard": [
        [
            {"text": "Давай!", "callback_data": "set_repeat"}
        ]
    ]
}

# Кнопки для вопроса будет ли практика слов
Practise_keyboard = {
    "inline_keyboard": [
        [
            {"text": "Давай", "callback_data": "set_practise_yes"},
            {"text": "Нет, не сегодня", "callback_data": "set_practise_no"}
        ]
    ]
}