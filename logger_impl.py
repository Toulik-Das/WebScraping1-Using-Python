import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = 'D:\Importants\cricket\D\logs\scrap_cric\scrap_cric.log'
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)

# below maxBytes is equal to 10 MB
handler = RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
