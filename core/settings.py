import os

BASE_DIR = os.path.abspath(os.path.join(os.getcwd()))
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)  # 创建路径

DATABASE_URL = "mysql://root:password@localhost:3306/tango"
REDIS_URL = "redis://localhost:6739/0"
