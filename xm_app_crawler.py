import json
import re

import pandas as pd
from bs4 import BeautifulSoup

import store
from app_store_crawler import save_app_info
from request import Request
from store import AppInfoTable

# 应用商店名称简写
XM_STORE_NAME = 'XM'
# 应用商店基本URL
XM_BASE_URL = 'https://app.mi.com'
# 类型最大数量
MAX_CATEGORY_INDEX = 29
MAX_PAGE_INDEX = 999


class XiaoMiAppStoreCrawler:
    def __init__(self, **kwargs):
        self.request = kwargs.get('request', Request(use_cache=True))


    def parse_app_list_from_json(self, app_list):
        apps = []
        for app in app_list:
            apps.append({
                AppInfoTable.APP_NAME: app['displayName'],
                AppInfoTable.APP_PACKAGE_NAME: app['packageName'],
                AppInfoTable.APP_CATEGORY: app['level1CategoryName'],
                AppInfoTable.APP_TAG: app['level2CategoryName'],
                AppInfoTable.APP_STORE: XM_STORE_NAME,
                AppInfoTable.APP_ICON_URL: app['icon'],
                AppInfoTable.APP_DETAIL_URL: XM_BASE_URL + 'details?id=' + app['packageName'],
                AppInfoTable.COMPANY: app['publisherName'],
                AppInfoTable.DOWNLOAD_COUNT: ''
            })
        return apps

    def get_app_list(self, max_category=MAX_CATEGORY_INDEX, max_page=MAX_PAGE_INDEX):
        app_list = []
        url_str = XM_BASE_URL + '/categotyAllListApi?page={}&categoryId={}&pageSize=30'
        for category_index in range(max_category):
            for page_index in range(max_page):
                url = url_str.format(page_index, category_index)
                print(url)
                response = request.do_request(url)
                has_next = False
                if response:
                    data = json.loads(response.text)['data']
                    has_next = json.loads(response.text)['hasNext']
                    app_list += self.parse_app_list_from_json(data)
                    print(f'get page index {page_index} data')
                if not has_next:
                    break
        return app_list

    def parse_app_list(self, li_list):
        result_list = []
        for li in li_list:
            app_name = li.find(name='h5').find(name='a').text
            # print(app_name)
            detail_url = li.find(name='a').attrs.get('href')
            # print(detail_url)
            app_package_name = re.findall('(?<=details\?id\=).*$', detail_url)[0]
            # print(app_package_name)
            icon_url = li.find(name='img').get('data-src')
            # print(icon_url)
            download_num = ''
            # print(download_num)
            category = li.find(name='p').find(name='a').text
            # print(category)
            app = {
                AppInfoTable.APP_NAME: app_name,
                AppInfoTable.APP_PACKAGE_NAME: app_package_name,
                AppInfoTable.APP_CATEGORY: category,
                AppInfoTable.APP_TAG: '',
                AppInfoTable.APP_STORE: XM_STORE_NAME,
                AppInfoTable.APP_ICON_URL: icon_url,
                AppInfoTable.APP_DETAIL_URL: XM_BASE_URL + detail_url,
                AppInfoTable.COMPANY: '',
                AppInfoTable.DOWNLOAD_COUNT: download_num
            }
            result_list.append(app)

        return result_list

    def get_category_top_list(self, max_category=MAX_CATEGORY_INDEX, max_page=MAX_PAGE_INDEX):
        app_list = []
        url_str = XM_BASE_URL + '/catTopList/{}?page={}'
        for category_index in range(1, max_category):
            for page_index in range(1, max_page):
                url = url_str.format(category_index, page_index)
                print(url)
                response = request.do_request(url)
                if response:
                    print(f'get page index {page_index} data')
                    soup = BeautifulSoup(response.text, 'lxml')
                    result_list = soup.find(name='ul', class_="applist").find_all(name='li')
                    if len(result_list) == 0:
                        print('category no app')
                        break
                    app_list += self.parse_app_list(result_list)
        return app_list


if __name__ == '__main__':
    print('start Xiao Mi App Store crawler')
    request = Request(use_cache=True)
    xm_crawler = XiaoMiAppStoreCrawler(request=request)
    xm_app_list = []
    # xm_app_list += xm_crawler.get_app_list()
    xm_app_list += xm_crawler.get_category_top_list(max_page=10)
    print('finish Xiao Mi App Store crawler')
    print('Total count:', len(xm_app_list))
    db_helper = store.SqliteStore('AppInfo.db')
    df_app = pd.DataFrame(xm_app_list, columns=[
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

    print(len(df_app))
    save_app_info(db_helper, df_app.values.tolist())
    db_helper.close_con()
