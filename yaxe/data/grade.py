import csv
from functools import reduce
from pathlib import Path
from typing import Dict, List


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

    def __init__(self, output="result") -> None:
        with open(Path(output).joinpath("grade.csv"), newline="") as f:
            reader = csv.DictReader(f)
            credit, grade, point, semester = [], [], [], []
            for row in reader:
                credit.append(float(row["学分"]))
                grade.append(float(row["总成绩"]))
                point.append(float(row["绩点"]))
                semester.append(str(row["学期学年"]))
            self.grades = {
                "credit": credit,
                "grade": grade,
                "point": point,
                "semester": semester,
            }
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

    def get_year_based_average_grade(self) -> Dict[str, float]:
        years = [item[:11] for item in self.grades["semester"]]
        grades_yeared = {}.fromkeys(years, 0)
        credits = {}.fromkeys(years, 0)
        points = {}.fromkeys(years, 0)
        years = set(years)

        for grade, point, semester, credit in zip(
            self.grades["grade"],
            self.grades["point"],
            self.grades["semester"],
            self.grades["credit"],
        ):
            grades_yeared[semester[:11]] += grade * credit
            points[semester[:11]] += point * credit
            credits[semester[:11]] += credit

        for year in years:
            grades_yeared[year] /= credits[year]
            points[year] /= credits[year]
        return grades_yeared, points
