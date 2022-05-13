# Парсер статей и документов
___

# Функции
___
1. Обработка docx файлов def doc(path)
  + Данная функция обрабатывает структурированные файлы, 
принимает ссылку на файл 
```pycon
  def doc(path):
         doc_text = ""
         document = Document(path)
         multi_space_pattern = re.compile(r'\s{2,}')
         for table in document.tables:
             for row in table.rows:
                 name, weight, price = [multi_space_pattern.sub(' ', i.text.strip()) for i in row.cells]
                 if name == weight == price or (not weight or not price):
                     doc_text = doc_text + "\n"
                     name = name.title()
                     doc_text = doc_text + name
                     continue
    
                 doc_text = doc_text + '{} {} {}'.format(name, weight, price)
             break
         return doc_text
```
2. Обработка файлов pdf
+ Данная функция обрабатывает файлы типа pdf, 
  - Принимает ссылку на файл 
  - Возвращает строку 
```pycon
   def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text
   ```
3. def serch_(str_, start)
+ Данная функция производит проверку маски.
  Если строка удовлетворяет условию, выводит True, иначе False
+ Принимает 2 параметра 
  + str_ - адрес веб страницы
  + start - маска
```pycon
def serch_(str_, start):
    if str_.startswith(start):
        return True
    else:
        return False
```
4. def lang(st)
+ Данная функция определяет язык поиска статей. 
  + Если пользователь не вводил язык для поиска, 
  то берется значение по умолчанию - ru
```pycon
def lang(st):
    flag = 0
    k = ""
    default = "ru"
    for el in st:
        if el == "/":
            flag = flag + 1
            continue
        if flag >= 3:
            if flag == 4:
                if len(k) > 2:
                    return default
                else:
                    return k
            k = k + el
```
5. def mask(url)
+ Данная функция создает словарь маски с нужными нам значениями, 
язык поиска, маска или ее отсутствие 
  + flag указываеть была ли задана маска
```pycon
def mask(url):
    lan = lang(url)
    flag = True
    if url.find("*") != -1:
        num = url.find("*")
        url = url[0:num]
        flag = False
    sp = {"language": lan, "url": url, "flag": flag}
    return sp
```
6. def links(url, d_, fl)
+ Функция проводит парсинг ссылок в статье, 
с использованием маски 
```pycon
def links(url, d_, fl):
    links_all = []
    c = []
    d = {'links_all': links_all, 'text': c}
    article = newspaper.Article(url)
    try:
        article.download()
        article.parse()
    except newspaper.article.ArticleException:
        return d
    d['text'] = d['text'] + scrape_all(article)
    cnn_paper = newspaper.build(url, memoize_articles=False, language=d_['language'])
    if fl:
        for article in cnn_paper.articles:
            d['links_all'].append(article.url)
    return d
```
7. def go(url, col)
+ Функция отвечает за глубину поиска
```pycon
def go(url, col):
    col_f = col
    flag = False
    dict_ = mask(url)
    while col != -1:
        if col_f == col:
            if (col - 1) != -1:
                flag = True
            dict_o = links(url, dict_, flag)
        else:
            if (col - 1) != -1:
                flag = True
            for el in dict_o['links_all']:
                new_d = links(el, dict_, flag)
                dict_o['text'] = dict_o['text'] + new_d['text']
                dict_o['links_all'] = dict_o['links_all'] + new_d['links_all']
        col = col - 1
    return dict_o
```
8. def save_article(a, name)
+ Функция сохраняет 2 файла, обработанный и необработанный файл.
  ```pycon
  def save_article(a, name):
    with open("статьи/" + name + ".txt", "w", encoding="utf-8") as file:
        file.write(a)
    with open("статьи/clear/" + name + "_clear.txt", "w", encoding="utf-8") as file:
        for el in a:
            a = a + el
            a = a.replace(' ', '')
            a = a.replace('\n', '')
            a = a.replace('▍', '')
            a = a.lower()
            a = a.replace('none', '')
        file.write(a)
        a = "".join(a)
    dbname_ = "scrap"
    user_ = "postgres"
    password_ = "123"
    host_ = "127.0.0.1"
    port_ = "5432"
    conn = connect_pg(dbname_, user_, password_, host_, port_)
    insert(conn, a)
  ```
9. def main()
+ Главная функция, 
которая отвечает за визуальное представление программы
```pycon
def main():
    print("1. Scrap web\n2.Scrap file\n3.Scrap doc\nEnter:\n>\n")
    ch = int(input())
    match ch:
        case 1:
            print("Enter url \n>")
            url_ = input()
            print("and number scrape\n>")
            n = int(input())
            a = go(url_, n)
            return a
        case 2:
            print("Enter url \n>")
            url_ = input()
            a = extract_text_from_pdf(url_)
            return a
        case 3:
            print("Enter url \n>")
            url_ = input()
            a = doc(url_)
            return a
```
10. def name_go(name):
+ Функция очистки из названия статьи всех спецсимволов
```pycon
def name_go(name):
    name = name.replace(' ', '')
    name = name.replace('/', '')
    name = name.replace('\\', '')
    name = name.replace(':', '')
    name = name.replace('*', '')
    name = name.replace('?', '')
    name = name.replace('"', '')
    name = name.replace('<', '')
    name = name.replace('>', '')
    name = name.replace('|', '')
    return name
```
11. def connect_pg(dbname_, user_, password_, host_, port_)
+ Создание подключение к нашей БД  
```pycon
def connect_pg(dbname_, user_, password_, host_, port_):
    conn = psycopg2.connect(dbname=dbname_, user=user_,
                            password=password_, host=host_, port=port_)
    return conn
```
12. def insert(conn, a)
+ Добавление в нашу базу данных
```pycon
    try:
        cursor = conn.cursor()
        postgres_insert_query = """INSERT INTO "Articles" (text_art) VALUES (%s);"""
        a = a[:254]
        record_to_insert = a
        cursor.execute(postgres_insert_query, (record_to_insert,))
        conn.commit()
    except(Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if conn:
            cursor.close()
            conn.close()
```
# Работа с БД PostgreSql
___
+ Создадим Бд scrap
+ Добавим таблицу Articles
+ Столбец Id
+ Столбец text_art типа text
+ Добавим расширение в нашу БД 
  + ```
    CREATE EXTENSION fuzzystrmatch;
    ```
+ Добавим триггер, который будет проверять повторение статьи с помощью функции levenshtein
  + ```
    CREATE FUNCTION emp_stamp() RETURNS trigger AS $emp_stamp$
    BEGIN
        IF (SELECT EXISTS(SELECT text_art FROM "Articles" WHERE levenshtein(text_art, NEW.text_art) <= 100)) THEN
            RAISE EXCEPTION 'Такая статья уже существует';
        END IF;
   
        RETURN NEW;
    END;
    $emp_stamp$ LANGUAGE plpgsql;

    CREATE TRIGGER emp_stamp BEFORE INSERT OR UPDATE ON "Articles"
    FOR EACH ROW EXECUTE PROCEDURE emp_stamp();
    ```
# Структура хранения статей
___
+ Создадим папку статьи, где будут храниться наши статьи 
+ В ней создадим папку clear, где будут храниться наши очищенные статьи 