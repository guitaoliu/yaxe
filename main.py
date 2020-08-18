import os
from pathlib import Path
from core.grade import GradeParser

if __name__ == "__main__":
    if not os.path.exists('result'):
        os.mkdir('result')

    grade = GradeParser()
    grade.save_csv('result/grade.csv')
