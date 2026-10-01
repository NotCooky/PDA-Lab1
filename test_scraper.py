import json
import re
import time
import requests
from bs4 import BeautifulSoup


def clean_price(price_raw: str | None) -> float:
    """Очищает строку цены и переводит её во float."""
    if not price_raw:
        return 0.0

    text = price_raw.lower()
    if "бесплатно" in text or "free" in text or "демо" in text or "demo" in text:
        return 0.0

    # оставляем только цифры запятую и точку
    cleaned = re.sub(r"[^\d,\.]", "", price_raw)
    cleaned = cleaned.replace(",", ".")

    return float(cleaned)


def clean_discount(discount_raw: str | None) -> int:
    """Извлекает размер скидки в виде целого числа процентов."""
    if not discount_raw:
        return 0

    cleaned = re.sub(r"[^\d]", "", discount_raw)
    return int(cleaned) if cleaned.isdigit() else 0


def clean_rating(tooltip_html: str | None) -> int | None:
    """Извлекает процент положительных отзывов из тултипа."""
    if not tooltip_html:
        return None

    # ищем шаблон по типу 85%
    match = re.search(r"(\d+)%", tooltip_html)
    return int(match.group(1)) if match else None


def scrape_steam_catalog(
    total_games: int = 300, delay_seconds: float = 1.0
) -> list[dict]:
    """Собирает игры из каталога Steam с постраничной пагинацией."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

    games = []
    seen_ids = set()
    step = 50

    for start in range(0, total_games, step):
        url = f"https://store.steampowered.com/search/results/?query&start={start}&count={step}&category1=998"
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find_all("a", class_="search_result_row")

        if not rows:
            print("\nКарточки игр закончились.")
            break

        for row in rows:
            app_id_raw = row.get("data-ds-appid")
            if not app_id_raw:
                continue

            app_id = int(app_id_raw.split(",")[0])

            # исключаем дубликаты
            if app_id in seen_ids:
                continue
            seen_ids.add(app_id)

            title_el = row.find("span", class_="title")
            title = title_el.text.strip() if title_el else "Unknown"

            date_el = row.find("div", class_="search_released")
            release_date = date_el.text.strip() if date_el else None

            disc_el = row.find("div", class_="discount_pct")
            discount = clean_discount(disc_el.text.strip()) if disc_el else 0

            price_el = row.find("div", class_="discount_final_price")
            price = clean_price(price_el.text.strip()) if price_el else 0.0

            review_el = row.find("span", class_="search_review_summary")
            positive_rate = None
            if review_el and "data-tooltip-html" in review_el.attrs:
                positive_rate = clean_rating(review_el["data-tooltip-html"])

            # Извлечение поддерживаемых платформ
            platforms = []
            if row.find("span", class_="win"):
                platforms.append("Windows")
            if row.find("span", class_="mac"):
                platforms.append("macOS")
            if row.find("span", class_="linux"):
                platforms.append("Linux")

                # если иконки не найдены (например веб версия) то ставим по умолчанию винду
            if not platforms:
                platforms.append("Windows")

            games.append(
                {
                    "app_id": app_id,
                    "title": title,
                    "release_date": release_date,
                    "price": price,
                    "discount_percent": discount,
                    "positive_rate": positive_rate,
                    "platforms": ", ".join(platforms),
                }
            )

        time.sleep(delay_seconds)

    return games


if __name__ == "__main__":
    # Собираем 200 записей (достаточно для репрезентативности лабы)
    data = scrape_steam_catalog(total_games=200, delay_seconds=1.0)

    with open("raw_games.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nСохранено {len(data)} записей в .json файл")
