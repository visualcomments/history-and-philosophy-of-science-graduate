#!/usr/bin/env bash
# Самопроверка валидатора курса.
#
# Принцип: проверка, которая не может упасть, — не проверка. Скрипт
# копирует репозиторий, убеждается, что целая копия проходит, затем ломает
# её шестью способами — в том числе так, как был сломан сам курс
# (оборванная вставка цитаты продублировала хвост занятия). Каждая поломка
# обязана быть замечена.
#
# Запуск: bash .github/scripts/selftest.sh
set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

repo="$work/repo"
mkdir -p "$repo"

# Копируем то, что читает валидатор. Копия делается ДО правок: это эталон,
# из которого восстанавливаются файлы между поломками.
tar -C "$src" --exclude=.git --exclude=__pycache__ -cf - . | tar -C "$repo" -xf -

cd "$repo"

restore () {  # вернуть репозиторий в целое состояние
  tar -C "$src" --exclude=.git --exclude=__pycache__ -cf - . | tar -C "$repo" -xf -
}

# ── 1. Целая копия обязана пройти ────────────────────────────────────────
if ! python3 tools/validate_course.py > /dev/null 2>&1; then
  echo "ОШИБКА: нетронутая копия не проходит проверку"
  python3 tools/validate_course.py
  exit 1
fi
echo "нетронутая копия проходит"

fail_if_passes () {
  local name="$1"
  if python3 tools/validate_course.py > /dev/null 2>&1; then
    echo "ОШИБКА: проверка не заметила поломку: $name"
    python3 tools/validate_course.py
    exit 1
  fi
  echo "замечено: $name"
}

# ── 2. Пропавшее занятие ─────────────────────────────────────────────────
rm lectures/17_kun.md
fail_if_passes "пропавшее занятие"
restore

# ── 3. Дублированный раздел (след оборванной вставки) ────────────────────
printf '\n## Задания\n\n- повтор\n' >> lectures/10_kant.md
fail_if_passes "дублированный раздел"
restore

# ── 4. Висячая строка отчёта ─────────────────────────────────────────────
python3 - <<'PY'
from pathlib import Path
p = Path("lectures/16_popper.md")
t = p.read_text(encoding="utf-8")
p.write_text(t.replace("## Задания", "> `verification/REPORT.md`)\n\n## Задания", 1),
             encoding="utf-8")
PY
fail_if_passes "висячая строка отчёта"
restore

# ── 5. Текст корпуса внутри вопросов самопроверки ────────────────────────
# Именно этот дефект был в занятии 09: вставка цитаты уничтожила вопросы.
python3 - <<'PY'
from pathlib import Path
p = Path("lectures/20_empiricheskoe_poznanie.md")
t = p.read_text(encoding="utf-8")
marker = "## Вопросы для самопроверки"
i = t.index(marker) + len(marker)
t = t[:i] + ("\n\n1. Что утверждает имматuOME People are fubject to a "
             "certain delicacy of paffion and adverfity\n") + t[i:]
p.write_text(t, encoding="utf-8")
PY
fail_if_passes "текст корпуса в вопросах"
restore

# ── 6. Битая относительная ссылка ────────────────────────────────────────
printf '\n[битая](lectures/nope.md)\n' >> syllabus.md
fail_if_passes "битая ссылка"
restore

# ── 7. Пропавшая лицензия на контент ─────────────────────────────────────
rm LICENSE-CONTENT.md
fail_if_passes "пропавшая LICENSE-CONTENT.md"
restore

# ── 8. Незаявленный долг по координатам ──────────────────────────────────
printf '\n**Источник:** `x.txt` · фрагмент (номер требует сверки)\n' >> lectures/18_lakatos.md
fail_if_passes "незаявленный долг по координатам"
restore

echo "Самопроверка пройдена: валидатор замечает все семь поломок."
