#!/usr/bin/env python3
"""Тесты инструментов курса «История и философия науки».

Запуск без зависимостей:
    python3 tests/test_tools.py

Запуск через pytest:
    pytest tests/test_tools.py

Главный тест здесь — самопроверка валидатора: копия репозитория
намеренно ломается пятью способами и валидатор обязан каждый заметить.
Проверка, которая не может упасть, — не проверка.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "tools" / "validate_course.py"
LECTURES = ROOT / "lectures"
REPORT = ROOT / "verification" / "REPORT.md"

LESSONS = 26
FALL = 13


def run_validator(cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(cwd / "tools" / "validate_course.py"), "--json"],
        capture_output=True, text=True, cwd=cwd,
    )


def copy_repo(dst: Path) -> Path:
    """Copy everything the validator reads.

    Copying only part of the tree makes the validator fail for the wrong
    reason, which would make the self-test meaningless — the intact copy
    must PASS first.
    """
    dst.mkdir(parents=True, exist_ok=True)
    for item in sorted(ROOT.iterdir(), key=lambda p: p.name):
        if item.name in {".git", "__pycache__", ".pytest_cache"}:
            continue
        target = dst / item.name
        if item.is_symlink() and not item.exists():
            continue  # dangling symlink: nothing to copy
        if item.is_dir():
            shutil.copytree(item, target,
                            ignore=shutil.ignore_patterns("__pycache__"),
                            symlinks=True, dirs_exist_ok=True)
        else:
            try:
                shutil.copy2(item, target)
            except (FileNotFoundError, OSError):
                # An ignored, transient file disappeared mid-copy; it is not
                # read by the validator, so skipping it is safe.
                continue
    return dst


class TestCourseStructure(unittest.TestCase):
    """Курс целиком: 26 занятий, два семестра, единая структура."""

    def test_twenty_six_lectures(self):
        found = sorted(LECTURES.glob("[0-9][0-9]_*.md"))
        self.assertEqual(len(found), LESSONS, f"найдено {len(found)}")

    def test_numbering_is_continuous(self):
        nums = sorted(int(p.name[:2]) for p in LECTURES.glob("[0-9][0-9]_*.md"))
        self.assertEqual(nums, list(range(1, LESSONS + 1)))

    def test_semester_split(self):
        nums = sorted(int(p.name[:2]) for p in LECTURES.glob("[0-9][0-9]_*.md"))
        self.assertEqual(len([n for n in nums if n <= FALL]), FALL)
        self.assertEqual(len([n for n in nums if n > FALL]), LESSONS - FALL)

    def test_every_lecture_has_required_sections(self):
        required = ("## Тезис", "## Цели занятия", "## Источники и свидетельства",
                    "## Вопросы для самопроверки", "## Задания")
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            for section in required:
                self.assertIn(section, text, f"{lp.name}: нет {section!r}")

    def test_no_duplicated_sections(self):
        """Повтор раздела — след оборванной вставки цитаты."""
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            heads = re.findall(r"(?m)^## (.+)$", text)
            dupes = {h for h in heads if heads.count(h) > 1}
            self.assertEqual(dupes, set(), f"{lp.name}: дубли разделов {dupes}")

    def test_no_orphaned_report_lines(self):
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            self.assertNotIn("`verification/REPORT.md`)", text,
                             f"{lp.name}: висячая строка отчёта")

    def test_self_check_questions_are_questions(self):
        """Вопросы не должны содержать сырой текст корпуса."""
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            m = re.search(r"## Вопросы для самопроверки(.*?)(?=\n## |\Z)",
                          text, re.S)
            self.assertIsNotNone(m, f"{lp.name}: нет блока вопросов")
            body = m.group(1)
            numbered = [l for l in body.split("\n")
                        if re.match(r"^\d+\.", l.strip())]
            self.assertGreaterEqual(len(numbered), 2,
                                    f"{lp.name}: вопросов {len(numbered)}")
            self.assertIsNone(re.search(r"[a-zA-Z]{25,}", body),
                              f"{lp.name}: в вопросах длинная латинская строка")

    def test_navigation_links_resolve(self):
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            self.assertIn("**Навигация:**", text, f"{lp.name}: нет навигации")
            for target in re.findall(r"\]\(([^)]+)\)", text.split("**Навигация:**")[1]):
                if target.startswith(("http", "#")):
                    continue
                self.assertTrue((lp.parent / target).resolve().exists(),
                                f"{lp.name}: битая ссылка {target}")

    def test_syllabus_links_every_lecture(self):
        text = (ROOT / "syllabus.md").read_text(encoding="utf-8")
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            self.assertIn(lp.name, text, f"syllabus.md не ссылается на {lp.name}")

    def test_syllabus_json_is_valid(self):
        data = json.loads((ROOT / "syllabus.json").read_text(encoding="utf-8"))
        self.assertIsInstance(data, (dict, list))

    def test_goals_are_not_mechanical(self):
        """Цели должны быть содержательными, а не «Объяснять, <обрывок>»."""
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            m = re.search(r"## Цели занятия(.*?)(?=\n## |\Z)", text, re.S)
            self.assertIsNotNone(m, f"{lp.name}: нет целей")
            goals = [l for l in m.group(1).split("\n") if l.strip().startswith("- ")]
            self.assertGreaterEqual(len(goals), 2, f"{lp.name}: целей {len(goals)}")
            for g in goals:
                body = g.strip("- ").strip()
                self.assertGreater(len(body), 25,
                                   f"{lp.name}: слишком короткая цель {body!r}")


class TestCoordinateDebt(unittest.TestCase):
    """Координаты цитат: долг посчитан и совпадает с действительностью."""

    def test_debt_file_exists_and_matches(self):
        debt = json.loads(
            (ROOT / "verification" / "UNRESOLVED-COORDS.json")
            .read_text(encoding="utf-8"))
        actual = 0
        for lp in LECTURES.glob("[0-9][0-9]_*.md"):
            actual += lp.read_text(encoding="utf-8").count("номер требует сверки")
        self.assertEqual(debt["count"], actual,
                         "UNRESOLVED-COORDS.json расходится с занятиями")
        self.assertEqual(len(debt["items"]), actual)

    def test_debt_items_have_source_and_quote(self):
        debt = json.loads(
            (ROOT / "verification" / "UNRESOLVED-COORDS.json")
            .read_text(encoding="utf-8"))
        for item in debt["items"]:
            self.assertTrue(item["source"].startswith(("txt/", "philosophy")),
                            f"подозрительный источник: {item['source']}")
            self.assertTrue((LECTURES / item["lecture"]).is_file())

    def test_coordinates_have_numbers_where_known(self):
        numbered = unresolved = 0
        for lp in LECTURES.glob("[0-9][0-9]_*.md"):
            text = lp.read_text(encoding="utf-8")
            numbered += len(re.findall(r"фрагмент #\d+", text))
            unresolved += text.count("номер требует сверки")
        self.assertGreater(numbered, 0, "ни одной координаты с номером")
        self.assertGreater(numbered, unresolved,
                           "координат без номера больше, чем с номером")


class TestVerificationReport(unittest.TestCase):
    def test_report_exists(self):
        self.assertTrue(REPORT.is_file())

    def test_report_has_no_failures(self):
        text = REPORT.read_text(encoding="utf-8")
        self.assertTrue("неудач: **0**" in text or "неудач: 0" in text,
                        "в отчёте верификации есть неудачи")

    def test_report_covers_all_lectures(self):
        text = REPORT.read_text(encoding="utf-8")
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            self.assertIn(lp.name, text, f"отчёт не упоминает {lp.name}")


class TestLicensing(unittest.TestCase):
    def test_content_license_exists(self):
        self.assertTrue((ROOT / "LICENSE-CONTENT.md").is_file())

    def test_content_license_names_cc_by_sa(self):
        text = (ROOT / "LICENSE-CONTENT.md").read_text(encoding="utf-8")
        self.assertIn("CC BY-SA 4.0", text)

    def test_content_license_separates_code(self):
        text = (ROOT / "LICENSE-CONTENT.md").read_text(encoding="utf-8")
        self.assertIn("GPL-3.0", text)

    def test_code_license_exists(self):
        self.assertTrue((ROOT / "LICENSE").is_file())

    def test_copyrighted_authors_are_outside_corpus(self):
        """Прямых цитат охраняемых авторов быть не должно."""
        guarded = ["Поппер", "Кун", "Лакатос", "Фейерабенд", "Витгенштейн"]
        for lp in sorted(LECTURES.glob("[0-9][0-9]_*.md")):
            text = lp.read_text(encoding="utf-8")
            for author in guarded:
                if author not in text:
                    continue
                # Any quote block attributed to a Wikipedia page on these
                # authors would violate the citation contract.
                for m in re.finditer(r"\*\*Источник:\*\*\s*`([^`]+)`", text):
                    src = m.group(1)
                    self.assertNotIn(
                        author.lower(), src.lower(),
                        f"{lp.name}: цитата из охраняемого источника {src}")


class TestValidatorSelfTest(unittest.TestCase):
    """Валидатор обязан падать на сломанном курсе и проходить на целом."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hps-selftest-"))
        self.repo = copy_repo(self.tmp / "repo")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_intact_copy_passes(self):
        r = run_validator(self.repo)
        self.assertEqual(r.returncode, 0,
                         f"нетронутая копия не прошла:\n{r.stdout}\n{r.stderr}")
        self.assertEqual(json.loads(r.stdout)["problems"], [])

    def _expect_failure(self, needle: str) -> None:
        r = run_validator(self.repo)
        self.assertEqual(r.returncode, 1,
                         f"валидатор не заметил поломку ({needle})")
        problems = json.loads(r.stdout)["problems"]
        self.assertTrue(any(needle in p for p in problems),
                        f"нет проблемы про {needle!r}, есть: {problems}")

    def test_detects_missing_lecture(self):
        (self.repo / "lectures" / "17_kun.md").unlink()
        self._expect_failure("занятие 17")

    def test_detects_duplicated_section(self):
        p = self.repo / "lectures" / "10_kant.md"
        text = p.read_text(encoding="utf-8")
        p.write_text(text + "\n## Задания\n\n- повтор\n", encoding="utf-8")
        self._expect_failure("дублированных разделов")

    def test_detects_orphaned_report_line(self):
        p = self.repo / "lectures" / "16_popper.md"
        text = p.read_text(encoding="utf-8")
        p.write_text(text.replace("## Задания",
                                  "> `verification/REPORT.md`)\n\n## Задания"),
                     encoding="utf-8")
        self._expect_failure("висячих строк")

    def test_detects_broken_link(self):
        p = self.repo / "syllabus.md"
        text = p.read_text(encoding="utf-8")
        p.write_text(text + "\n[битая](lectures/nope.md)\n", encoding="utf-8")
        self._expect_failure("ссылка разрешается")

    def test_detects_missing_content_license(self):
        (self.repo / "LICENSE-CONTENT.md").unlink()
        self._expect_failure("LICENSE-CONTENT.md")

    def test_detects_undeclared_coordinate_debt(self):
        """Незаявленный долг по координатам должен ронять проверку."""
        p = self.repo / "lectures" / "18_lakatos.md"
        text = p.read_text(encoding="utf-8")
        p.write_text(text + "\n**Источник:** `x.txt` · фрагмент (номер требует сверки)\n",
                     encoding="utf-8")
        self._expect_failure("долг по координатам")

    def test_detects_ocr_contamination_in_questions(self):
        """Мусор корпуса внутри блока вопросов должен ронять проверку.

        Именно этот дефект был в занятии 09: вставка цитаты уничтожила
        вопросы и оставила на их месте сырой текст Юма.
        """
        p = self.repo / "lectures" / "20_empiricheskoe_poznanie.md"
        text = p.read_text(encoding="utf-8")
        marker = "## Вопросы для самопроверки"
        idx = text.index(marker) + len(marker)
        injected = ("\n\n1. Что утверждает имматuOME People are fubject to a "
                    "certain delicacy of paffion and adverfity\n")
        p.write_text(text[:idx] + injected + text[idx:], encoding="utf-8")
        self._expect_failure("засорены")


if __name__ == "__main__":
    unittest.main(verbosity=2)
