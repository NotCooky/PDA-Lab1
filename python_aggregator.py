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
        release_date, 
        AVG(price)
    FROM games
    WHERE SUBSTR(release_date, -4) >= "2023"
    GROUP BY release_date""",

    "MOST_DISCOUNT": """
    SELECT 
        title,
        discount, 
        price
    FROM games
    WHERE discount > 0
    ORDER BY discount DESC
    LIMIT 10""",

    "GAMES_FOR_LESS_THAN_DOLLAR": """SELECT title, price
    FROM games
    Where price < 10
    ORDER BY price DESC""",

    "GAMES_WITH_RATING_HIGH": """
        SELECT 
            title, 
            rating,
            release_date
        FROM games
        WHERE rating IS NOT NULL 
          AND rating >= :high_rating
        ORDER BY rating DESC, title ASC;
    """,

    "GAMES_WITH_RATING_LOW": """
        SELECT 
            title, 
            rating,
            release_date
        FROM games
        WHERE rating IS NOT NULL 
          AND rating <= :low_rating
        ORDER BY rating ASC, title ASC;
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
        print(df)

