"""Regression tests for the sexagenary-day calculation fixed in issue #1."""

import datetime
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "liuyao.py"
SPEC = importlib.util.spec_from_file_location("liuyao", str(SCRIPT_PATH))
liuyao = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(liuyao)


class GanzhiRegressionTests(unittest.TestCase):
    def assert_day(self, day, expected):
        # Fixed expected values are independent of the production offsets.
        self.assertEqual(liuyao.get_ganzhi_today(day), tuple(expected))

    def test_reference_date_is_wu_wu(self):
        self.assert_day(datetime.date(2000, 1, 1), "戊午")

    def test_issue_1_date_is_ji_si(self):
        self.assert_day(datetime.date(2026, 6, 24), "己巳")

    def test_date_before_reference(self):
        self.assert_day(datetime.date(1999, 12, 31), "丁巳")

    def test_leap_day_boundaries(self):
        cases = [
            ((2000, 2, 28), "丙辰"),
            ((2000, 2, 29), "丁巳"),
            ((2000, 3, 1), "戊午"),
            ((2024, 2, 28), "壬戌"),
            ((2024, 2, 29), "癸亥"),
            ((2024, 3, 1), "甲子"),
        ]
        for ymd, expected in cases:
            with self.subTest(date=ymd):
                self.assert_day(datetime.date(*ymd), expected)

    def test_non_leap_century_boundaries(self):
        cases = [
            ((1900, 2, 28), "壬申"),
            ((1900, 3, 1), "癸酉"),
            ((2100, 2, 28), "辛丑"),
            ((2100, 3, 1), "壬寅"),
        ]
        for ymd, expected in cases:
            with self.subTest(date=ymd):
                self.assert_day(datetime.date(*ymd), expected)

    def test_datetime_input(self):
        self.assert_day(datetime.datetime(2000, 1, 1, 12, 0), "戊午")
        self.assert_day(datetime.datetime(2026, 6, 24, 12, 34), "己巳")

    def test_assembly_updates_day_dependent_fields(self):
        result = liuyao.assemble_hexagram(
            [7, 8, 9, 6, 7, 8], dt=datetime.datetime(2026, 6, 24, 12, 0)
        )
        self.assertEqual(result["日干支"], "己巳")
        self.assertEqual(result["空亡"], ("戌", "亥"))
        self.assertEqual(
            [yao["六神"] for yao in result["爻象"]],
            ["螣蛇", "白虎", "玄武", "青龙", "朱雀", "勾陈"],
        )

    def test_cli_date_argument(self):
        output = subprocess.check_output(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--date", "2026-06-24",
                "--coins", "7", "8", "9", "6", "7", "8",
                "--json",
                "--no-save",
            ],
            cwd=str(SCRIPT_PATH.parents[1]),
            universal_newlines=True,
        )
        result = json.loads(output)
        self.assertEqual(result["日干支"], "己巳")
        self.assertEqual(result["空亡"], ["戌", "亥"])
        self.assertEqual(result["爻象"][0]["六神"], "螣蛇")


if __name__ == "__main__":
    unittest.main()
