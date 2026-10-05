import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///steam.db")

query_list = {
    "AVG_PRICE_BY_YEAR": """
        SELECT
            SUBSTR(release_date, -4) AS release_year,
            ROUND(AVG(price), 2) AS average_price_eur,
            COUNT(*) AS games_count
        FROM games
        WHERE release_date IS NOT NULL
        GROUP BY SUBSTR(release_date, -4)
        ORDER BY release_year
    """,

    "GAMES_BY_PLATFORM_COMBINATION": """
        SELECT
            platforms,
            COUNT(*) AS games_count,
            ROUND(AVG(price), 2) AS average_price_eur
        FROM games
        WHERE platforms IS NOT NULL
        GROUP BY platforms
        ORDER BY games_count DESC
    """,

    "GAMES_BY_DISCOUNT_RANGE": """
        SELECT
            CASE
                WHEN COALESCE(discount, 0) = 0 THEN '0%: без скидки'
                WHEN discount BETWEEN 1 AND 25 THEN '1-25%'
                WHEN discount BETWEEN 26 AND 50 THEN '26-50%'
                WHEN discount BETWEEN 51 AND 75 THEN '51-75%'
                ELSE '76-100%'
            END AS discount_range,
            COUNT(*) AS games_count,
            ROUND(AVG(price), 2) AS average_price_after_discount_eur
        FROM games
        GROUP BY discount_range
        ORDER BY MIN(COALESCE(discount, 0))
    """,

    "GAMES_BY_RATING_RANGE": """
        SELECT
            CASE
                WHEN rating < 60 THEN 'до 60'
                WHEN rating < 80 THEN '60-79'
                WHEN rating < 90 THEN '80-89'
                ELSE '90 и выше'
            END AS rating_range,
            COUNT(*) AS games_count,
            ROUND(AVG(price), 2) AS average_price_eur
        FROM games
        WHERE rating IS NOT NULL
        GROUP BY rating_range
        ORDER BY MIN(rating)
    """,

    "GAMES_BY_PRICE_RANGE": """
        SELECT
            CASE
                WHEN price = 0 THEN 'Бесплатно'
                WHEN price < 5 THEN 'Меньше 5 €'
                WHEN price < 15 THEN '5-14.99 €'
                WHEN price < 30 THEN '15-29.99 €'
                ELSE '30 € и выше'
            END AS price_range,
            COUNT(*) AS games_count,
            ROUND(AVG(rating), 1) AS average_rating
        FROM games
        WHERE price IS NOT NULL
        GROUP BY price_range
        ORDER BY MIN(price)
    """
}


def run_query(query: str) -> pd.DataFrame:
    with engine.connect() as connection:
        return pd.read_sql_query(text(query), connection)


if __name__ == "__main__":
    for name, sql in query_list.items():
        print(f"\n{name}")
        print(run_query(sql).to_string(index=False))