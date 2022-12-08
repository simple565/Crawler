import os
import shutil

import store
from img_tool import ImageOperation
from request import Request
from store import AppInfoTable
from store import CategoryTable


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


# 过滤出热门应用图标
def filter_hot_app_icon():
    app_helper = store.SqliteStore('App.db')
    apps = []
    fetch_sql = "SELECT * FROM app WHERE DownloadCount LIKE'%万%'"
    raws = app_helper.fetchall_table(fetch_sql)
    print(len(raws))
    output_dir_path = os.path.join(os.getcwd(), 'AppIcons')
    input_dir_path = os.path.join(os.getcwd(), 'WebpIcons')
    for raw in raws:
        apps.append({
            AppInfoTable.APP_NAME: raw[1],
            AppInfoTable.APP_PACKAGE_NAME: raw[2],
            AppInfoTable.APP_CATEGORY: raw[3],
            AppInfoTable.APP_TAG: raw[4],
            AppInfoTable.APP_STORE: raw[5],
            AppInfoTable.APP_ICON_URL: raw[6],
            AppInfoTable.APP_DETAIL_URL: raw[7],
            AppInfoTable.COMPANY: raw[8],
            AppInfoTable.DOWNLOAD_COUNT: raw[9]
        })
        img_path = os.path.join(input_dir_path, raw[2] + '.webp')
        output_path = os.path.join(output_dir_path, raw[2] + '.webp')
        print(raw[1] + raw[9] + img_path)
        if os.path.isfile(img_path):
            shutil.copy(img_path, output_path)
        else:
            print(f"{img_path} not exist!")

    print(len(apps))
    app_helper.close_con()


# 存储应用分类信息
def save_category_info(store_helper, category_list):
    sql = """INSERT OR IGNORE INTO 'category' ('CategoryName', 'ParentCategoryName', 'Store', 'Url') VALUES (?,?,?,?)"""
    create_result = store_helper.create_tabel(CategoryTable.gen_create_table_sql(CategoryTable.TABLE_NAME))
    print(create_result)
    store_helper.insert_table_many(sql=sql, value=category_list)


# 存储应用信息
def save_app_info(store_helper, app_list):
    sql = """INSERT OR IGNORE INTO 'app' ('AppName','PackageName',
                               'Category',
                               'Tag',
                               'Store',
                               'IconUrl',
                               'DetailUrl',
                               'Company',
                               'DownloadCount') 
                           VALUES (?,?,?,?,?,?,?,?,?)"""

    create_result = store_helper.create_tabel(AppInfoTable.gen_create_table_sql(AppInfoTable.TABLE_NAME))
    print(create_result)
    store_helper.insert_table_many(sql=sql, value=app_list)


if __name__ == '__main__':
    db_helper = store.SqliteStore('App.db')
    request = Request(use_cache=True)
    download_icon()
    filter_hot_app_icon()
