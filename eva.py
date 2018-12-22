#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from Logincommon import Logincommon
import sys

class Evaluate(Logincommon):

    list_tmp = ['Director', 'Counsellor', 'Dptsecretary']
    list_out_zip = ['evaluationScore', 'ensure', 'teacherStaffId', 'teacherName']

    def getlist(self):
        list_out = []
        for i in self.list_tmp:
            data_url = 'http://eva.gdut.edu.cn/edu{}Controller.do?datagrid&field=id,{}No,{},'.format(i,i,i)
            try:
                a = self._session.get(data_url,  headers=self.HEADER_GET)
            except Exception as e:
                print(e)
                sys.exit()
            dict_out_tmp = {
                'evaluationScore' : '85',
                'ensure' : ''
                }
            dict_out_tmp['teacherName'] = a.json()['rows'][0][i]
            dict_out_tmp['teacherStaffId'] = a.json()['rows'][0][i+'No']
            list_out.append(dict_out_tmp)
        return dict(zip(self.list_tmp, list_out))
    
    def printlist(self):
        list_get = self.getlist()
        print('(打分请控制在 65-95 分)')
        for key,value in list_get.items():
            try:
                score = int(input('请给 {} 打分：\n'.format(value['teacherName'])))
                while score>100 and score<65:
                    score = int(input('输入有误，请重新输入：\n'))
            except:
                score = int(input('输入有误，请重新输入：\n'))
                while score>100 and score<65:
                    score = int(input('输入有误，请重新输入：\n'))
            value['evaluationScore'] =score
        return list_get

    def postnow(self):
        list_get = self.printlist()
        for key,value in list_get.items():
            try:
                status = self._session.post(
                    'http://eva.gdut.edu.cn/EvaluateController.do?do{}Evaluate_submit'.format(key),
                    headers=self.HEADER_POST,
                    data=value
                )
            except Exception as e:
                print(e)
        print('评分完成')


eva = Evaluate('eva')
eva.postnow()