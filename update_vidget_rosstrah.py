import os
import sys
import logging
import pymysql
from pymysql import MySQLError as PyMysqlError
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

db_params = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3366)),
    "database": os.getenv("DB_DATABASE"),
    "charset": 'utf8mb4',
}

db_uri = os.getenv("DB_URI")
target_table = os.getenv("TARGET_TABLE", "Vidget_Rosstrah_AgentManager")

def first_update():
    logger.info("Начато единоразовое обновление vidget_rosstrah")

    if None in db_params.values() or not db_uri:
        logger.error("Не заданы обязательные параметры подключения!")
        sys.exit(1)

    engine = create_engine(db_uri)

    try:
        conn = pymysql.connect(**db_params, cursorclass=pymysql.cursors.DictCursor)
    except PyMysqlError as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    pau.email as 'agent',
                    pau2.email as 'manager'
                FROM public.app_users pau
                LEFT JOIN public.app_users pau2 ON pau.manager_id = pau2.id
                INNER JOIN public.orders_paid_operations popo ON popo.user_id = pau.id
                WHERE popo.paid_operation_id = 227
            """)

            db_data = cur.fetchall()
            logger.info(f"Получено {len(db_data)} записей из БД")

            if not db_data:
                logger.error("Данные не получены из БД")
                return

            column_names = [desc[0] for desc in cur.description]

        df_du = pd.DataFrame(db_data, columns=column_names)

        with engine.begin() as conn:
            if not df_du.empty:
                df_du.to_sql(
                    name=target_table,
                    con=conn,
                    if_exists='replace',
                    index=False
                )
        logger.info(f"Данные успешно обновлены в таблице {target_table}")

    except Exception as e:
        logger.exception(f"Критическая ошибка: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()

def update_vidget_rosstrah():
    logger.info("Начато обновление vidget_rosstrah")

    yesterday = datetime.now() - timedelta(days=2)

    if None in db_params.values() or not db_uri:
        logger.error("Не заданы обязательные параметры подключения!")
        sys.exit(1)

    engine = create_engine(db_uri)

    try:
        conn = pymysql.connect(**db_params, cursorclass=pymysql.cursors.DictCursor)
    except PyMysqlError as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        sys.exit(1)

    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT
                    pau.email as 'agent',
                    pau2.email as 'manager'
                FROM public.app_users pau
                LEFT JOIN public.app_users pau2 ON pau.manager_id = pau2.id
                INNER JOIN public.orders_paid_operations popo ON popo.user_id = pau.id
                WHERE popo.paid_operation_id = 227
                AND popo.registered_date > %s
            """, yesterday)
            
            db_data = cur.fetchall()
            logger.info(f"Получено {len(db_data)} записей из БД")
            
            if not db_data:
                logger.error("Данные не получены из БД")
                return

            column_names = [desc[0] for desc in cur.description]

        df_du = pd.DataFrame(db_data, columns=column_names)
        
        with engine.begin() as conn:
            if not df_du.empty:
                df_du.to_sql(
                    name=target_table,
                    con=conn,
                    if_exists='replace',
                    index=False
                )
        logger.info(f"Данные успешно обновлены в таблице {target_table}")

    except Exception as e:
        logger.exception(f"Критическая ошибка: {str(e)}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    update_vidget_rosstrah()