import json
import re

import pandas as pd
from bs4 import BeautifulSoup

import store
from app_store_crawler import save_app_info, save_category_info
from request import Request
from store import AppInfoTable
from store import CategoryTable

# 应用商店名称简写
WDJ_STORE_NAME = 'WDJ'
# 应用商店基本URL
WDJ_BASE_URL = 'https://www.wandoujia.com'
MAX_PAGE_INDEX = 999

class WdjStoreCrawler:

    def __init__(self, **kwargs):
        self.request = kwargs.get('request', Request(use_cache=True))
        self.store_helper = kwargs.get('store_helper', store.SqliteStore('App.db'))

    # 拼接应用分类url
    def parse_category_url(self, category_lis):
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
    def parse_category_info(self, soup, parent_category_name):
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
    def parse_page_app_info_list(self, category_name, sub_category_name, soup):
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
    def get_wdj_app_category(self):
        wdj_app_category_list = []
        url = WDJ_BASE_URL + '/category/app'
        print(url)
        response = self.request.do_request(url)
        if response is None:
            return wdj_app_category_list
        soup = BeautifulSoup(response.text, 'lxml')
        first_category_list = soup.find_all(name='li', class_="parent-cate")
        for first_category in first_category_list:
            temp_category = first_category.find('a')
            parent_category = self.parse_category_info(temp_category, '')
            wdj_app_category_list.append(parent_category)
            child_category_list = first_category.find(name='div', class_="child-cate").find_all('a')
            for category in child_category_list:
                wdj_app_category_list.append(self.parse_category_info(category, parent_category[CategoryTable.NAME]))

        return self.parse_category_url(wdj_app_category_list)

    # 获取豌豆荚页面的应用列表 https://www.wandoujia.com/wdjweb/api/category/more?catId=5029&subCatId=0&page=2
    def get_wdj_category_app_list(self, app_category_lis):
        category_app_list = []
        page_index_str = '&page={}'
        for category in list(filter(lambda cat: cat[CategoryTable.PARENT_CAT_NAME] != '', app_category_lis)):
            parent_category_name = category[CategoryTable.PARENT_CAT_NAME]
            category_name = category[CategoryTable.NAME]
            print(parent_category_name + " " + category_name)
            for page in range(1, MAX_PAGE_INDEX):
                url = category[CategoryTable.URL] + page_index_str.format(page)
                response = self.request.do_request(url)
                if response:
                    content = json.loads(response.text)['data']['content']
                    if content == '':
                        break
                    print(f'get page index {page} data')
                    soup = BeautifulSoup(content, features="lxml")
                    category_app_list += self.parse_page_app_info_list(parent_category_name, category_name, soup)
                else:
                    print(f'page index {page} no data')
                    break
        return category_app_list

    # 获取豌豆荚排行榜下应用列表 https://www.wandoujia.com/wdjweb/api/top/more?resourceType=0&page=1
    # resourceType=0 软件排行榜 resourceType=1 游戏排行榜
    def get_wdj_rank_top_list(self, resource_type=0):
        rank_app_list = []
        rank_url = WDJ_BASE_URL + '/wdjweb/api/top/more?resourceType={}&page={}'
        for page in range(1, MAX_PAGE_INDEX):
            url = rank_url.format(resource_type, page)
            print(url)
            response = self.request.do_request(url)
            if response:
                content = json.loads(response.text)['data']['content']
                if content == '':
                    break
                print(f'get page index {page} data')
                soup = BeautifulSoup(content, features="lxml")
                rank_app_list += self.parse_page_app_info_list(category_name='', sub_category_name='', soup=soup)
            else:
                print(f'page index {page} no data')
                break

        return rank_app_list

    def search_result_list(self, keywords):
        search_result_list = []
        search_url = WDJ_BASE_URL + '/wdjweb/api/search/more?page={}&key={}'
        for keyword in keywords:
            for page_index in range(0, MAX_PAGE_INDEX):
                url = search_url.format(page_index, keyword)
                print(url)
                response = self.request.do_request(url)
                if response:
                    content = json.loads(response.text)['data']['content']
                    if content == '':
                        break
                    soup = BeautifulSoup(content, features="lxml")
                    search_result_list += self.parse_page_app_info_list('', '', soup)

        return search_result_list


if __name__ == '__main__':
    db_helper = store.SqliteStore('App.db')
    request = Request(use_cache=True)
    wdj_crawler = WdjStoreCrawler(request=request, store_helper=db_helper)

    # 应用分类
    wdj_category_list = wdj_crawler.get_wdj_app_category()
    print(len(wdj_category_list))

    df_category = pd.DataFrame(wdj_category_list)
    # 应用分类入库
    save_category_info(db_helper, df_category.values.tolist())

    # 分类下应用
    apps = wdj_crawler.get_wdj_category_app_list(wdj_category_list)

    # 排行榜
    apps += wdj_crawler.get_wdj_rank_top_list(resource_type=0)
    apps += wdj_crawler.get_wdj_rank_top_list(resource_type=1)

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
    save_app_info(db_helper, df_app.values.tolist())
    db_helper.close_con()
