import os
import logging
import sys

# --- Клас для перенаправлення print() (Винесено на верхній рівень файлу) ---
class LoggerWriter:
    """
    Користувацький об'єкт, схожий на файл, для перенаправлення sys.stdout та sys.stderr до логера.
    """
    def __init__(self, logger_instance, level): # Змінено параметр logger на logger_instance для чіткості
        self.logger = logger_instance
        self.level = level
        self.buffer = ''

    def write(self, message):
        # Буферизуємо повідомлення до зустрічі нового рядка
        if isinstance(message, bytes): # Обробка випадків, коли повідомлення можуть бути байтами
            message = message.decode('utf-8', errors='replace')
            
        self.buffer += message
        if '\n' in self.buffer:
            lines = self.buffer.split('\n')
            for line in lines[:-1]:
                if line: 
                    self.logger.log(self.level, line.rstrip()) 
            self.buffer = lines[-1] 

    def flush(self):
        # Логуємо будь-який залишок у буфері, коли викликається flush
        if self.buffer:
            self.logger.log(self.level, self.buffer.rstrip())
            self.buffer = ''

def setup_logging(aim_dir):
    """
    Налаштовує систему логування, створює папку для логів та перенаправляє
    stdout та stderr до логера. Цю функцію слід викликати один раз на початку головного скрипту.
    """
    # LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    # LOG_DIR = os.path.join(aim_dir, 'logs')
    # os.makedirs(LOG_DIR, exist_ok=True) 

    # LOG_FILE_PATH = os.path.join(LOG_DIR, 'mock_scraper.log')
    LOG_FILE_PATH = os.path.join(aim_dir, 'mock_scraper.log')

    # Конфігуруємо логування для виводу у файл та консоль
    logging.basicConfig(
        level=logging.INFO, # Встановлюємо базовий рівень логування
        format='%(asctime)s - %(levelname)s - %(message)s', # Формат повідомлень логу
        handlers=[
            logging.FileHandler(LOG_FILE_PATH, encoding='utf-8'), # Логуємо у файл з UTF-8
            logging.StreamHandler() # Логуємо у консоль
        ]
    )
    # Отримуємо екземпляр логера для поточного модуля, який буде використовуватися LoggerWriter
    logger_instance = logging.getLogger(__name__) 

    # Перенаправляємо stdout та stderr до логера
    sys.stdout = LoggerWriter(logger_instance, logging.INFO)
    sys.stderr = LoggerWriter(logger_instance, logging.ERROR)

    # Повертаємо логер, щоб головний скрипт міг його використовувати
    return logger_instance

def restore_stdout_stderr():
    """
    Відновлює sys.stdout та sys.stderr до їхніх оригінальних значень.
    Викликається у finally блоці головного скрипту.
    """
    # Тепер LoggerWriter доступний, оскільки він визначений на верхньому рівні модуля
    if sys.stdout is not None and isinstance(sys.stdout, LoggerWriter):
        sys.stdout.flush()
        sys.stdout = sys.__stdout__ 
    if sys.stderr is not None and isinstance(sys.stderr, LoggerWriter):
        sys.stderr.flush()
        sys.stderr = sys.__stderr__ 

# У модулі logging в Python, окрім logger.info(), ви можете використовувати наступні стандартні рівні логування, які вказують на серйозність події:

# logger.debug(message): Використовується для детальної інформації, яка зазвичай цікава лише при діагностиці проблем. Це найнижчий рівень деталізації.

# logger.info(message): Використовується для загальної інформації про хід виконання програми, яка підтверджує, що все працює, як очікувалося.

# logger.warning(message): Вказує на те, що сталося щось несподіване, або на проблему в найближчому майбутньому (наприклад, "майже заповнений дисковий простір"). Програма все ще працює, як очікувалося.

# logger.error(message): Вказує на більш серйозну проблему, яка завадила програмі виконати якусь функцію.

# logger.critical(message): Вказує на серйозну помилку, яка може призвести до зупинки програми або її повного збою. Це найвищий рівень серйозності.

# Вибір рівня залежить від важливості та характеру повідомлення, яке ви хочете залогувати. Ви можете налаштувати ваш логер, щоб він виводив повідомлення лише певного рівня або вище. Наприклад, у вашому скрипті логер налаштований на level=logging.INFO, що означає, що він буде виводити повідомлення INFO, WARNING, ERROR та CRITICAL, але ігноруватиме DEBUG.