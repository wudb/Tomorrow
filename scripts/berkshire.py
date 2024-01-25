import os
import sys
import requests
from bs4 import BeautifulSoup
import pdfkit
from pypdf import PdfMerger, PdfReader, PdfWriter
import xml2epub

# 文件夹名称
desDirName = "巴菲特致股东及合伙人的信（中文版）"

def start(startYear=1957, endYear=2022, toPdf=False, toEpub=False):
    '''开始下载'''
    if not os.path.exists(desDirName):
        os.mkdir(desDirName)
    
    epub_name = '{}至{}年{}'.format(startYear, endYear, desDirName)
    epub = xml2epub.Epub(epub_name, creator="沃伦·巴菲特", language="cn", publisher="伯克希尔哈撒韦")
    # 封面
    # cover = xml2epub.create_chapter_from_string("https://0.rc.xiniu.com/g3/M00/2B/98/CgAH6F5SMCqAS1WmAADdkLeIwkg01.jpeg", title='Cover', strict=False)
    # epub.add_chapter(cover)
    
    for year in range(startYear, endYear+1):
        print('---开始下载{}年---'.format(year))
        if (year > 2018):
            url = 'http://www.xindaoyi.com/buffett-{}/'.format(year)
        else:
            url = 'http://www.xindaoyi.com/{}-buffett/'.format(year)
        title, content = download_page(url)
        if toPdf:
            convert_pdf(content, title)

        if toEpub:
            chapter = xml2epub.create_chapter_from_string(content, title=title, strict=False)
            epub.add_chapter(chapter)
            
    epub.create_epub(desDirName)

def removeTags(tag):
    return True
    # return not (tag.has_attr('id') and tag['id'] == 'wp_rp_first') or tag['class'] != 'tags'

def download_page(url):
    '''根据链接下载指定年份的股东信'''
    print(url)
    page = requests.get(url)
    # print(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    # 获取所有文本内容
    title_node = soup.find('h1', class_="single-title")
    # print(str(title_node))
    content_nodes = soup.find('div', id='content').find_all(removeTags, recursive=False)
    
    nodes = []
    for node in content_nodes:
        if node.has_attr('id') and node['id'] == 'wp_rp_first':
            break
        nodes.append(node)
    content = '\n'.join([str(x) for x in nodes])
    # print(content_nodes)
    
    # 完整文章
    title = str(title_node)
    page_content = '{}\n{}'.format(title, content)
    return title, page_content
    

def convert_pdf(content, title):
    # 转换成 pdf
    file_name = '{}.pdf'.format(title)
    # dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), desDirName)
    file = os.path.join(desDirName, file_name)
    # config = pdfkit.configuration(wkhtmltopdf=bytes('/Users/djios/opt/anaconda3/lib/python3.10/site-packages/wkhtmltopdf', 'utf-8'))
    # pdfkit.from_string(page_content, file, False, configuration=config)
    pdfkit.from_string(content, file, options={'encoding': 'UTF-8', 'minimum-font-size': "24"})
    
    
def get_file_name(year):
    if year < 1970:
        return '{}年巴菲特致合伙人的信（中文版）'.format(year)
    elif year == 1970:
        return '1970巴菲特致合伙人的信（中文版）'
    else:
        return '{}年巴菲特致股东的信（中文版）'.format(year)

def merge_pdf(startYear=1957, endYear=2022):
    '''合并pdf'''
    writer = PdfWriter()
    page_num = 0 # 记录每次合并一个pdf 文件后总页数
    pdf_name = '{}/{}-{}年{}.pdf'.format(desDirName, startYear, endYear, desDirName)
    
    with open(pdf_name, 'wb') as pdf_file:
        for year in range(startYear, endYear+1):
            page_name = get_file_name(year)
            file_name = '{}/{}.pdf'.format(desDirName, page_name)
            page = PdfReader(file_name)
            writer.append_pages_from_reader(page)
            writer.add_outline_item(page_name, page_num)
            page_num += len(page.pages)
        
        writer.write(pdf_file)
        writer.close()
    pdf_file.close()

if __name__ == '__main__':
    sys.setrecursionlimit(10000)
    start(toPdf=True, toEpub=True)
    merge_pdf()