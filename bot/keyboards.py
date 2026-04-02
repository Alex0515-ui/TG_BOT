from models import Levels, Mode

# Выбор режима
Mode_keyboard = { 
    "inline_keyboard": [
        [
            {"text": f"{mode.name}, {mode.value}", "callback_data": f"set_mode_{mode.name}"}
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