import io
import os

import newspaper
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import re
from docx import Document
import psycopg2
from psycopg2 import Error


def connect_pg(dbname_, user_, password_, host_, port_):
    conn = psycopg2.connect(dbname=dbname_, user=user_,
                            password=password_, host=host_, port=port_)
    return conn


def insert(conn, a):
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
    full_name = os.path.basename(doc_text)
    name = os.path.splitext(full_name)[0]
    save_article(doc_text, name)
    return doc_text


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
    converter.close()
    fake_file_handle.close()

    if text:
        full_name = os.path.basename(pdf_path)
        name = os.path.splitext(full_name)[0]
        save_article(text, name)
        return text



def serch_(str_, start):
    if str_.startswith(start):
        return True
    else:
        return False


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
                if len(k) != 2:
                    return default
                else:
                    return k
            k = k + el


def mask(url):
    lan = lang(url)
    flag = True
    if url.find("*") != -1:
        num = url.find("*")
        url = url[0:num]
        flag = False
    sp = {"language": lan, "url": url, "flag": flag}
    return sp


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


def scrape_all(article):
    c_2 = []
    c_2.append(article.title)
    for l_ in article.authors:
        c_2.append(l_)
    c_2.append(str(article.publish_date))
    c_2.append(article.text)
    text = article.text
    text = text.replace('▍', '')
    text = text.replace('none', '')
    text = text.replace('None', '')
    a = str(article.publish_date) + text
    name = article.title
    name = name_go(name)
    save_article(a, name)
    return c_2


def links(url, d_, fl):
    links_all = []
    c = []
    d = {'links_all': links_all, 'text': c}
    article = newspaper.Article(url, language='ru')
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


'''
def save_txt(text_):
    if isinstance(text_, str):
        with open("save.txt", "w", encoding="utf-8") as file:
            file.write(text_)
    else:
        with open("save.txt", "w", encoding="utf-8") as file:
            for el in text_:
                if el is not None:
                    file.write(el + "\n")
    print("Необработанный файл сохранен")
    a = ""
    for el in text_:
        a = a + el
        a = a.replace(' ', '')
        a = a.replace('\n', '')
        a = a.replace('▍', '')
        a = a.lower()
        a = a.replace('none', '')
    if isinstance(text_, str):
        with open("save2.txt", "w", encoding="utf-8") as file:
            b = text_.replace(' ', '')
            b = b.lower()
            file.write(b)
    else:
        with open("save2.txt", "w", encoding="utf-8") as file:
            file.write(a)
    print("Обработанный файл сохранен")
'''


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


if __name__ == "__main__":
    main()
    print("Все прошло успешно")
