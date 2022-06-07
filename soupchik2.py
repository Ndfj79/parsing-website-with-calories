#библиотека для запросов с сайта от парсера    & C:/Users/компьютер/AppData/Local/Programs/Python/Python310/python.exe c:/Users/компьютер/Desktop/mama/.vscode/bot2.py
import requests
#импорт парсера
from bs4 import BeautifulSoup
#импорт библиотеки для работы с json файлами
import json
#импорт библиотеки для работы с csv файлами
import csv
# импорт задержки и рандома
import time, random
def dietparse():
    #константа со ссылкой на страницу
    url = "https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"
    #Словарь с Accept и User-Agent взятые из кода элемента сайта для того что бы показать сайту что мы не бот(вроде как)

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.72 (Edition Yx GX)"
    }

    #запрашиваем HTML-код сайта и сохраняем его как текст в переменную src
    req = requests.get(url, headers=headers)
    src = req.text

    #проверка получения программного кода
    #print(src)
    # создаем файл в который вписываем полностью программный код сайта(мы используем его в файле чтобы не перегружать сайт запросами)
    # with open("indexa.html", "w",encoding="utf-8") as file:
    #     file.write(src)
    #считываем файл в переменную src
    with open("indexa.html" ,"r", encoding="utf-8") as file:
        src = file.read()

    #создаём обьект супа
    soup = BeautifulSoup(src, "html.parser")

    #создаем словарь со всеми категориями
    all_categories_diet = {}

    #собираем список всех катгорий продуктов
    all_products_category_hrefs = soup.find_all(class_="mzr-tc-group-item-href")

    #цикл в котором мы выбираем из категорий продуктов их имена и ссылки на них
    for items in all_products_category_hrefs:
        #получение названий
        item_text = items.text
        #получение ссылок
        item_href =  "https://health-diet.ru"+items.get("href")
        #проверка через запись в консоль
        #print(f"{item_text}:{item_href}")
        #Записание всего этого в словарь
        all_categories_diet[item_text] = item_href

    #создание json файла с параметрами для красивой записи и записание в него словаря с категориями
    # with open("all_categories_diet.json", "w",encoding="utf-8") as file:
    #     json.dump(all_categories_diet, file, indent=4, ensure_ascii=False)

    #Чтение этого же файла и сохранение его в переменную
    with open("all_categories_diet.json",encoding="utf-8") as file:
        all_categories = json.load(file)

    #переменная для счетчика оставшихся файлов загрузки
    iteration_count = int(len(all_categories)-1)

    #вывод в консоль сколько всего итераций осталось
    print(f"Всего итераций: {iteration_count}")

    # счетчик цикла
    count = 0

    #цикл  основной работы парсинга
    for category_name, category_href in all_categories.items():
        rep = [","," ","-","'"] #символы для замены (чтобы красива)
        # сама замена символов
        for item in rep:
            if item in category_name: #если символ имеется в словах то
                category_name = category_name.replace(item,"_") # метод замены файлов
        #запрос в хим. описание каждого элемент
        req = requests.get(url=category_href, headers=headers)
        #сохранение в переменную src  текста страницы
        src = req.text

        #создание файлов с HTML кодами для каждой категории
        with open(f"data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
            file.write(src)

        #считывание их в переменную src
        with open(f"data/{count}_{category_name}.html", "r", encoding="utf-8") as file:
            src = file.read()
    #создание обьекта супа
        soup = BeautifulSoup(src, "html.parser")

        #проверка на наличие на странице таблицы с продукатми
        alert_block = soup.find(class_="uk-alert-danger")
        if alert_block is not None:
            continue

        #собираем зоголовки таблицы
        table_head = soup.find(class_="mzr-tc-group-table").find_all("th")
        product = table_head[0].text
        calories = table_head[1].text
        proteins = table_head[2].text
        fats = table_head[3].text
        carbohydrates = table_head[4].text

        #создание csv файла(таблица), сохранение в переменную writer и  запись в него заголовков таблиц
        with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            #запись в строку
            writer.writerow(
                (
                    product,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )

        #собираем данные продуктов в список
        products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

        #список в котором будет информация о продуктах
        product_info = []
        #цикл - перебирает все колонки таблицы и сохраняет информацию из строк колонок
        for items in products_data:
            product_tds = items.find_all("td") #сохранение всех строк в список

            title = product_tds[0].find("a").text #извлечение из списка названия продукта
            calories = product_tds[1].text  #извлечение из списка калорий продукта
            proteins = product_tds[2].text #извлечение из списка белков продукта
            fats = product_tds[3].text #извлечение из списка жиров продукта
            carbohydrates = product_tds[4].text #извлечение из списка углеводов продукта

            # добавление в список всей этой информации
            product_info.append(
                {
                    "Title": title,
                    "Calories": calories,
                    "Proteins": proteins,
                    "Fats": fats,
                    "Carbohydrates": carbohydrates
                }
            )

            # добавление к файлам, в которые уже записаны заголовки, информации о хим. составе продуктов
            with open(f"data/{count}_{category_name}.csv", "a", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(
                    (
                        title,
                        calories,
                        proteins,
                        fats,
                        carbohydrates
                    )
                )

        # создание файлов json в которые красиво добавляем тоже самое что и в таблицы
        with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
            json.dump(product_info,file, indent=4, ensure_ascii=False )

        # увеличение переменной-счетчика
        count+=1
        # информация для пользователя
        print(f"# Итерация {count}. {category_name} записан...")
        iteration_count-=1
        # остановка главного цикла при истечении  обратного счетчика цикла
        if iteration_count == 0:
            print("Работа завершена")
            break
        # информация для пользователя (не обязательно)
        print(f"Осталось итераций {iteration_count}")
        time.sleep(random.randrange(2,4))

