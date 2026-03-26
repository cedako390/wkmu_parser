"""
check_links.py – проверяет все ссылки в all_data.json на доступность.

Запуск:
    python check_links.py [all_data.json]

Опциональные аргументы окружения:
    WORKERS   – количество параллельных потоков (по умолчанию 10)
    TIMEOUT   – таймаут одного запроса в секундах (по умолчанию 10)

После проверки создаётся файл-отчёт broken_links_report.log с записями вида:
    Строка 42, ссылка https://example.com — HTTP 404
"""

from __future__ import annotations

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

# ---------------------------------------------------------------------------
# Настройки
# ---------------------------------------------------------------------------
JSON_FILE   = sys.argv[1] if len(sys.argv) > 1 else "all_data.json"
WORKERS     = int(os.environ.get("WORKERS", 10))
TIMEOUT     = int(os.environ.get("TIMEOUT", 10))
REPORT_FILE = os.environ.get("REPORT_FILE", "broken_links_report.log")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; link-checker/1.0; "
        "+https://github.com/cedako390/wkmu_parser)"
    )
}

# ---------------------------------------------------------------------------
# Сбор ссылок
# ---------------------------------------------------------------------------

def collect_urls_from_item(item: dict) -> list[str]:
    """Рекурсивно собирает URL из одного элемента категории."""
    urls = []
    for link in item.get("links", []):
        url = link.get("url", "").strip()
        if url:
            urls.append(url)
    for child in item.get("children", []):
        urls.extend(collect_urls_from_item(child))
    return urls


def collect_urls(data: dict) -> list[str]:
    """Собирает все URL из структуры all_data.json."""
    urls = []
    for section_items in data.values():
        for item in section_items:
            urls.extend(collect_urls_from_item(item))
    return urls


def collect_urls_regex(text: str) -> list[str]:
    """Запасной метод: ищет все http/https-ссылки в сыром тексте."""
    return re.findall(r'https?://[^\s\'"<>]+', text)


def find_url_line_numbers(raw_text: str) -> dict[str, int]:
    """Возвращает словарь {url: номер_строки} для первого вхождения каждой ссылки."""
    url_lines: dict[str, int] = {}
    for lineno, line in enumerate(raw_text.splitlines(), start=1):
        for url in re.findall(r'https?://[^\s\'"<>]+', line):
            if url not in url_lines:
                url_lines[url] = lineno
    return url_lines


# ---------------------------------------------------------------------------
# Проверка одной ссылки
# ---------------------------------------------------------------------------

def check_url(url: str) -> tuple[str, str | None]:
    """
    Возвращает (url, error_description).
    error_description is None, если ссылка доступна.
    """
    try:
        # Сначала пробуем HEAD (быстрее), потом GET если не поддерживается
        resp = requests.head(url, headers=HEADERS, timeout=TIMEOUT,
                             allow_redirects=True)
        if resp.status_code == 405:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                                allow_redirects=True, stream=True)

        if resp.status_code >= 400:
            return url, f"HTTP {resp.status_code}"
        return url, None

    except requests.exceptions.SSLError as exc:
        return url, f"SSL ошибка: {str(exc)[:120]}"
    except requests.exceptions.ConnectionError as exc:
        return url, f"Ошибка соединения: {str(exc)[:120]}"
    except requests.exceptions.Timeout:
        return url, f"Таймаут ({TIMEOUT}s)"
    except requests.exceptions.TooManyRedirects:
        return url, "Слишком много редиректов"
    except requests.exceptions.RequestException as exc:
        return url, f"Ошибка запроса: {str(exc)[:120]}"


# ---------------------------------------------------------------------------
# Основная логика
# ---------------------------------------------------------------------------

def main() -> None:
    # Читаем файл
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as fh:
            raw_text = fh.read()
            data = json.loads(raw_text)
    except FileNotFoundError:
        print(f"[ОШИБКА] Файл не найден: {JSON_FILE}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"[ОШИБКА] Не удалось разобрать JSON: {exc}", file=sys.stderr)
        sys.exit(1)

    # Собираем ссылки через структуру JSON
    urls = collect_urls(data)

    # Дополняем regex-поиском на случай нестандартных полей
    regex_urls = set(collect_urls_regex(raw_text))
    structured_urls = set(urls)
    extra = regex_urls - structured_urls
    if extra:
        urls.extend(sorted(extra))

    # Убираем дубликаты, сохраняя порядок
    seen: set[str] = set()
    unique_urls: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique_urls.append(u)

    # Карта URL -> номер строки в файле
    url_line_map = find_url_line_numbers(raw_text)

    total = len(unique_urls)
    print(f"Всего уникальных ссылок: {total}")

    broken: list[tuple[str, str]] = []
    ok_count = 0

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(check_url, url): url for url in unique_urls}
        for future in as_completed(futures):
            url, error = future.result()
            if error:
                broken.append((url, error))
            else:
                ok_count += 1

    # Итог в консоль
    print(f"Проверено: {total}  |  ОК: {ok_count}  |  Проблемных: {len(broken)}")

    # Отчёт в файл
    with open(REPORT_FILE, "w", encoding="utf-8") as report:
        report.write(f"Отчёт проверки ссылок: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.write(f"Файл: {JSON_FILE}\n")
        report.write(f"Проверено: {total}  |  ОК: {ok_count}  |  Проблемных: {len(broken)}\n")
        report.write("-" * 60 + "\n")
        if broken:
            for url, error in broken:
                lineno = url_line_map.get(url)
                line_label = f"Строка {lineno}" if lineno is not None else "Строка неизвестна"
                report.write(f"{line_label}, ссылка {url} — {error}\n")
        else:
            report.write("Все ссылки доступны.\n")

    print(f"Отчёт сохранён: {REPORT_FILE}")


if __name__ == "__main__":
    main()
