import json

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


    def parse_app_list(self, app_list):
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
                    app_list += self.parse_app_list(data)
                print(f'get page index {page_index} data')
                if not has_next:
                    break
        return app_list


if __name__ == '__main__':
    print('start Xiao Mi App Store crawler')
    request = Request(use_cache=True)
    xm_app_list = XiaoMiAppStoreCrawler(request=request).get_app_list()
    print('finish Xiao Mi App Store crawler')
    print('Total count:', len(xm_app_list))
