upd 27.02.25

Периодически, из-за некоторых аудио файлов, программа прекращала свою работу и через код не получилось пока решить проблему.
Чтобы код продолжал работать, необходимо запускать скрипт restart_whisper.ps1, он проверяет работает ли код в данный момент, если не работает
то проверяет файл errors, получает оттуда путь к проблемному аудио файлу и удаляет его, после чего заного запускает основной код обработки.
Также пришлось переписать ссылки, потому что powershell почему-то не понимал относительные ссылки :(

Порядок запуска кода:

1) python work.py - основной код который обрабатывает аудио файлы и проставляет аналитику через нейронку
2) python get_ton_graph.py - код который обрабатывает уже текстовые файлы после обработки аудио, собирает персональные статистики по людям в соовтетствующие эксель файлы
3) python get_sum_stat.py - собирает сводник в одном файле на базе эксель файлов разбитых по людям