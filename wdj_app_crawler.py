import json
import os
import re

import pandas as pd
from bs4 import BeautifulSoup

import store
from img_tool import ImageOperation
from request import Request
from store import AppInfoTable
from store import CategoryTable

# 应用商店名称简写
WDJ_STORE_NAME = 'WDJ'
# 应用商店基本URL
WDJ_BASE_URL = 'https://www.wandoujia.com'


# 存储应用分类信息
def save_category_info(category_list):
    sql = """INSERT OR IGNORE INTO 'category' ('CategoryName', 'ParentCategoryName', 'Store', 'Url') VALUES (?,?,?,?)"""
    create_result = db_helper.create_tabel(CategoryTable.gen_create_table_sql(CategoryTable.TABLE_NAME))
    print(create_result)
    db_helper.insert_table_many(sql=sql, value=category_list)


# 存储应用信息
def save_app_info(app_list):
    sql = """INSERT OR IGNORE INTO 'app' ('AppName','PackageName',
                               'Category',
                               'Tag',
                               'Store',
                               'IconUrl',
                               'DetailUrl',
                               'Company',
                               'DownloadCount') 
                           VALUES (?,?,?,?,?,?,?,?,?)"""

    create_result = db_helper.create_tabel(AppInfoTable.gen_create_table_sql(AppInfoTable.TABLE_NAME))
    print(create_result)
    db_helper.insert_table_many(sql=sql, value=app_list)


# 拼接应用分类url
def parse_category_url(category_lis):
    base_category_url = WDJ_BASE_URL + '/wdjweb/api/category/more?'
    for category in category_lis:
        url = category[CategoryTable.URL]
        print(url)
        if category[CategoryTable.PARENT_CAT_NAME] == '':
            cat_id = re.findall('\\d+', url)
            print(cat_id)
            category[CategoryTable.URL] = base_category_url + 'catId={}'.format(cat_id[0])
        else:
            number = re.findall('\\d+', url)
            print(number)
            category[CategoryTable.URL] = base_category_url + 'catId={}&subCatId={}'.format(number[0], number[1])
        print(category[CategoryTable.URL])

    return category_lis


# 获取分类信息
def parse_category_info(soup, parent_category_name):
    print(soup)
    name = soup.get('title')
    url = soup.get('href')
    category = {
        CategoryTable.NAME: name,
        CategoryTable.PARENT_CAT_NAME: parent_category_name,
        CategoryTable.STORE: WDJ_STORE_NAME,
        CategoryTable.URL: url
    }

    return category


# 获取应用信息
def parse_page_app_info_list(category_name, sub_category_name, soup):
    page_app_list = []
    li_list = soup.find_all(name='li', class_='card')
    for li in li_list:
        app_name = li.find(name='a', class_="name").text
        # print(app_name)
        app_package_name = li.get('data-pn')
        # print(app_package_name)
        detail_url = li.find(name='a', class_="name").attrs.get('href')
        # print(detail_url)
        icon_url = li.find(name='img').get('data-original')
        # print(icon_url)
        download_num = li.find(name='span', class_="install-count").text.removesuffix('人安装').removesuffix('人下载')
        # print(download_num)
        # app_size = li.find(name='span', attrs={"title": re.compile('\d+MB')}).text
        # print(app_size)
        app = {
            AppInfoTable.APP_NAME: app_name,
            AppInfoTable.APP_PACKAGE_NAME: app_package_name,
            AppInfoTable.APP_CATEGORY: category_name,
            AppInfoTable.APP_TAG: sub_category_name,
            AppInfoTable.APP_STORE: WDJ_STORE_NAME,
            AppInfoTable.APP_ICON_URL: icon_url,
            AppInfoTable.APP_DETAIL_URL: detail_url,
            AppInfoTable.COMPANY: '',
            AppInfoTable.DOWNLOAD_COUNT: download_num
        }
        if category_name == '':
            app[AppInfoTable.APP_CATEGORY] = li.find(name='a', class_="tag-link").text
            # print(app[AppInfoTable.APP_CATEGORY])
        page_app_list.append(app)

    return page_app_list


# 获取豌豆荚应用分类 https://www.wandoujia.com/category/app
def get_wdj_app_category():
    wdj_app_category_list = []
    url = WDJ_BASE_URL + '/category/app'
    print(url)
    response = request.do_request(url)
    if response is None:
        return wdj_app_category_list

    soup = BeautifulSoup(response.text, 'lxml')
    first_category_list = soup.find_all(name='li', class_="parent-cate")
    for first_category in first_category_list:
        temp_category = first_category.find('a')
        parent_category = parse_category_info(temp_category, '')
        wdj_app_category_list.append(parent_category)
        child_category_list = first_category.find(name='div', class_="child-cate").find_all('a')
        for category in child_category_list:
            wdj_app_category_list.append(parse_category_info(category, parent_category[CategoryTable.NAME]))
            
    return wdj_app_category_list


# 获取豌豆荚页面的应用列表 https://www.wandoujia.com/wdjweb/api/category/more?catId=5029&subCatId=0&page=2
def get_wdj_category_app_list(app_category_lis):
    max_page_index = 99
    category_app_list = []
    page_index_str = '&page={}'
    for category in list(filter(lambda cat: cat[CategoryTable.PARENT_CAT_NAME] != '', app_category_lis)):
        parent_category_name = category[CategoryTable.PARENT_CAT_NAME]
        category_name = category[CategoryTable.NAME]
        print(parent_category_name + " " + category_name)
        for page in range(1, max_page_index):
            url = category[CategoryTable.URL] + page_index_str.format(page)
            response = request.do_request(url)
            if response:
                content = json.loads(response.text)['data']['content']
                if content == '':
                    break
                print(f'get page index {page} data')
                soup = BeautifulSoup(content, features="lxml")
                category_app_list += parse_page_app_info_list(parent_category_name, category_name, soup)
            else:
                print(f'page index {page} no data')
                break

    return category_app_list


# 获取豌豆荚排行榜下应用列表 https://www.wandoujia.com/wdjweb/api/top/more?resourceType=0&page=1
# resourceType=0 软件排行榜 resourceType=1 游戏排行榜
def get_wdj_rank_top_list(resource_type=0):
    rank_app_list = []
    rank_url = WDJ_BASE_URL + '/wdjweb/api/top/more?resourceType={}&page={}'
    max_page_index = 999
    for page in range(1, max_page_index):
        url = rank_url.format(resource_type, page)
        print(url)
        response = request.do_request(url)
        if response:
            content = json.loads(response.text)['data']['content']
            if content == '':
                break
            print(f'get page index {page} data')
            soup = BeautifulSoup(content, features="lxml")
            rank_app_list += parse_page_app_info_list(category_name='', sub_category_name='', soup=soup)
        else:
            print(f'page index {page} no data')
            break

    return rank_app_list


# 下载图片到本地目录
def download_icon():
    app_list = []
    fetch_sql = 'SELECT * FROM app'
    raws = db_helper.fetchall_table(fetch_sql)
    print(len(raws))
    for raw in raws:
        app_value = {
            AppInfoTable.APP_NAME: raw[1],
            AppInfoTable.APP_PACKAGE_NAME: raw[2],
            AppInfoTable.APP_CATEGORY: raw[3],
            AppInfoTable.APP_TAG: raw[4],
            AppInfoTable.APP_STORE: raw[5],
            AppInfoTable.APP_ICON_URL: raw[6],
            AppInfoTable.APP_DETAIL_URL: raw[7],
            AppInfoTable.COMPANY: raw[8],
            AppInfoTable.DOWNLOAD_COUNT: raw[9]
        }
        app_list.append(app_value)

    dir_path = 'Icons/'
    for app in app_list:
        pkg_name = app[AppInfoTable.APP_PACKAGE_NAME]
        url = app[AppInfoTable.APP_ICON_URL]
        icon_name = pkg_name + '.' + url.split('/')[-1].split('.')[1]
        print(icon_name)
        icon_path = dir_path + icon_name
        # 判断文件是否存在
        if os.path.isfile(icon_path):
            print('icon already exist')
            continue
        else:
            ImageOperation.download(request, url, dir_path, icon_name)


if __name__ == '__main__':
    db_helper = store.SqliteStore('App.db')
    request = Request(use_cache=True)
    # 应用分类
    wdj_category_list = get_wdj_app_category()
    print(len(wdj_category_list))
    # 修改应用分类url
    parse_category_url(wdj_category_list)

    df_category = pd.DataFrame(wdj_category_list)
    # 应用分类入库
    save_category_info(df_category.values.tolist())

    # 分类下应用
    apps = get_wdj_category_app_list(wdj_category_list)

    # 排行榜
    apps += get_wdj_rank_top_list(resource_type=0)
    apps += get_wdj_rank_top_list(resource_type=1)

    df_app = pd.DataFrame(apps, columns=[
        AppInfoTable.APP_NAME,
        AppInfoTable.APP_PACKAGE_NAME,
        AppInfoTable.APP_CATEGORY,
        AppInfoTable.APP_TAG,
        AppInfoTable.APP_STORE,
        AppInfoTable.APP_ICON_URL,
        AppInfoTable.APP_DETAIL_URL,
        AppInfoTable.COMPANY,
        AppInfoTable.DOWNLOAD_COUNT
    ]).drop_duplicates([AppInfoTable.APP_PACKAGE_NAME])

    print(df_app.head())
    save_app_info(df_app.values.tolist())
    db_helper.close_con()