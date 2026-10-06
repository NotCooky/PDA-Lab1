import json
from db import get_session, init_db, Game


def _normalize_record(raw):
    app_id = raw.get("app_id")
    title = raw.get("title")
    if app_id is None or not title:
        return None
    platforms = raw.get("platforms")
    if isinstance(platforms, list):
        platforms = json.dumps(platforms, ensure_ascii=False) 
    return {
        "app_id": int(app_id),
        "title": str(title),
        "release_date": raw.get("release_date"),
        "price": raw.get("price"),
        "discount": raw.get("discount") or 0,
        "rating": raw.get("rating"),
        "platforms": platforms,

    }

def load_steam_json(path):
    init_db()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    games_by_id = {}
    for raw in data:
        rec = _normalize_record(raw)
        if rec is not None:
            games_by_id[rec["app_id"]] = rec

    with get_session() as session:
        for rec in games_by_id.values():
            session.merge(Game(**rec))

    return(len(games_by_id))






if __name__ == "__main__":
    n = load_steam_json("raw_games.json")
    print(f"Загружено: {n}")