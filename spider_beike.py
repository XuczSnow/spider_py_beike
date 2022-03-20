# from cgi import print_arguments
import os
import re
# import pymysql
from urllib import request
from bs4 import BeautifulSoup
import requests
import time
import csv

page_num = 9
url_base = 'https://bj.zu.ke.com/ditiezufang/li46537785s46538264/'

# host = 'localhost'
# port = 3306
# db = 'xianzufang'
# user = 'root'
# password = '961013zxc'

# # 连接数据库
# db = pymysql.connect(host=host, port=port, db=db, user=user, password=password)

def get_bc(page = ''):
    # 获取网页源码
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30'
    }

    url_title = 'https://xa.zu.ke.com/'
    # 如果需要查询别的地区的房子，直接改这个就行
    url = url_base + page

    response = requests.get(url, headers=headers)

    res = BeautifulSoup(response.text, 'lxml')
    res_fang = res.find_all('div', class_='content__list--item')

    # 遍历一个页面的所有房源信息
    for fang in res_fang:
        # 获取基础信息
            #  通过社区信息判断是不是为广告
        des = fang.find('div', class_='content__list--item--main').find('p', class_='content__list--item--des')
        des_ad = des.find('span', class_='room__left')
        print(des_ad)
        if des_ad != None:
            break
        des_text = des.find_all('a')
        des_community = des_text[2].get_text()

        
        title = fang.find('div', class_='content__list--item--main').find('p', class_='content__list--item--title')
        title_url = url_title + title.find('a').get('href')
        title_name = title.find('a').get_text()[11:26]
        price = fang.find('div', class_='content__list--item--main').find('span', class_='content__list--item-price').find('em').get_text()
        date = fang.find('div', class_='content__list--item--main').find('p', class_='content__list--item--brand oneline')\
            .find('span', class_='content__list--item--time oneline').get_text()
        print(title_url, title_name, des_community, price, date)

        # 打开房源页面，获取详细信息
        res_fang = requests.get(title_url, headers=headers)
        res_fang_soup = BeautifulSoup(res_fang.text, 'lxml')
        info = res_fang_soup.find('ul', class_='content__aside__list').find_all('li')
        info_buf = info[0].get_text()
        info_buf = info_buf.split('：')
        info_method = info_buf[1]
        info_buf = info[1].get_text()
        info_buf = re.split('[： ]', info_buf)
        info_style = info_buf[1]
        info_area = info_buf[2]
        if len(info_buf) == 4:
            info_decoration = info_buf[3]
        else:
            info_decoration = ''
        info_buf = info[2].get_text()
        info_buf = re.split('[： /]', info_buf)
        info_direction = info_buf[1]
        info_floor = info_buf[3][0:3]
        print(info_method, info_style, info_area, info_decoration, info_direction, info_floor)

        # 获取房源图片
        title_name = title_name.replace('·', '-')
        img_dir = './img/'+title_name+'/'
        os.makedirs(img_dir, exist_ok=True)
        # 获取图片链接（旧版，获取不到图片）
        # img_buf = res_fang_soup.find('ul', class_='content__article__slide__wrapper').find_all('div', class_='content__article__slide__item')
        # img_cnt = 0
        # for img_url in img_buf:
        #     img_url = img_url.find('img').get('src')
        #     with open(img_dir+str(img_cnt)+'.jpg', 'wb') as f:
        #         f.write(request.urlopen(img_url).read())
        #         f.close()
        #     print(img_url)
        #     img_cnt += 1

        # 获取图片链接（新版）
        img_buf = res_fang_soup.find('ul', class_='content__article__slide--small content__article__slide_dot').find_all('li', class_='')
        # print(img_buf)
        img_cnt = 0
        img_fix = '!m_fill,w_780,h_439,l_fbk,o_auto'
        for img_url in img_buf:
            img_url_buf = img_url.find('img').get('src')
            img_url_buf = img_url_buf.split('!')
            img_url = img_url_buf[0]+img_fix
            with open(img_dir+str(img_cnt)+'.jpg', 'wb') as f:
                try:
                    res = request.urlopen(img_url)
                except:
                    continue
                f.write(res.read())
                f.close()
            img_cnt += 1
        
        # 数据库写入
        # cur = db.cursor()
        # sql = 'INSERT INTO info(url, name, community, price, date, method, style, area, decoration, direction, floor, img_dir) ' \
        #                'VALUES ("%s","%s", "%s",      "%f",  "%s", "%s",   "%s",  "%f", "%s",       "%s",      "%s",  "%s")' % \
        #     (title_url, title_name, des_community, float(price), date, info_method, info_style, float(info_area[:-2]), info_decoration, info_direction, info_floor, img_dir)
        # cur.execute(sql)
        # db.commit()
        # break

        # csv写入
        with open('info.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([title_url, title_name, des_community, price, date, info_method, info_style, info_area, info_decoration, info_direction, info_floor, img_dir])

    time.sleep(1)

for i in range (page_num):
    if i == 0:
        page = ''
    else:
        page = 'pg'+str(i+1)+'/'
    get_bc(page)
