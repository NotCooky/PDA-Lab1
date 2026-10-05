import pandas as pd
import sqlalchemy


from sqlalchemy import create_engine
from sqlalchemy import text

data_source = "sqlite:///steam.db"
engine = create_engine(data_source)

params = {
    "high_rating": 85,
    "low_rating": 80,
}

query_list = {
    "AVG_PRICE_BY_YEAR": """
    SELECT 
        SUBSTR(release_date, -4) AS year, 
        AVG(price),
        COUNT(*)
    FROM games
    WHERE SUBSTR(release_date, -4) >= "2023"
    GROUP BY SUBSTR(release_date, -4)""",

    "AVG_PRICE_ON_RATING": """
    SELECT 
        (rating / 10) * 10 AS rating_step, 
        AVG(price), 
        COUNT(*)
    FROM games
    GROUP BY FLOOR(rating / 10) * 10
    ORDER BY rating_step DESC""",

    "GAMES_ON_PLATFORMS_AVG_PRICE": """
    SELECT platforms, AVG(price) as average_price, COUNT(*) AS games_count 
    FROM games
    WHERE platforms IS NOT NULL
    GROUP BY platforms
    ORDER BY games_count DESC;""",

    "PRICE_GROUPS": """
        SELECT  
            (price / 10) * 10 AS price_step,
            AVG(rating),
            COUNT(*)
        FROM games
        WHERE rating IS NOT NULL 
        GROUP BY FLOOR(price / 10) * 10
        ORDER BY price_step DESC;
    """,

    "GAMES_BY_RATING": """
        SELECT 
            CASE
                WHEN rating < 60 THEN "<60"
                WHEN rating BETWEEN 60 AND 79 THEN "60-79"
                WHEN rating BETWEEN 80 AND 89 THEN "80-89"
                ELSE "90+"
            END AS rating_range,
            AVG(price * (1 - COALESCE(discount, 0) / 100)) AS average_price_with_discount,
            COUNT(*)   
        FROM games
        WHERE rating IS NOT NULL AND discount > 0
        GROUP BY rating_range
        ORDER BY rating_range DESC;
    """
}


def run_query(query, engine):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
        return df


if __name__ == "__main__":
    results = {}
    for name, sql in query_list.items():
        df = run_query(sql, engine)
        results[name] = df
        print(f"{name}")
        print(df)

