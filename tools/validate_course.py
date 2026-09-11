#!/usr/bin/env python3
"""Проверка целостности курса «История и философия науки».

Курс — это 26 занятий, каждое из которых раскрывает один экзаменационный
вопрос. Скрипт следит за тем, чтобы связи между занятиями, программой и
корпусом не распадались, а структура занятий оставалась единообразной.

Отдельно проверяется то, что было повреждено в этом репозитории:
оборванные вставки цитат (дублированные разделы, висячие строки отчёта)
и координаты фрагментов без номера.

Запуск:
    python3 tools/validate_course.py [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LECTURES = ROOT / "lectures"
SYLLABUS_MD = ROOT / "syllabus.md"
SYLLABUS_JSON = ROOT / "syllabus.json"

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
LESSONS = 26
FALL = 13  # занятия 01–13 — осенний семестр

REQUIRED_SECTIONS = (
    "## Тезис",
    "## Цели занятия",
    "## Источники и свидетельства",
    "## Вопросы для самопроверки",
    "## Задания",
)

problems: list[str] = []
checks_run = 0


def check(name: str, condition: bool, message: str) -> None:
    global checks_run
    checks_run += 1
    if not condition:
        problems.append(f"{name}: {message}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="машиночитаемый вывод")
    args = parser.parse_args()

    check("syllabus.md существует", SYLLABUS_MD.is_file(), "файл отсутствует")
    check("syllabus.json существует", SYLLABUS_JSON.is_file(), "файл отсутствует")

    syllabus_text = SYLLABUS_MD.read_text(encoding="utf-8") if SYLLABUS_MD.is_file() else ""
    if SYLLABUS_JSON.is_file():
        try:
            json.loads(SYLLABUS_JSON.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"syllabus.json не является корректным JSON: {e}")

    # ── каждое занятие существует и достижимо из программы ────────────────
    lecture_files: list[Path] = []
    for n in range(1, LESSONS + 1):
        matches = sorted(LECTURES.glob(f"{n:02d}_*.md"))
        check(f"занятие {n:02d} существует", len(matches) == 1,
              f"найдено файлов: {len(matches)}")
        if not matches:
            continue
        lecture_files.append(matches[0])
        check(f"занятие {n:02d} связано с программой",
              matches[0].name in syllabus_text,
              f"{matches[0].name} не упоминается в syllabus.md")

    check("занятий ровно 26", len(lecture_files) == LESSONS,
          f"найдено {len(lecture_files)}")

    fall = [p for p in lecture_files if int(p.name[:2]) <= FALL]
    spring = [p for p in lecture_files if int(p.name[:2]) > FALL]
    check("осенний семестр — 13 занятий", len(fall) == FALL, f"найдено {len(fall)}")
    check("весенний семестр — 13 занятий", len(spring) == LESSONS - FALL,
          f"найдено {len(spring)}")

    # ── структура занятия ─────────────────────────────────────────────────
    for lp in lecture_files:
        text = lp.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            check(f"{lp.name} содержит {section!r}", section in text,
                  f"отсутствует раздел {section!r}")
        check(f"{lp.name} имеет навигацию", "**Навигация:**" in text,
              "нет блока навигации")

        # Заголовки разделов не должны повторяться: повтор — признак
        # оборванной вставки, при которой хвост файла продублирован.
        heads = re.findall(r"(?m)^## (.+)$", text)
        dupes = sorted({h for h in heads if heads.count(h) > 1})
        check(f"{lp.name} не содержит дублированных разделов", not dupes,
              f"повторяются: {dupes}")

        # Висячая строка, оставшаяся от неудачной вставки отчёта.
        check(f"{lp.name} не содержит висячих строк отчёта",
              "`verification/REPORT.md`)" not in text,
              "найдена строка вида '> `verification/REPORT.md`)'")

        # Вопросы самопроверки должны быть настоящими вопросами, а не
        # сырым текстом корпуса, попавшим туда при вставке.
        m = re.search(r"## Вопросы для самопроверки(.*?)(?=\n## |\Z)", text, re.S)
        if m:
            body = m.group(1)
            numbered = [l for l in body.split("\n") if re.match(r"^\d+\.", l.strip())]
            check(f"{lp.name} содержит вопросы для самопроверки", len(numbered) >= 2,
                  f"найдено пунктов: {len(numbered)}")

            # Так выглядит след вставки цитаты: в блок вопросов попадает
            # текст корпуса. Ловится по длинным латинским фрагментам и по
            # характерным для сканированных текстов XVIII–XIX вв. формам
            # («long s», устаревшие лигатуры, склейки переносов).
            ocr_markers = (
                re.search(r"[a-zA-Z]{25,}", body),          # длинная строка
                re.search(r"\b\w*(?:fubject|paffion|adverfity|"
                          r"fenfible|meafure|conclufion)\w*\b", body),
                re.search(r"[A-Za-z]{3,}\s+[A-Za-z]{3,}\s+[A-Za-z]{3,}\s+"
                          r"[A-Za-z]{3,}\s+[A-Za-z]{3,}", body),
                re.search(r"\bf\w{2,}(?:ion|ing)\b", body),  # f + long-s слова
            )
            check(f"{lp.name}: вопросы не засорены текстом корпуса",
                  not any(ocr_markers),
                  "в вопросах найден фрагмент текста корпуса (OCR)")

    # ── координаты цитат ──────────────────────────────────────────────────
    # Контракт курса требует «файл · фрагмент #N». Часть координат была
    # утеряна при вставке цитат и восстановлена из отчёта верификации;
    # остальные свести не с чем, поэтому они перечислены в
    # verification/UNRESOLVED-COORDS.json. Долг допустим, но обязан быть
    # посчитан: незаявленное расхождение — ошибка, заявленное — нет.
    debt_file = ROOT / "verification" / "UNRESOLVED-COORDS.json"
    declared = 0
    if debt_file.is_file():
        try:
            declared = int(json.loads(debt_file.read_text(encoding="utf-8"))["count"])
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            problems.append(f"UNRESOLVED-COORDS.json нечитаем: {e}")

    total_coords = unresolved = 0
    for lp in lecture_files:
        text = lp.read_text(encoding="utf-8")
        total_coords += len(re.findall(r"\*\*Источник:\*\*", text))
        unresolved += len(re.findall(r"номер требует сверки", text))

    check("долг по координатам заявлен полностью", unresolved == declared,
          f"в занятиях {unresolved} пометок, в UNRESOLVED-COORDS.json {declared}")

    # ── ссылки разрешаются ────────────────────────────────────────────────
    docs = [SYLLABUS_MD] + lecture_files
    docs += sorted((ROOT / "docs").glob("*.md"))
    docs += sorted((ROOT / "verification").glob("*.md"))
    total_links = 0
    for md in docs:
        if not md.is_file():
            continue
        for m in LINK_RE.finditer(md.read_text(encoding="utf-8", errors="replace")):
            target = m.group(2).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            total_links += 1
            check("ссылка разрешается", (md.parent / target).resolve().exists(),
                  f"{md.relative_to(ROOT)} -> {target}")

    # ── опорные документы ─────────────────────────────────────────────────
    for rel in ("CORPUS.md", "PROVENANCE.md", "citations.md", "AGENTS.md",
                "LICENSE", "LICENSE-CONTENT.md", "verification/REPORT.md"):
        check(f"{rel} существует", (ROOT / rel).is_file(), "файл отсутствует")

    # ── отчёт верификации ─────────────────────────────────────────────────
    report = ROOT / "verification" / "REPORT.md"
    if report.is_file():
        text = report.read_text(encoding="utf-8")
        check("отчёт верификации не содержит неудач",
              "неудач: **0**" in text or "неудач: 0" in text,
              "есть неудачные цитаты")
        check("отчёт верификации содержит таблицу цитат",
              "| Лекция |" in text, "нет таблицы цитат")

    if args.json:
        print(json.dumps({
            "checks_run": checks_run,
            "problems": problems,
            "relative_links_checked": total_links,
            "lectures": len(lecture_files),
            "fall": len(fall),
            "spring": len(spring),
            "coords_with_number": total_coords - unresolved,
            "coords_unresolved": unresolved,
            "ok": not problems,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"Проверка курса: {checks_run} проверок, "
              f"{total_links} относительных ссылок, занятий {len(lecture_files)} "
              f"({len(fall)} осень + {len(spring)} весна)")
        print(f"Координаты цитат: {total_coords - unresolved} с номером, "
              f"{unresolved} требуют сверки")
        if problems:
            print(f"\nПроблем: {len(problems)}")
            for p in problems:
                print(f"  - {p}")
        else:
            print("Все проверки пройдены.")

    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
