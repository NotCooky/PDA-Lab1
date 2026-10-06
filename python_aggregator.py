from db import SessionLocal, Game
from tabulate import tabulate
from sqlalchemy import select, func, case

year = func.substr(Game.release_date, -4)

month = func.substr(Game.release_date, 4, 2)

season = case(
    (month.in_(["12", "01", "02"]), "Зима"),
    (month.in_(["03", "04", "05"]), "Весна"),
    (month.in_(["06", "07", "08"]), "Лето"),
    (month.in_(["09", "10", "11"]), "Осень"),
).label("season")

price_range = case(
    (Game.price == 0, "Бесплатно"),
    (Game.price < 5, "Меньше 5 €"),
    (Game.price < 15, "5-14.99 €"),
    (Game.price < 30, "15-29.99 €"),
    else_="30 € и выше",
).label("price_range")

rating_range = case(
    (Game.rating < 60, "До 60"),
    (Game.rating < 80, "60-79"),
    (Game.rating < 90, "80-89"),
    else_="90 и выше",
).label("rating_range")

sort_by_platforms = (
    select(Game.platforms,
           func.count(Game.app_id).label("games_count"),
           func.avg(Game.price).label("average_price"),
           )
           .group_by(Game.platforms)
           .order_by(func.count(Game.app_id).desc())
)

average_price_by_year = (
    select(year.label("release_year"),
           func.count(Game.app_id).label("games_count"),
           func.avg(Game.price).label("average_price")
           )
           .where(Game.release_date.is_not(None), Game.release_date != "")
           .group_by(year)
           .order_by(year)
)

average_discount_by_season = (
    select(
        season,
        func.round(func.avg(Game.discount), 1).label("average_discount"),
        func.count(Game.app_id).label("games_count"),
    )
    .where(Game.release_date.is_not(None))
    .group_by(season)
    .order_by(season)
)

games_by_price_range = (
    select(
        price_range,
        func.count(Game.app_id).label("games_count"),
        func.round(func.avg(Game.rating), 1).label("average_rating"),
    )
    .where(Game.price.is_not(None))
    .group_by(price_range)
    .order_by(func.min(Game.price))
)

games_by_rating_range = (
    select(
        rating_range,
        func.count(Game.app_id).label("games_count"),
        func.round(func.avg(Game.price), 2).label("average_price"),
    )
    .where(Game.rating.is_not(None))
    .group_by(rating_range)
    .order_by(func.min(Game.rating))
)


queries = {
    "Игры по платформам": sort_by_platforms,
    "Средняя цена по году": average_price_by_year,
    "Скидки по сезонам": average_discount_by_season,
    "Игры по диапазонам цены": games_by_price_range,
    "Игры по диапазонам рейтинга": games_by_rating_range,
}

with SessionLocal() as session:
    for title, statement in queries.items():
        rows = session.execute(statement).mappings().all()

        print(f"\n{title}")
        print(tabulate(rows, headers="keys", tablefmt="grid"))
