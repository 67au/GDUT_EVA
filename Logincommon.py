#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import os
import json
import getpass
import sys

class Logincommon:

    HEADER_POST = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8'
        }
    HEADER_GET = {
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type' : 'text/html;charset=UTF-8'
        }
    EVA_URL = 'http://eva.gdut.edu.cn/'
    EVA_URL_LOGIN = 'http://eva.gdut.edu.cn/loginController.do?checkuser'
    EVA_URL_CODE = 'http://eva.gdut.edu.cn/randCodeImage'

    def __init__(self, sessionID):
        self.sessionID = sessionID
        self._session = requests.session()
        self.__init_session()

    def __login(self):

        def post_data_build():
            print('使用手动直接登录的方式:')
            try:
                homepage = self._session.get(self.EVA_URL, headers=self.HEADER_GET)
                s = bs(homepage.text, 'lxml').find_all('input')[:4]
                img = self._session.get(self.EVA_URL_CODE, headers=self.HEADER_GET)
                with open('verifycode.jpeg', 'wb+') as f:
                    f.write(img.content)
                print('verifycode.jpeg 已保存在目录中......')
            except Exception as e:
                print(e)
                sys.exit()
            dict_tmp = {i['name']:'' for i in s}
            dict_tmp['userKey'] = s[0]['value']
            dict_tmp['userName'] = input('请输入你的学号:\n')
            dict_tmp['password'] = getpass.getpass('请输入你的登录密码:\n')
            verifycode = input('请输入验证码:\n')
            dict_tmp['randCode'] = verifycode
            return dict_tmp
        
        try:
            post_status = self._session.post(self.EVA_URL_LOGIN, headers=self.HEADER_POST, data=post_data_build())
            if post_status.status_code == '500':
                raise requests.HTTPError('You may be banned by this site')
            ###
            if post_status.json()['msg'] != '操作成功':
                raise Exception('Your username or password may be wrong!')
            ###
            self.__save_cookies(self._session)
            return self._session
        except Exception as e:
            print(e)
            sys.exit()
    
    def __login_status_check(self):
        try:
            soup2 = bs(self._session.get('http://eva.gdut.edu.cn/loginController.do?login', headers=self.HEADER_GET).text, 'lxml')
            return soup2.title.string == '广东工业大学学生工作评价系统'
        except:
            print('error in check!')

    def __save_cookies(self,save_session): #传入参数为requests.session()
        save_session.cookies.set('__jsluid',None)
        if os.path.isfile('cookies-tmp-'+str(self.sessionID)) is not True:
            with open('cookies-tmp-'+str(self.sessionID),'x') as f:
                json.dump(dict(save_session.cookies),f)
        else:
            with open('cookies-tmp-'+str(self.sessionID),'w') as f:
                f.truncate()
                json.dump(dict(save_session.cookies),f)

    def __init_session(self):
        if os.path.isfile('cookies-tmp-'+str(self.sessionID)) is True:
            print('尝试使用缓存的cookies登录......')
            try:
                with open('cookies-tmp-'+str(self.sessionID),'r') as f:
                    requests.utils.add_dict_to_cookiejar(self._session.cookies, json.load(f))
            except:
                os.remove('cookies-tmp-'+str(self.sessionID))
                return self.__login()
            ###
            if self.__login_status_check() is False:
                print('Cookies登录失败，请使用帐号密码登录')
                os.remove('cookies-tmp-'+str(self.sessionID))
                self._session.cookies.clear()
                return self.__login()
            ###
            return self._session
        else:
            return self.__login()