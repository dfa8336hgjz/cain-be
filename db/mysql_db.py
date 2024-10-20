import os

from dotenv import load_dotenv
from mysql.connector.aio import connect, MySQLConnectionAbstract


load_dotenv()

# Hàm để kết nối đến cơ sở dữ liệu
async def get_mysql_connection() -> MySQLConnectionAbstract:
    cnx = await connect(
        database=os.getenv("MYSQL_DB"),
        user=os.getenv("MYSQL_USER"),
        host=os.getenv("MYSQL_SERVER"),
        port=int(os.getenv("MYSQL_PORT")),
        password=os.getenv("MYSQL_PASSWORD"),
    )
    await cnx.set_autocommit(False)
    return cnx
