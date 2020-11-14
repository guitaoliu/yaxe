import csv
import json
from functools import reduce
from pathlib import Path
from typing import Dict, List

from rich.progress import track

from yaxe.login import ehall_login
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
            "grade_rank": int(data["ZRS"]) - int(data["PM"]),
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


class GPACalculator:

    point_convert_table = {
        "basic_4_0": {
            "grade": (90, 80, 70, 60, 0),
            "credit": (4.0, 3.0, 2.0, 1.0, 0.0),
        },
        "improved_4_0_version1": {
            "grade": (85, 70, 60, 0),
            "credit": (4.0, 3.0, 2.0, 0.0),
        },
        "improved_4_0_version2": {
            "grade": (85, 75, 60, 0),
            "credit": (4.0, 3.0, 2.0, 0.0),
        },
        "pku": {
            "grade": (90, 85, 82, 78, 75, 72, 68, 64, 60, 0),
            "credit": (4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.5, 1.0, 0.0),
        },
        "ustc": {
            "grade": (95, 90, 85, 82, 78, 75, 72, 68, 65, 64, 61, 60, 0),
            "credit": (
                4.3,
                4.0,
                3.7,
                3.3,
                3.0,
                2.7,
                2.3,
                2.0,
                1.7,
                1.5,
                1.3,
                1.0,
                0.0,
            ),
        },
        "sjtu": {
            "grade": (95, 90, 85, 75, 70, 67, 65, 62, 60, 0),
            "credit": (4.3, 4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.0, 0.0),
        },
    }

    def __init__(self, data_file="result/grade.csv") -> None:
        with open(data_file, newline="") as f:
            reader = csv.DictReader(f)
            credit, grade, point = [], [], []
            for row in reader:
                credit.append(float(row["学分"]))
                grade.append(float(row["总成绩"]))
                point.append(float(row["绩点"]))
            self.grades = {"credit": credit, "grade": grade, "point": point}
        self.total_credit = reduce(lambda x, y: x + y, self.grades["credit"])
        self.xjtu_gpa = self.get_average(self.grades["point"])
        self.average = self.get_average(self.grades["grade"])

    def get_average(self, points: List[float]):
        total_points = reduce(
            lambda x, y: x + y,
            [x * y for x, y in zip(points, self.grades["credit"])],
        )
        return round(total_points / self.total_credit, 2)

    def calculate(self):
        def get_credit(g, c_table) -> float:
            for grade, credit in zip(c_table["grade"], c_table["credit"]):
                if g >= grade:
                    return credit
            return 0

        result = {}
        for method, c_table in self.point_convert_table.items():
            points = [get_credit(g, c_table) for g in self.grades["grade"]]
            result[method] = self.get_average(points)

        return result

    def get_gpa(self) -> Dict[str, int]:
        return {
            "average": self.average,
            **self.calculate(),
            "xjtu": self.xjtu_gpa,
        }
