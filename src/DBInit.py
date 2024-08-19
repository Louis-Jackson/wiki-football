from feapder.db.mysqldb import MysqlDB
from loguru import logger

class DBInit:
    def __init__(self, table_name):
        self.db = MysqlDB(
            ip="192.168.2.215",
            port=3306,    
            user_name="root",
            user_pass="menmen8888",
            db="soccer_database"
        )
        
        logger.add(f"../logs/{table_name}.log", rotation="1 MB", encoding="utf-8")