# -*- coding:utf-8 -*-

__Author__ = 'HuZhiKai'

import os
import os.path
# import random
# import time
# from urllib.request import urlretrieve  # 直接下载资源的方法
import re
import time
import requests
from bs4 import BeautifulSoup
# from selenium import webdriver
# # import selenium
# # import selenium.webdriver.support.ui as ui
# # from selenium.common.exceptions import TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# # from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 Chrome/103.0.0.0 '  # 
                  'Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br'
}


def check_connect():
    # 通过检验网页标题顺利加载，来断定网站服务正常
    check = requests.get('https://www.gequbao.com/', timeout=7)
    soup = BeautifulSoup(check.text, 'lxml')
    if '歌曲宝' in (title := soup.title.string):
        return title
    else:
        return None


def url_music_name(name_put):
    url_ready = "https://www.gequbao.com/s/" + name_put  # 拉取音乐页面，获取音乐标签里的关键信息
    site = requests.get(url_ready)
    # bs方法获取标签内容
    bs = BeautifulSoup(site.text, "lxml")  # hml.parser解析不能对复杂内容处理，这里使用lxml
    bs_tag = bs.select(".text-primary.font-weight-bold")  # 通过class属性定位到标签
    url_name_list = []
    for url_and_name in bs_tag:  # 测试限制了数据，记得改过来[:20]
        url_name_list.append(str(url_and_name)[48:].strip(
            r"\n                                                                    </a>"))  #
        # 有换行，对其进行处理，处理后再来个循环进行链接与歌曲名的分割
    out_array = []
    for m in url_name_list:
        url_str = m.split("\">")[0]  # 很好，数据越来越短，离想提取的数据越来越近。这里利用切片和数组索引那到了第一个值
        music_name_str = name_put + '_' + m.split("\">")[1][:-1]
        out_array.append([url_str, music_name_str])
    return out_array  # 搜索歌手的结果列表，取到链接与歌曲名的数组


def second_url_name(name):
    another_url = "https://www.gequbao.com/s/" + name
    site = requests.get(another_url, headers=header)

    # bs方法获取标签内容
    bs = BeautifulSoup(site.text, "lxml")  # html.parser解析不能对复杂内容处理，这里使用lxml
    bst_tag = bs.find_all('tr')  # 通过tr标签匹配

    print("\n【注意】：当搜索的是歌曲名时，为节省资源，\n  将仅下载搜索结果的前五首歌曲！  ")
    list_from_bs = []
    for urlMusicName in bst_tag[1:6]:
        not_ready = str(urlMusicName)[57:-56].split("\n")
        # print(not_ready)
        list_from_bs.append([not_ready[0], not_ready[-1]])
    print("----------------")
    out = []
    for m, n in list_from_bs:
        url_put = m.split("\">")[0]  # 很好，数据越来越短，离想提取的数据越来越近。这里利用切片和数组索引那到了第一个值
        music_may_put = m.split("\">")[1]
        singer = n.strip('<td class="text-success">')

        music_put = music_may_put + "_" + singer
        # print(f"music_may_put's Content is |{music_put}|")
        out.append([url_put, music_put])  # 添加到列表后，我们看看是不是真的提取到了这两个值
    return out


# 想办法由列表数据，生成一个只含下载链接的数组
def getDownUrl(input_list=None):
    if input_list is None:
        input_list = [['music/81215', '笨小孩 (Live)'], ['music/37479', '忘情水(Live)']]
    s = requests.session()
    # 设置连接活跃状态为False
    s.keep_alive = False

    checklist = []
    for xi, yi in input_list:
        final_url = "https://www.gequbao.com/" + xi
        response = requests.get(final_url, headers=header, timeout=100)  # 超时
        response.close()

        down_url = re.findall(r'url = (.+)\.', response.text)[0].strip('\'').strip('\'').replace(r'amp;',
                                                                                                 '')  # 合理提取MP3链接
        yi = yi.replace('...', '')

        checklist.append([down_url, yi])
    return checklist


# def SeleniumDown(list_for=None):
#     from pykeyboard import PyKeyboard
#     from pymouse import PyMouse
#     k = PyKeyboard()
#     mouse = PyMouse()
#     xm, ym = mouse.screen_size()  # 获取屏幕尺寸
#     # print(xm,ym)
#     # 继续通过访问页面，再获取页面下的链接来
#     wd = webdriver.Chrome()
#     action = ActionChains(wd)
#
#     # 先打开一个基本页面
#     urlencoded = "https://www.gequbao.com/s/%E5%88%98%E5%BE%B7%E5%8D%8E"
#     wd.get(urlencoded)  # 是否调用浏览器
#     wd.maximize_window()
#
#     # 拿到下载页的button
#     downBtn = "//*[@id='btn-download-mp3']"
#     if list_for is None:
#         list_for = []
#
#     # 循环调用下载详情页地址
#     for content in list_for:
#         detailUrl = "https://www.gequbao.com/" + content[0]
#         after_string = str(random.randint(10, 20))
#         print(content[1])
#         detailMusicName = content[1] + after_string
#
#         wd.get(detailUrl)
#         handles = wd.window_handles
#         wd.switch_to.window(handles[-1])
#         wd.implicitly_wait(1.5)
#         # 使用webdriver调用button点击下载
#         wd.find_element(By.XPATH, downBtn).click()  # 注释掉
#         handles = wd.window_handles
#         wd.switch_to.window(handles[-1])
#         wd.implicitly_wait(2)
#
#         # 随机定位浏览器播放页的元素
#         # ele = "//body/video/source[@type='audio/mpeg']"      # 选取任意元素
#         # inputElement = wd.find_element(By.XPATH,ele)          # 找不到元素
#         # time.sleep(1)
#         # playEle = wd.find_element(By.CSS_SELECTOR,css_selector)
#         # playEle = wd.find_element(By.TAG_NAME,tag_name)
#
#         # ctrl+s 保存当前文件。重复保存一次，并给予弹窗足够保留时间
#         action.reset_actions()
#         action.move_by_offset(xm / 2, ym / 2).click(None).perform()  # 点击空白处
#         # action.key_down(Keys.CONTROL).send_keys('s').key_up(Keys.CONTROL).perform()
#         # print("------[1]------")
#         # playEle.send_keys(Keys.CONTROL,'s')
#         # print("------[2]------")
#         k.press_key(k.control_key)
#         k.tap_key("S", n=2, interval=1)
#         k.release_key(k.control_key)
#         time.sleep(3)
#
#         # 输入歌名
#         k.type_string(detailMusicName)
#         # print("输入音乐保存名了。。。")
#
#         # 联合点击Alt+s 快速定位到保存按钮: 替代回车键
#         # inputElement.send_keys(Keys.ENTER)
#         k.press_key(k.alt_key)  # 按住alt键
#         k.tap_key("S")  # 单骑s键
#         k.release_key(k.alt_key)  # 释放alt键
#
#         # 给两秒的下载时间
#         time.sleep(2)
#         # 慎用close操作
#         # wd.close()
#         print(f"执行了第{list_for.index(content) + 1}次")
#     wd.quit()
#
#
# def displayProgress(module, totalsize, which):
#     """
#     Dynamic display of progress
#     :param module:已经下载的数据块
#     :param totalsize:数据块的大小
#     :param which:远程文件的大小
#     :return:不用return，直接打印
#     """
#     progressDown = module * totalsize * 100.0 / which
#     if progressDown > 100:
#         progressDown = 100
#
#     print("\r downloading: %.1f%%" % progressDown, end="")
#
#
# def downloadMp3(uurl, singer_music):
#     if '.' in uurl[-6:]:
#         postfix = uurl.split(".")[-1]
#     else:
#         postfix = uurl.split("=")[-1]
#     MusicName = singer_music + "." + postfix
#     print(f'MusicName = {MusicName}')
#     downloadPath = "./" + input_name
#
# try:
#     os.makedirs(input_name, exist_ok=True)
#     print("目录已创建！")
# finally:
#     pass
#     downloadDir = downloadPath + "/" + MusicName
#     urlretrieve(uurl, downloadDir, displayProgress)  # api接口的可以直接下，部分接口暂无法正常下载
#     print("  下载完成！")


def fileDownloadUsingRequests(file_url, music_name):
    """It will download file specified by url using requests module"""
    global r

    # 处理文件后缀名
    if file_url.count("=") >= 2:
        file_suf = '.' + file_url.split('=')[-1]
    else:
        file_suf = '.' + file_url.split('.')[-1]
    # 处理文件命名异常，非法命名无法保存到windows磁盘里
    if "<" in music_name:
        music_name = music_name.split("<")[0]  # .replace("<","")，多了个斜杠
    if "|" in music_name or "/" in music_name:
        music_name = music_name.replace("/", "")
        music_name = music_name.replace("|", "")
    if True:
        music_name = music_name.replace(r"amp;", "")
        music_name = music_name.replace(r":", "")

    file_name = music_name.replace(",", "") + file_suf
    print(f"已获取歌名：{file_name}！")
    pwd = os.path.join(os.getcwd(), input_name, file_name)
    file_position = os.path.join(os.getcwd(), input_name)
    # print(pwd)
    if not os.path.exists(file_position):
        os.mkdir(input_name)
        print(f"目录'{input_name}'已创建！")

    if os.path.exists(pwd):
        print('File already exists')
        return
    try:
        r = requests.get(file_url, stream=True, timeout=200)
    except requests.exceptions.SSLError:
        try:
            response = requests.get(file_url, stream=True, verify=False, timeout=200)
            print(f'连接状态：{response.status_code}')
        except requests.exceptions.RequestException as e:
            print(e)
            quit()
    except requests.exceptions.RequestException as e:
        print(e)
        quit()
    chunk_size = 1024

    # total_size = int(r.headers['Content-Length'])
    # 对headers['Content-Length']无值的情况作跳过处理
    if getValue := r.headers.get('Content-Length'):
        total_chunks = int(getValue) / chunk_size
        print('歌曲包totalSize：%.2fKB' % total_chunks)

        file_iterable = r.iter_content(chunk_size=chunk_size)
        # 用tqdm进度提示信息，包括执行进度、处理速度等信息，且可在一定程度上进行定制。
        tqdm_iter = tqdm(iterable=file_iterable, total=total_chunks, unit='KB',
                         leave=False, colour='MAGENTA'
                         )
        with open(pwd, 'wb') as f:  # file_name
            for data in tqdm_iter:
                f.write(data)  # 字节写入

        print('Downloaded file %s\n------------------------------------' % file_name)
    else:
        print(f'检测到歌曲：{file_name}下载链接已失效！')
        with open(r'.\失效歌曲.txt', 'a') as newF:
            newF.write(file_name)
        return


if __name__ == "__main__":
    global input_name

    # 搜歌手 和 搜歌名的方式结合后，去下载
    print('\n小Tips：输入2后，按歌名+歌手名搜索。如搜索："Mojito 周杰伦"')
    while 1:
        down_type = input("请输入搜索方式-- 1：歌手；2：歌名！：")
        down_type = down_type.strip()
        if down_type in ('1', '2'):
            break
        else:
            print('请输入 1 或者 2 ')
    while 1:
        try:
            input_name = input("请输入要搜索的内容：")
            if input_name:
                print('~~~即将校验搜索搭载的服务是否可用~~~')
                if check_connect():
                    print('服务正常，网络可用！')
                    print('歌曲下载源的解析速率取决于源服务器效率，下载时长取决于歌曲大小，请耐心等待！')
                else:
                    print('歌曲源出现问题，请联系作者更新歌曲源！作者:bg110123@gmail.com')
                break
        finally:
            pass

    if down_type == "1":
        get_now = getDownUrl(url_music_name(input_name))
        if len(get_now) < 1:
            print('暂未搜索到歌曲资源，请等待作者更新歌源！')
            print('按ctrl C退出程序~~~')
        else:
            for du, dn in get_now:
                fileDownloadUsingRequests(du, dn)
            print("\n全部下载：已完成！")
    elif down_type == "2":
        letGo = getDownUrl(second_url_name(input_name))
        print(letGo)
        if len(letGo) < 1:
            print('暂未搜索到歌曲资源，请等待作者更新歌源！')
            print('按ctrl C退出程序~~~')

        else:
            for mm, nn in letGo:
                fileDownloadUsingRequests(mm, nn)
            print("\n全部下载：已完成！<-- Author:HuZK --> 将在18秒后自动关闭窗口！")

    else:
        print("Unknown error.Check ur code again pls.")
    for i in range(18)[::-1]:
        print(f'窗口关闭倒计时： {i + 1} 秒！')
        time.sleep(1)
