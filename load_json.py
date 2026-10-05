import json
import pandas as pd
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db import engine, init_db, Game


def load_steam_json(path):
    init_db()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.DataFrame(data).rename(columns={
        "discount_percent": "discount",
        "positive_rate": "rating",
    })

    df["platforms"] = df["platforms"].apply(
        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, list) else x
    )
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0).astype(int)
    
    df["app_id"] = pd.to_numeric(df["app_id"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["app_id"])
    df["app_id"] = df["app_id"].astype(int)
    df = df.drop_duplicates(subset="app_id", keep="last")

    
    with engine.begin() as conn:
        query = sqlite_insert(Game.__table__).values(df.to_dict(orient="records"))
        update_cols = {c: query.excluded[c] for c in df.columns if c != "app_id"}
        query = query.on_conflict_do_update(index_elements=["app_id"], set_=update_cols)
        conn.execute(query)

    return len(df)


if __name__ == "__main__":
    n = load_steam_json("raw_games.json")
    print(f"Загружено: {n}")