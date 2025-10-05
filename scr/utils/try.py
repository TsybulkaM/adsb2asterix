# Установка: pip install adsb
from adsb.sbs import MSG1

# 1. Создаем объект сообщения типа MSG1 (Identification and Category)
#    Это объектный подход, в отличие от словаря в pyModeS.
msg = MSG1()

# 2. Заполняем поля объекта
msg.icao = "4CA1FA"
msg.callsign = "LOT456"

# 3. Вызываем метод encode() для получения SBS-строки
sbs_string = msg.encode()

# 4. Выводим результат
print(f"Объект сообщения: {msg}")
print(f"Закодированная SBS-строка: {sbs_string}")