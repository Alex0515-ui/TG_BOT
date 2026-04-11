from entities.models import Levels, Mode


Main_menu_keyboard = {
    "keyboard": [
        [
            {"text": "📚 Учить слова"},
            {"text": "⚙️ Выбрать режим"}
        ],  
        [
            {"text": "🎯 Выбрать уровень"}
        ]
    ],
    "resize_keyboard": True
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