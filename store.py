import sqlite3


class CategoryTable:
    TABLE_NAME = 'category'
    NAME = 'CategoryName'
    PARENT_CAT_NAME = 'ParentCategoryName'
    STORE = 'Store'
    URL = 'Url'

    @staticmethod
    def gen_create_table_sql(table_name):
        return """CREATE TABLE IF NOT EXISTS %s 
                        (_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        %s TEXT,
                        %s TEXT,
                        %s TEXT,
                        %s TEXT)
                        """ % (table_name,
                               CategoryTable.NAME,
                               CategoryTable.PARENT_CAT_NAME,
                               CategoryTable.STORE,
                               CategoryTable.URL)


class AppInfoTable:
    TABLE_NAME = 'app'
    APP_NAME = 'AppName'
    APP_DETAIL_URL = "DetailUrl"
    APP_PACKAGE_NAME = 'PackageName'
    APP_CATEGORY = 'Category'
    APP_TAG = 'Tag'
    APP_STORE = 'Store'
    APP_ICON_URL = 'IconUrl'
    COMPANY = 'Company'
    DOWNLOAD_COUNT = 'DownloadCount'

    @staticmethod
    def gen_create_table_sql(table_name):
        return """CREATE TABLE IF NOT EXISTS %s 
                    (_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    %s TEXT,
                    %s TEXT UNIQUE,
                    %s TEXT,
                    %s TEXT,
                    %s TEXT,
                    %s TEXT,
                    %s TEXT,
                    %s TEXT,
                    %s TEXT )
                    """ % (table_name,
                           AppInfoTable.APP_NAME,
                           AppInfoTable.APP_PACKAGE_NAME,
                           AppInfoTable.APP_CATEGORY,
                           AppInfoTable.APP_TAG,
                           AppInfoTable.APP_STORE,
                           AppInfoTable.APP_ICON_URL,
                           AppInfoTable.APP_DETAIL_URL,
                           AppInfoTable.COMPANY,
                           AppInfoTable.DOWNLOAD_COUNT
                           )


class SqliteStore:
    db_path = None

    def __init__(self, db_name):
        """
        ???????????????--???????????????????????????
        :param db_name: ??????????????????????????????'.db'??????
        """
        self._conn = sqlite3.connect(db_name)
        self._cur = self._conn.cursor()

    def close_con(self):
        """
        ??????????????????--????????????
        :return:
        """
        self._cur.close()
        self._conn.close()

    def create_tabel(self, sql):
        """
        ??????????????????
        :param sql: ????????????
        :return: True is ok
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return True
        except Exception as e:
            return False

    def drop_table(self, table_name):
        """
        ?????????
        :param table_name: ??????
        :return:
        """
        try:
            self._cur.execute('DROP TABLE {0}'.format(table_name))
            self._conn.commit()
            return True
        except Exception as e:
            return False

    def delete_table(self, sql):
        """
        ???????????????
        :param sql:
        :return: True or False
        """
        try:
            if 'DELETE' in sql.upper():
                self._cur.execute(sql)
                self._conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print("[DELETE TABLE ERROR]", e)
            return False

    def fetchall_table(self, sql, limit_flag=True):
        """
        ??????????????????
        :param sql:
        :param limit_flag: ?????????????????????False ???????????????True ????????????
        :return: [(xxx, xxxx, xxx), (xxx, xxxx, xxx)]
        """
        try:
            self._cur.execute(sql)
            war_msg = ' The [{}] is empty or equal None!'.format(sql)
            if limit_flag is True:
                r = self._cur.fetchall()
                return r if len(r) > 0 else war_msg
            elif limit_flag is False:
                r = self._cur.fetchone()
                return r if len(r) > 0 else war_msg
        except Exception as e:
            print("[FETCHALL TABLE ERROR]", e)

    def insert_update_table(self, sql):
        """
        ??????/???????????????
        :param sql:
        :return:
        """
        try:
            self._cur.execute(sql)
            self._conn.commit()
            return True
        except Exception as e:
            print("[INSERT/UPDATE TABLE ERROR]", e)
            return False

    def insert_table_many(self, sql, value):
        """
        ??????????????????
        :param sql:
        :param value: list:[(),()]
        :return:
        """
        try:
            self._cur.executemany(sql, value)
            self._conn.commit()
            return True
        except Exception as e:
            print("[INSERT MANY TABLE ERROR]", e)
            return False


if __name__ == '__main__':
    sqlite_helper = SqliteStore('/../AppInfo.db')
    create_result = sqlite_helper.create_tabel(AppInfoTable.gen_create_table_sql(AppInfoTable.TABLE_NAME))
    print(create_result)
    sqlite_helper.close_con()
