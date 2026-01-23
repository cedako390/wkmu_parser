import json

def generate_html_from_json(json_file, output_file):
    """
    Генерирует простой HTML файл из JSON данных с аккордеоном.
    Адаптирован для WordPress (минификация CSS).
    """
    import random
    import string
    
    # Генерируем случайный суффикс для классов
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # Читаем JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 1. Формируем CSS отдельно (можно писать с отступами для удобства чтения в коде)
    # Обратите внимание: здесь двойные фигурные скобки {{ }} не нужны, так как это пока не f-string,
    # но ниже мы будем использовать .format или просто сложение строк, чтобы избежать путаницы.
    # Для надежности используем f-string с удвоением скобок, но потом удалим переносы.
    
    css_raw = f'''
        .container-{suffix} {{
            max-width: 1200px !important;
            margin: 0 auto !important;
            font-family: Arial, sans-serif !important;
            line-height: 1.6 !important;
            color: #333 !important;
        }}
        .title-{suffix} {{
            font-size: 32px !important;
            margin-bottom: 30px !important;
            color: #333 !important;
            font-weight: bold !important;
        }}
        .section-details-{suffix} {{
            margin-bottom: 10px !important;
        }}
        .section-details-{suffix} > summary {{
            background-color: #e8e8e8 !important;
            color: #333 !important;
            cursor: pointer !important;
            padding: 18px 20px !important;
            border: none !important;
            text-align: left !important;
            outline: none !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            transition: background-color 0.3s !important;
            list-style: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }}
        .section-details-{suffix} > summary::-webkit-details-marker {{
            display: none !important;
        }}
        .section-details-{suffix} > summary:hover {{
            background-color: #d5d5d5 !important;
        }}
        .section-details-{suffix}[open] > summary {{
            background-color: #d0d0d0 !important;
        }}
        .section-details-{suffix} > summary::after {{
            content: '+' !important;
            font-size: 24px !important;
            font-weight: bold !important;
            transition: transform 0.3s !important;
        }}
        .section-details-{suffix}[open] > summary::after {{
            content: '−' !important;
        }}
        .section-content-{suffix} {{
            background-color: #fff !important;
            margin-bottom: 2px !important;
        }}
        .category-details-{suffix} {{
            border-bottom: 1px solid #fff !important;
        }}
        .category-details-{suffix} > summary {{
            background-color: #4a5568 !important;
            color: white !important;
            cursor: pointer !important;
            padding: 15px 20px !important;
            border: none !important;
            text-align: left !important;
            outline: none !important;
            font-size: 15px !important;
            font-weight: 500 !important;
            transition: background-color 0.3s !important;
            list-style: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
        }}
        .category-details-{suffix} > summary::-webkit-details-marker {{
            display: none !important;
        }}
        .category-details-{suffix} > summary:hover {{
            background-color: #5a6678 !important;
        }}
        .category-details-{suffix}[open] > summary {{
            background-color: #3a4558 !important;
        }}
        .category-details-{suffix} > summary::after {{
            content: '▼' !important;
            font-size: 12px !important;
            transition: transform 0.3s !important;
        }}
        .category-details-{suffix}[open] > summary::after {{
            transform: rotate(180deg) !important;
        }}
        .category-content-{suffix} {{
            background-color: #f9f9f9 !important;
            padding: 15px 20px !important;
        }}
        .category-content-{suffix} ul {{
            list-style-type: none !important;
            padding-left: 0 !important;
            margin: 0 !important;
        }}
        .category-content-{suffix} ul li {{
            padding: 10px 0 !important;
            border-bottom: 1px solid #e0e0e0 !important;
            margin: 0 !important;
        }}
        .category-content-{suffix} ul li:last-child {{
            border-bottom: none !important;
            padding-bottom: 0 !important;
        }}
        .category-content-{suffix} a {{
            color: #2563eb !important;
            text-decoration: none !important;
            transition: color 0.2s !important;
        }}
        .category-content-{suffix} a:hover {{
            color: #1d4ed8 !important;
            text-decoration: underline !important;
        }}
        .nested-details-{suffix} {{
            margin: 8px 0 !important;
        }}
        .nested-details-{suffix}:first-child {{
            margin-top: 0 !important;
        }}
        .nested-details-{suffix} > summary {{
            background-color: #f3f4f6 !important;
            color: #333 !important;
            cursor: pointer !important;
            padding: 12px 15px !important;
            font-size: 14px !important;
            border-left: 3px solid #4a5568 !important;
            list-style: none !important;
            transition: background-color 0.3s !important;
        }}
        .nested-details-{suffix} > summary::-webkit-details-marker {{
            display: none !important;
        }}
        .nested-details-{suffix} > summary:hover {{
            background-color: #e5e7eb !important;
        }}
        .nested-details-{suffix}[open] > summary {{
            background-color: #e5e7eb !important;
            border-left-color: #2563eb !important;
        }}
        .nested-content-{suffix} {{
            background-color: white !important;
            border-left: 3px solid #d1d5db !important;
            margin-left: 10px !important;
            padding: 15px 20px !important;
        }}
        .nested-content-{suffix} ul {{
            margin: 0 !important;
        }}
    '''
    
    # !!! ВАЖНО: Удаляем переносы строк и лишние пробелы для WordPress !!!
    # Мы заменяем переносы на пробел, а потом удаляем двойные пробелы, чтобы получить одну длинную строку.
    css_minified = css_raw.replace('\n', ' ').replace('  ', ' ')
    while '  ' in css_minified:
        css_minified = css_minified.replace('  ', ' ')

    # Начало HTML
    # Вставляем уже очищенный CSS
    html = f'<style>{css_minified}</style>'
    html += f'\n<div class="container-{suffix}">'
    # Генерируем контент
    for file_name, categories in data.items():
        html += f'\n<details class="section-details-{suffix}">'
        html += f'\n<summary>{file_name}</summary>'
        html += f'\n<div class="section-content-{suffix}">'
        
        for category in categories:
            html += f'\n<details class="category-details-{suffix}">'
            html += f'\n<summary>{category["title"]}</summary>'
            html += f'\n<div class="category-content-{suffix}">'
            
            if category['links']:
                html += '\n<ul>'
                
                for link in category['links']:
                    html += f'\n<li><a href="{link["url"]}" target="_blank">{link["text"]}</a></li>'
                html += '\n</ul>'
            
            if category['children']:
                for child in category['children']:
                    html += f'\n<details class="nested-details-{suffix}">'
                    html += f'\n<summary>{child["title"]}</summary>'
                    html += f'\n<div class="nested-content-{suffix}">'
                    
                    if child['links']:
                        html += '\n<ul>'
                        for link in child['links']:
                            html += f'\n<li><a href="{link["url"]}" target="_blank">{link["text"]}</a></li>'
                        html += '\n</ul>'
                    
                    html += '\n</div>'
                    html += '\n</details>'
            
            html += '\n</div>'
            html += '\n</details>'
        
        html += '\n</div>'
        html += '\n</details>'
    
    html += '\n</div>'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML файл создан: {output_file}")

if __name__ == "__main__":
    import sys
    # Создаем фиктивный файл данных для теста, если его нет (для запуска примера)
    # В реальном использовании это можно удалить
    try:
        with open('all_data.json', 'r') as f: pass
    except FileNotFoundError:
        print("Файл all_data.json не найден, создаю тестовый...")
        dummy_data = {
            "Раздел 1": [{"title": "Категория 1", "links": [{"url":"#","text":"Тест"}], "children": []}]
        }
        with open('all_data.json', 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f)
    print("zzz")
    generate_html_from_json("all_data.json", "output.html")