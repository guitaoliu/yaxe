import csv
import json
from pathlib import Path
from typing import List

from rich.progress import track

from yaxe.data.login import ehall_login
from yaxe.utils import get_timestamp

session = ehall_login()


class GradeParser:
    # 最大课程数
    NUM = 999

    def __init__(self) -> None:
        self.session = session
        self.session.get("http://ehall.xjtu.edu.cn/new/index.html?browser=no")
        self.session.get(
            "http://ehall.xjtu.edu.cn/portal/html/select_role.html",
            params={"appId": 4768574631264620},
        )
        resp = self.session.get(
            "http://ehall.xjtu.edu.cn/appMultiGroupEntranceList",
            params={
                "r_t": get_timestamp(),
                "appId": 4768574631264620,
                "param": "",
            },
        )
        data = resp.json()
        target_url = ""
        for group in data["data"]["groupList"]:
            if group["groupName"] == "移动应用学生":
                target_url = group["targetUrl"]
        self.session.get(target_url)

        self.origin_data = self.grade()
        self.courses = self.parse_grade()
        self.course_number = len(self.courses)

    def grade(self) -> List[dict]:
        """获得学生对应的所有学科成绩分析数据

        Args:
            num (int, optional): 最大课程数目. 默认 999.

        Returns:
            dict: 原始学科成绩数据格式
        """

        resp = self.session.post(
            "http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do",
            data={
                "querySetting": [
                    {
                        "name": "SFYX",
                        "caption": "是否有效",
                        "linkOpt": "AND",
                        "builderList": "cbl_m_List",
                        "builder": "m_value_equal",
                        "value": "1",
                        "value_display": "是",
                    }
                ],
                "pageSize": self.NUM,
                "pageNumber": 1,
            },
        )
        grade = resp.json()["datas"]["xscjcx"]["rows"]
        return grade

    def courses_analysis(self, course: str, semester: str, stu: str):
        """这里是成绩分析页面点开单科成绩后的请求，还未做处理，可以进一步分析数据

        Args:
            subject (dict): 查询成绩时得到的一个科目对应的字典
        """
        # 成绩分布
        course_distribution = (
            "http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jxbcjfbcx.do"
        )
        resp = self.session.post(
            course_distribution,
            data={
                "JXBID": course,  # 教学班 ID
                "XNXQDM": semester,  # 学年学期代码
                "TJLX": "01",
                "*order": "+DJDM",
            },
        )
        data = resp.json()["datas"]["jxbcjfbcx"]["rows"]
        course_grade_distribution = [
            {
                "level": item["DJDM_DISPLAY"],
                "numbers": item["DJSL"],
            }
            for item in data
        ]

        # 成绩统计
        course_grade_anl = (
            "http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jxbcjtjcx.do"
        )
        resp = self.session.post(
            course_grade_anl,
            data={
                "JXBID": course,  # 教学班 ID
                "XNXQDM": semester,  # 学年学期代码
                "TJLX": "01",
            },
        )

        data = resp.json()["datas"]["jxbcjtjcx"]["rows"][0]
        course_grade_stats = {
            "ave": data["PJF"],
            "max": data["ZGF"],
            "min": data["ZDF"],
        }

        # 学生排名
        stu_rank = "http://ehall.xjtu.edu.cn/jwapp/sys/cjcx/modules/cjcx/jxbxspmcx.do"
        resp = self.session.post(
            stu_rank,
            data={
                "JXBID": course,  # 教学班 ID
                "XNXQDM": semester,  # 学年学期代码
                "TJLX": "01",
                "XH": stu,
            },
        )
        data = resp.json()["datas"]["jxbxspmcx"]["rows"][0]
        course_stats = {
            "total_numbers": data["ZRS"],
            "grade_rank": data["PM"],
            "class_id": data["JXBID"],
            "class": data["KCH"],
        }

        res = {
            **course_stats,
            **course_grade_stats,
            "distribution": course_grade_distribution,
        }
        return res

    def parse_grade(self, grade=None) -> List[dict]:
        if grade is None:
            grade = self.origin_data
        grades = [
            {
                "课序号": {"display": subject["KXH"]},
                "课程号": {"display": subject["KCH"]},
                "课程名": {"display": subject["KCM"]},
                "学分": {"display": subject["XF"]},
                "总成绩": {"display": subject["ZCJ"]},
                "绩点": {"display": subject["XFJD"]},
                "考试日期": {"display": subject["KSSJ"]},
                "学期学年": {
                    "display": subject["XNXQDM_DISPLAY"],
                    "id": subject["XNXQDM"],
                },
                "学时": {"display": subject["XS"]},
                "课程类别": {
                    "id": subject["KCLBDM"],
                    "display": subject["KCLBDM_DISPLAY"],
                },
                "课程性质": {
                    "id": subject["DJCJLXDM"],
                    "display": subject["DJCJLXDM_DISPLAY"],
                },
                "修读方式": {
                    "id": subject["XDFSDM"],
                    "display": subject["XDFSDM_DISPLAY"],
                },
                "修读类型": {
                    "id": subject["SFZX"],
                    "display": subject["SFZX_DISPLAY"],
                },
                "重修重考": {
                    "id": subject["CXCKDM"],
                    "display": subject["CXCKDM_DISPLAY"],
                },
                "等级成绩类型": {
                    "id": subject["DJCJLXDM"],
                    "display": subject["DJCJLXDM_DISPLAY"],
                },
                "考试类型": {
                    "id": subject["KSLXDM"],
                    "display": subject["KSLXDM_DISPLAY"],
                },
                "开课单位": {
                    "id": subject["KKDWDM"],
                    "display": subject["KKDWDM_DISPLAY"],
                },
                "是否及格": {
                    "id": subject["SFJG"],
                    "display": subject["SFJG_DISPLAY"],
                },
                "是否有效": {
                    "id": subject["SFYX"],
                    "display": subject["SFYX_DISPLAY"],
                },
                "特殊原因": {
                    "id": subject["TSYYDM"],
                    "display": subject["TSYYDM_DISPLAY"],
                },
            }
            for subject in grade
        ]

        return grades

    def save(
        self,
        output="result",
    ):
        output_dir = Path(output)
        fieldnames = list(self.courses[0].keys())
        with open(output_dir.joinpath("grade.csv"), "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for grade in track(self.courses, description="Fetching grades..."):
                writer.writerow({key: val["display"] for key, val in grade.items()})

        with open(output_dir.joinpath("course.json"), "w", encoding="utf8") as f:
            for course in track(
                self.origin_data, description="Fetching courses data..."
            ):
                res = self.courses_analysis(
                    course=course["JXBID"], semester=course["XNXQDM"], stu=course["XH"]
                )
                added_name = {
                    "class_name": course["KCM"],
                    **res,
                }
                f.write(json.dumps(added_name, ensure_ascii=False) + "\n")
