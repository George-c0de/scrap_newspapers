import newspaper
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import re
from docx import Document


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
                if len(k) > 2:
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


def scrape_all(article):
    c_2 = [article.title]
    for l_ in article.authors:
        c_2.append(l_)
    c_2.append(str(article.publish_date))
    c_2.append(article.text)
    c_2.append(article.url)
    return c_2


def links(url, d_):
    links_all = []
    c = []
    d = {'links_all': links_all, 'text': c}
    cnn_paper = newspaper.build(url, memoize_articles=False, language=d_['language'])
    for article in cnn_paper.articles:
        if serch_(article.url, d_["url"]) or d_["flag"]:
            article.download()
            article.parse()
            d['text'] = d['text'] + scrape_all(article)
            d['links_all'] = article.url
    return d


def go(url, col):
    dict_o = {'links_all': [], 'text': []}
    dict_ = mask(url)
    while col != -1:
        if len(dict_o['text']) == 0:
            dict_o = links(url, dict_)
            dict_o['text'] = dict_o['text']
        else:
            for el in dict_o['text']:
                dict_o = links(el, dict_)
                dict_o['text'] = dict_o['text']
        col = col - 1
    return dict_o


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
    if isinstance(text_, str):
        with open("save2.txt", "w", encoding="utf-8") as file:
            file.write(text_)
    else:
        with open("save2.txt", "w", encoding="utf-8") as file:
            for el in text_:
                if el is not None:
                    file.write(el)
    print("Обработанный файл сохранен")


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
            save_txt(a['text'])
            return a
        case 2:
            print("Enter url \n>")
            url_ = input()
            a = extract_text_from_pdf(url_)
            save_txt(a['text'])
            return a
        case 3:
            print("Enter url \n>")
            url_ = input()
            a = doc(url_)
            save_txt(a['text'])
            return a


if __name__ == "__main__":
    main()
