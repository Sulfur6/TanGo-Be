import os

BASE_DIR = os.path.abspath(os.path.join(os.getcwd()))
LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)  # 创建路径

DATABASE_URL = "mysql://root:tango2023!!!@sh-cynosdbmysql-grp-azvmb5pu.sql.tencentcdb.com:27870/tango"
REDIS_URL = f"redis://localhost:6379/0"
