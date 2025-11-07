"""Connect to PostgreSQL and load a DataFrame into a table.

This script no longer imports `df` from `hello` (that variable isn't exported).
It reads a source file (defaults to the orders part file) into a DataFrame,
then writes it to Postgres using SQLAlchemy. A DBAPI cursor example is
kept using engine.raw_connection() if you need to run cursor-specific code.
"""

import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text


load_dotenv()

# Load DB config from environment with sensible defaults
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'de_retail_db')
DB_USER = os.getenv('DB_USER', 'de_retail_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'che')
DB_PORT = os.getenv('DB_PORT', '5432')


def make_engine():
    url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)


def main():
    # Default source CSV/part file for orders (change if needed)
    src = os.getenv('SRC_ORDERS_FILE', 'data/retail_db/orders/part-00000')

    if not os.path.exists(src):
        print(f"Source file not found: {src}")
        return

    df = pd.read_csv(src,chunksize=10000)
    
    

    engine = make_engine()

    try:
        # use a transactional context so DROP is committed automatically
        with engine.begin() as conn:
            conn.execute(text("DROP TABLE IF EXISTS public.orders CASCADE;"))
        # Write DataFrame to Postgres using SQLAlchemy engine
        for idx,DF in enumerate(df):
            print(f'Processing chunk {idx} with shape {DF.shape}')
            DF.to_sql('orders', engine, if_exists='append', index=False)

        # Read back using pandas to verify
        res = pd.read_sql('SELECT * FROM orders limit 10;', engine)
        print('Sample rows from orders table:')
        print(res)

        # Example: if you need a DBAPI cursor directly (raw_connection() may not support 'with')
        raw_conn = engine.raw_connection()
        try:
            cur = raw_conn.cursor()
            try:
                cur.execute('SELECT count(*) FROM orders;')
                print('orders count (via cursor):', cur.fetchone()[0])
            finally:
                cur.close()
            raw_conn.commit()
        finally:
            raw_conn.close()

    except Exception as e:
        print('Database error:', e)
        pass

    finally:
        engine.dispose()


if __name__ == '__main__':
    main()




#  Write CSV Data from Files to Database Tables in Chunks

