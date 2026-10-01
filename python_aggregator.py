import pandas as pd
import sqlalchemy


from sqlalchemy import create_engine
from sqlalchemy import text

data_source = "sqlite:///steam.db"
engine = create_engine(data_source)

params = {
    "target_date": "10 Aug, 2023"
}

query_list = {
    "AVG_PRICE_BY_YEAR": """SELECT release_date, AVG(price)
                            FROM games
                            WHERE release_date >= :target_date
                            GROUP BY release_date""",
    "MOST_DISCOUNT": """SELECT title, discount
                        FROM games
                        WHERE""",
    "GAMES_FOR_LESS_THAN_DOLLAR": "",
    "GAMES_WITH_RATING_HIGH": "",
    "GAMES_WITH_RATING_LOW": ""
}


def run_query(query, engine):
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params=params)
        return df


if __name__ == "__main__":
    for query in query_list.items():
        df = run_query(query, engine)
        results = {}