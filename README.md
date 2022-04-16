# Парсер статей и документов
___

# Функции
___
1. Обработка docx файлов def doc(path)
  + Данная функция обрабатывает структурированные файлы, 
принимает ссылку на файл 
```
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
```
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
```
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
```
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
```
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
6. def links(url, d_)
+ Функция проводит парсинг ссылок в статье, 
с использованием маски 
```
def links(url, d_):
    c = []
    cnn_paper = newspaper.build(url, memoize_articles=False, language=d_['language'])
    for article in cnn_paper.articles:
        if serch_(article.url, d_["url"]) or d_["flag"]:
            c.append(article.url)
    return c
```
7. def go(url, col)
+ Функция отвечает за глубину поиска
```
def go(url, col):
    b = []
    dict_ = mask(url)
    while col != -1:
        if len(b) == 0:
            b = b + links(url, dict_)
        else:
            for el in b:
                b = b + links(el, dict_)
        col = col - 1
    return b
```
8. def save_txt(text_)
+ Функция сохраняет 2 файла, обработанный и необработанный файл.
  + Принимает один параметр в случае с парсингом файла - строку, 
  + в случае с парсингом веб страницы - список
  ```
  def save_txt(text_):
    if isinstance(text_, str):
        with open("save.txt", "w", encoding="utf-8") as file:
            file.write(text_)
    else:
        with open("save.txt", "w", encoding="utf-8") as file:
            for el in text_:
                file.write(el + "\n")
    print("Необработанный файл сохранен")
    if isinstance(text_, str):
        with open("save2.txt", "w", encoding="utf-8") as file:
            file.write(text_)
    else:
        with open("save2.txt", "w", encoding="utf-8") as file:
            for el in text_:
                file.write(el)
    print("Обработанный файл сохранен")
  ```
9. def main()
+ Главная функция, 
которая отвечает за визуальное представление программы
```
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
            save_txt(a)
            return a
        case 2:
            print("Enter url \n>")
            url_ = input()
            a = extract_text_from_pdf(url_)
            save_txt(a)
            return a
        case 3:
            print("Enter url \n>")
            url_ = input()
            a = doc(url_)
            save_txt(a)
            return a
```