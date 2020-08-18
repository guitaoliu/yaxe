import sys
import json
import csv
from abc import abstractmethod
from typing import List

from auth.ehall_login import ehall_login
from utils import get_timestamp

session = ehall_login()


class GradeParser:
    # 最大课程数
    NUM = 999

    def __init__(self) -> None:
        self.grade = self.get_grade()
        self.grade_json = self.parse_grade()
        self.total_subject = len(self.grade_json)

    def get_grade(self) -> List[dict]:
        """获得学生对应的所有学科成绩分析数据

        Args:
            num (int, optional): 最大课程数目. 默认 999.

        Returns:
            dict: 原始学科成绩数据格式
        """
        session.get('http://ehall.xjtu.edu.cn/new/index.html?browser=no')
        session.get(
            'http://ehall.xjtu.edu.cn/portal/html/select_role.html',
            params={
                'appId': 4768574631264620,
            },
        )
        resp = session.get(
            'http://ehall.xjtu.edu.cn/appMultiGroupEntranceList',
            params={
                'r_t': get_timestamp(),
                'appId': 4768574631264620,
                'param': ''
            },
        )
        data = resp.json()
        target_url = ''
        for group in data['data']['groupList']:
            if group['groupName'] == '移动应用学生':
                target_url = group['targetUrl']
        session.get(target_url)
        resp = session.post(
            'http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do',
            data={
                'querySetting': [
                    {"name": "SFYX", "caption": "是否有效", "linkOpt": "AND", "builderList": "cbl_m_List",
                        "builder": "m_value_equal", "value": "1", "value_display": "是"},
                ],
                'pageSize': self.NUM,
                'pageNumber': 1,
            }
        )
        grade = resp.json()['datas']['xscjcx']['rows']
        return grade

    @abstractmethod
    def get_subject_rank(subject: dict):
        """这里是成绩分析页面点开单科成绩后的请求，还未做处理，可以进一步分析数据

        Args:
            subject (dict): 查询成绩时得到的一个科目对应的字典
        """
        # 成绩分布
        class_distribution_anl = 'http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jxbcjfbcx.do'
        req = session.get(
            class_distribution_anl,
            data={
                subject['JXBID'],  # 教学班 ID
                subject['XNXQDM'],  # 学年学期代码
                subject['TJLX'],
            })
        # 成绩统计
        class_grade_anl = 'http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jxbcjtjcx.do'
        req = session.get(
            class_grade_anl,
            data={
                subject['JXBID'],  # 教学班 ID
                subject['XNXQDM'],  # 学年学期代码
                subject['TJLX'],
            })
        # 学生排名
        stu_rank = 'http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jxbxspmcx.do'
        req = session.get(
            stu_rank,
            data={
                subject['JXBID'],  # 教学班 ID
                subject['XNXQDM'],  # 学年学期代码
                subject['TJLX'],
                subject['XH'],  # 学号
            }
        )
        # todo analyse data above

    def parse_grade(self, grade=None) -> List[dict]:
        if grade is None:
            grade = self.grade
        grades = [{
            '课序号': {
                'display': subject['KXH'],
            },
            '课程号': {
                'display': subject['KCH'],
            },
            '课程名': {
                'display': subject['KCM'],
            },
            '学分': {
                'display': subject['XF']
            },
            '总成绩': {
                'display': subject['ZCJ'],
            },
            '绩点': {
                'display': subject['XFJD'],
            },
            '考试日期': {
                'display': subject['KSSJ'],
            },
            '学期学年': {
                'display': subject['XNXQDM_DISPLAY'],
                'id': subject['XNXQDM'],
            },
            '学时': {
                'display': subject['XS'],
            },

            '课程类别': {
                'id': subject['KCLBDM'],
                'display': subject['KCLBDM_DISPLAY'],
            },
            '课程性质': {
                'id': subject['DJCJLXDM'],
                'display': subject['DJCJLXDM_DISPLAY'],
            },
            '修读方式': {
                'id': subject['XDFSDM'],
                'display': subject['XDFSDM_DISPLAY'],
            },
            '修读类型': {
                'id': subject['SFZX'],
                'display': subject['SFZX_DISPLAY'],
            },

            '重修重考': {
                'id': subject['CXCKDM'],
                'display': subject['CXCKDM_DISPLAY'],
            },
            '等级成绩类型': {
                'id': subject['DJCJLXDM'],
                'display': subject['DJCJLXDM_DISPLAY'],
            },
            '考试类型': {
                'id': subject['KSLXDM'],
                'display': subject['KSLXDM_DISPLAY'],
            },
            '开课单位': {
                'id': subject['KKDWDM'],
                'display': subject['KKDWDM_DISPLAY'],
            },
            '是否及格': {
                'id': subject['SFJG'],
                'display': subject['SFJG_DISPLAY'],
            },
            '是否有效': {
                'id': subject['SFYX'],
                'display': subject['SFYX_DISPLAY'],
            },
            '特殊原因': {
                'id': subject['TSYYDM'],
                'display': subject['TSYYDM_DISPLAY']
            },
        } for subject in self.grade]

        return grades

    def save_csv(self, dst='result/grade.csv'):
        fieldnames = list(self.grade_json[0].keys())
        with open(dst, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for grade in self.grade_json:
                writer.writerow({key: val['display']
                                 for key, val in grade.items()})

    def gpa_calculator(self):
        pass
