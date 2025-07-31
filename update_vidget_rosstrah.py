import os
import sys
import logging
import pymysql
from pymysql import MySQLError as PyMysqlError
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extras import RealDictCursor

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
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_DATABASE"),
}

db_uri = os.getenv("DB_URI")
target_table = os.getenv("TARGET_TABLE", "Vidget_Rosstrah_AgentManager")

def get_pg_connection():
    return psycopg2.connect(**db_params)

def fetch_data_from_db(query: str, params: tuple = ()):
    try:
        with get_pg_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                result = cur.fetchall()
                logger.info(f"Получено {len(result)} записей из БД")
                return result
    except Exception as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        sys.exit(1)

def upload_to_sql(df: pd.DataFrame):
    if not db_uri:
        logger.error("Не задан DB_URI")
        sys.exit(1)

    engine = create_engine(db_uri)
    with engine.begin() as conn:
        df.to_sql(name=target_table, con=conn, if_exists='replace', index=False)
        logger.info(f"Данные успешно обновлены в таблице {target_table}")

def first_update():
    logger.info("Начато единоразовое обновление vidget_rosstrah")

    query = """
        SELECT
            pau.email AS agent,
            pau2.email AS manager
        FROM public.app_users pau
        LEFT JOIN public.app_users pau2 ON pau.manager_id = pau2.id
        INNER JOIN public.orders_paid_operations popo ON popo.user_id = pau.id
        WHERE popo.paid_operation_id = 227 
        and popo.is_owner = true
    """
    data = fetch_data_from_db(query)

    if not data:
        logger.warning("Нет данных для загрузки")
        return

    df = pd.DataFrame(data)
    df.dropna(subset=['agent'], inplace=True)
    unique_agents = df['agent'].nunique()
    logger.info(f"Получено {unique_agents} уникальных pau.email (agent)")

    upload_to_sql(df)

def update_vidget_rosstrah():
    logger.info("Начато обновление vidget_rosstrah")
    yesterday = datetime.now() - timedelta(days=2)

    query = """
        SELECT
            pau.email AS agent,
            pau2.email AS manager
        FROM public.app_users pau
        LEFT JOIN public.app_users pau2 ON pau.manager_id = pau2.id
        INNER JOIN public.orders_paid_operations popo ON popo.user_id = pau.id
        WHERE popo.paid_operation_id = 227
        and popo.is_owner = true
        AND popo.registered_date > %s
    """
    data = fetch_data_from_db(query, (yesterday,))

    if not data:
        logger.warning("Нет новых данных для обновления")
        return

    df = pd.DataFrame(data)
    df.dropna(subset=['agent'], inplace=True)
    unique_agents = df['agent'].nunique()
    logger.info(f"Получено {unique_agents} уникальных pau.email (agent)")

    upload_to_sql(df)

if __name__ == "__main__":
    update_vidget_rosstrah()