import json
import re

import pandas as pd
from bs4 import BeautifulSoup

import store
from app import AppCategory
from request import Request
from store import AppInfoTable

# 应用商店名称简写
WDJ_STORE_NAME = 'WDJ'

# 存储应用信息
def save_app_info(app_info):
    sql = """
    INSERT INTO app(${AppInfoTable.APP_NAME},
                    ${AppInfoTable.APP_PACKAGE_NAME},
                           ${AppInfoTable.APP_CATEGORY},
                           ${AppInfoTable.APP_TAG},
                           ${AppInfoTable.APP_STORE},
                           ${AppInfoTable.APP_ICON_URL},
                           ${AppInfoTable.COMPANY},
                           ${AppInfoTable.DOWNLOAD_COUNT}) 
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
    """

    db_helper = store.SqliteStore('/../App.db')
    for pkg_name, app in app_info.items():
        db_helper.insert_table_many(sql=sql, value=app)
    db_helper.close_con()


# 拼接应用分类url
def parse_category_url(app_category_lis):
    url_list = []
    base_url = 'https://www.wandoujia.com/wdjweb/api/category/more?'
    for category in app_category_lis:
        # print(category.name)
        # print(category.url)
        cat_id = re.findall('\\d+', category.url)[0]
        # print(cat_id)
        category.url = base_url + 'catId={}'.format(cat_id)
        # print(category.url)
        for child_category in category.child_app_category:
            # print(child_category.name)
            # print(child_category.url)
            number = re.findall('\\d+', child_category.url)
            # print(number)
            child_category.url = base_url + 'catId={}&subCatId={}'.format(number[0], number[1])
            # print(child_category.url)
            url_list.append(child_category)
    return url_list


# 获取应用信息
def parse_app_info_list(category_name, sub_category_name, soup, app):
    li_list = soup.find_all(name='li', class_='card')
    for li in li_list:
        app_name = li.find(name='a', class_="name").text
        print(app_name)
        app_package_name = li.get('data-pn')
        print(app_package_name)
        detail_url = li.find(name='a', class_="name").attrs.get('href')
        print(detail_url)
        icon_url = li.find(name='img').get('data-original')
        print(icon_url)
        download_num = li.find(name='span', class_="install-count").text
        print(download_num)
        # app_size = li.find(name='span', attrs={"title": re.compile('\d+MB')}).text
        # print(app_size)
        # download_app_icon(app_name, app_package_name, icon_url)
        app[app_package_name] = {
            AppInfoTable.APP_NAME: app_name,
            AppInfoTable.APP_PACKAGE_NAME: app_package_name,
            AppInfoTable.APP_CATEGORY: category_name,
            AppInfoTable.APP_TAG: sub_category_name,
            AppInfoTable.APP_STORE: WDJ_STORE_NAME,
            AppInfoTable.APP_ICON_URL: icon_url,
            AppInfoTable.APP_DETAIL_URL: detail_url,
            AppInfoTable.DOWNLOAD_COUNT: download_num
        }


# 获取豌豆荚应用分类 https://www.wandoujia.com/category/app
def get_wdj_app_category():
    wdj_app_category_list = []
    url = 'https://www.wandoujia.com/category/app'
    print(url)
    category_result = Request().do_request(url).text
    soup = BeautifulSoup(category_result, 'lxml')
    first_category_list = soup.find_all(name='li', class_="parent-cate")
    for first_category in first_category_list:
        temp_category = first_category.find('a')
        # print(first_category)
        first_category_name = temp_category.get('title')
        first_category_url = temp_category.get('href')
        child_lis = []
        child_category_list = first_category.find(name='div', class_="child-cate").find_all('a')
        for category in child_category_list:
            # print(category)
            child_name = category.get('title')
            child_url = category.get('href')
            child_lis.append(AppCategory(name=child_name, url=child_url, child_app_category=[]))

        app_category = AppCategory(name=first_category_name, url=first_category_url, child_app_category=child_lis)
        wdj_app_category_list.append(app_category)
    return wdj_app_category_list


# 获取豌豆荚指定分类下的应用列表 https://www.wandoujia.com/wdjweb/api/category/more?catId=5029&subCatId=0&page=2
def get_wdj_app_list(app_category_lis):
    app = {}
    page_index = '&page={}'
    for category in app_category_lis:
        # print(category.name)
        for sub_category in category.child_app_category:
            # print(sub_category.name)
            for page in range(1, 2):
                url = sub_category.url + page_index.format(page)
                print(url)
                response = request.do_request(url)
                content = json.loads(response.text)['data']['content']
                if content == '':
                    print('page index ${page_index} no data')
                    break
                soup = BeautifulSoup(content, features="lxml")
                parse_app_info_list(category.name, sub_category.name, soup, app)
    return app


# 获取豌豆荚排行榜下应用列表 https://www.wandoujia.com/wdjweb/api/top/more?resourceType=0&page=1
# resourceType=0 软件排行榜 resourceType=1 游戏排行榜
def get_wdj_rank_top_list():
    app = {}
    rank_url = 'https://www.wandoujia.com/wdjweb/api/top/more?resourceType={}&page={}'
    max_page_index = 3
    resource_type = 0
    for page in range(1, max_page_index):
        url = rank_url.format(resource_type, page)
        print(url)
        response = request.do_request(url)
        content = json.loads(response.text)['data']['content']
        if content == '':
            print('page index ${page} no data')
            break
        soup = BeautifulSoup(content, features="lxml")
        parse_app_info_list('', '', soup, app)


if __name__ == '__main__':
    request = Request(use_cache=True)
    df = pd.DataFrame(columns=[AppInfoTable.APP_NAME, AppInfoTable.APP_PACKAGE_NAME,
                               AppInfoTable.APP_CATEGORY, AppInfoTable.APP_TAG,
                               AppInfoTable.APP_STORE, AppInfoTable.APP_ICON_URL,
                               AppInfoTable.APP_DETAIL_URL, AppInfoTable.DOWNLOAD_COUNT])

    # get_wdj_rank_top_list()
    # wdj_category_list = get_wdj_app_category()
    # parse_category_url(wdj_category_list)
    # app_list = get_wdj_app_list(wdj_category_list)
    app_list = {}
    app_list['app_package_name'] = {
        AppInfoTable.APP_NAME: 'app_name',
        AppInfoTable.APP_PACKAGE_NAME: 'app_package_name',
        AppInfoTable.APP_CATEGORY: 'category_name',
        AppInfoTable.APP_TAG: 'sub_category_name',
        AppInfoTable.APP_STORE: WDJ_STORE_NAME,
        AppInfoTable.APP_ICON_URL: 'icon_url',
        AppInfoTable.APP_DETAIL_URL: 'detail_url',
        AppInfoTable.DOWNLOAD_COUNT: 'download_num'
    }
    save_app_info(app_list)

    # df.append(app_list, ignore_index=True)
    # df = df.drop_duplicates(['pkg_name'])
    # df.to_excel('result_wdj.xlsx')





