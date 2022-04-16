import newspaper
import io
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import re
from docx import Document


def doc(path):
    document = Document(path)
    # Регулярка для поиска последовательностей пробелов: от двух подряд и более
    multi_space_pattern = re.compile(r'\s{2,}')
    for table in document.tables:
        for row in table.rows:
            name, weight, price = [multi_space_pattern.sub(' ', i.text.strip()) for i in row.cells]

            if name == weight == price or (not weight or not price):
                print()
                name = name.title()
                print(name)
                continue

            print('{} {} {}'.format(name, weight, price))

        # Таблицы в меню дублируются
        break


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


def serch_(str_, start):
    if str_.startswith(start):
        return True
    else:
        return False


def lang(st):
    n = 0
    k = ""
    default = "ru"
    for el in st:
        if el == "/":
            n = n + 1
            continue
        if n >= 3:
            if n == 4:
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


def links(url, d_):
    c = []
    print(d_)
    cnn_paper = newspaper.build(url, memoize_articles=False, language=d_['language'])
    for article in cnn_paper.articles:
        if serch_(article.url, d_["url"]) or d_["flag"]:
            c.append(article.url)
    return c


def go(url, col):
    b = []
    dict_ = mask(url)
    while col != -1:
        print(len(b))
        if len(b) == 0:
            b = b + links(url, dict_)
        else:
            for el in b:
                b = b + links(el, dict_)
        col = col - 1
    return b


print("1. Scrap web\n2.Scrap file\n3.Scrap doc\nEnter:\n>\n")
ch = int(input())
match ch:
    case 1:
        print("Enter url \n>")
        url_ = input()
        print("and number scrape\n>")
        n = int(input())
        a = go(url_, n)
    case 2:
        print("Enter url \n>")
        url_ = input()
        print(extract_text_from_pdf(url_))
    case 3:
        print("Enter url \n>")
        url_ = input()
        print(doc(url_))


