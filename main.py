import pandas as pd

if __name__ == '__main__':
    app = {'name': '测试', 'pkg_name':'com.my.test', 'tag':'系统工具'}
    app1 = {'name': '测试', 'pkg_name':'com.my.test', 'tag':'系统工具'}
    app2 = {'name': '测试3', 'pkg_name':'com.my.tes3t', 'tag':'系统工具'}
    app3 = {'name': '测试2', 'pkg_name':'com.my.test2', 'tag':'系统工具'}
    app4 = {'name': '测试', 'pkg_name':'com.my.test', 'tag':'系统工具'}
    app_list = [app, app1, app2, app3, app4]
    df = pd.DataFrame(app_list)
    # 加一句df_apply_index = df_apply.reset_index()
    # df_apply = df.groupby(['pkg_name', 'name'], as_index=False, axis=0).apply(lambda x: ','.join(x['tag']))
    df_apply = df.groupby(['pkg_name', 'name'], as_index=False, axis=0).apply(lambda x: ','.join(x['tag']))
    print(df_apply)
    df_apply = pd.DataFrame(df_apply, columns=['存钱占比'])  # 转化成dataframe格式
    df_apply_index = df_apply.reset_index()
    print(df_apply_index)
    print('111人安装'.removesuffix('人安装'))
