import os
import time
import sys
import logging
import pymysql
from pymysql import MySQLError as PyMysqlError
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine, text

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def update_vidget_rosstrah():
    logger.info("Начато обновление vidget_rosstrah")
    
    db_params = {
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "host": os.getenv("MYSQL_HOST"),
        "port": int(os.getenv("MYSQL_PORT", 3366)),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": 'utf8mb4',
    }
    
    db_uri = os.getenv("DB_URI")
    target_table = os.getenv("TARGET_TABLE", "Vidget_Rosstrah_AgentManager")

    if None in db_params.values() or not db_uri:
        logger.error("Не заданы обязательные параметры подключения!")
        sys.exit(1)

    try:
        conn = pymysql.connect(**db_params, cursorclass=pymysql.cursors.DictCursor)
    except PyMysqlError as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        sys.exit(1)

    try:
        now = datetime.now()
        date_from = (now - timedelta(days=4)).strftime("%Y-%m-%d")
        date_to = (now + timedelta(days=1)).strftime("%Y-%m-%d")

        with conn.cursor() as cur:
            cur.execute(f"""

            """, (date_from, date_to))
            
            db_data = cur.fetchall()
            logger.info(f"Получено {len(db_data)} записей из БД")
            
            if not db_data:
                logger.error("Данные не получены из БД")
                return

            column_names = [desc[0] for desc in cur.description]

        engine = create_engine(db_uri)
        df_du = pd.DataFrame(db_data, columns=column_names)
        
        with engine.begin() as conn:
            delete_sql = text(f"DELETE FROM {target_table}")
            conn.execute(delete_sql)
            
            if not df_du.empty:
                df_du.to_sql(
                    name=target_table,
                    con=conn,
                    if_exists='append',
                    index=False
                )
        logger.info(f"Данные успешно обновлены в таблице {target_table}")

    except Exception as e:
        logger.exception(f"Критическая ошибка: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    update_vidget_rosstrah()