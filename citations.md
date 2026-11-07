# Цитирование и источники корпуса

## Правила цитирования (обязательны)

- Все прямые цитаты — **только из корпуса**: файлы в `txt/` (источники
  публичного достояния). Цитата должна быть дословной; допускается
  нормализация OCR (пробелы/переносы, ё/е, двойные слоги), покрытие
  фрагментом источника ≥ 0.92 (проверяет `tools/verify_quotes.py`).
- Формат цитаты в лекции:
  `> **Цитата:** «...»` и на следующей строке
  `> **Источник:** \`txt/<файл>.txt\` · фрагмент #<номер>`
  (номер фрагмента заполняется по индексу; временно допустимо «фрагмент —»).
- Охраняемые авторским правом тексты (Поппер, Кун, Лакатос, Фейерабенд,
  Витгенштейн, Рассел, Карнап и другие авторы XX в.) **не цитируются**:
  их идеи излагаются авторским синтезом с пометкой «вне корпуса».
- Не включать в корпус современные коммерческие издания.

## Карта «вопрос → источники корпуса» (основные)

Актуальная полная карта, автоматически проверяемая на ≥ 10 источников на
занятие, — `catalog/sources-map.json` (генератор
`build-corpus/build_sources_map.py`). Ниже — основные первоисточники.

| № | Основные источники корпуса |
|---|---|
| 01 | Конт (Позитивная философия; Wikipedia) — наука как институт; Милль (Система логики; On Liberty; Wikipedia) |
| 02 | Конт; Спенсер (Основные начала, Начала этики); Wikipedia (Epistemology, Philosophy of science) |
| 03 | Платон (Государство, Тимей, Теэтет, Пир, Менон; Wikipedia); Лукреций; Аристотель (Категории, Органион); Демокрит/атомизм (Wikipedia); Секст Эмпирик; Пифагореизм (Wikipedia); история математики (Heath: Архимед, Аристарх) |
| 04 | Аристотель: Категории, Этика, Никомахова этика, История животных, О душе, Parva Naturalia, Поэтика, Органион (нем./англ. издания) + Wikipedia |
| 05 | Галилей (Звёздный вестник); Леонардо (Записные книжки, 3 тома); Коперник/Кеплер (Wikipedia); Возрождение (Wikipedia); истории Gebler/Wegg-Prosser о Галилее |
| 06 | Декарт (Рассуждение, Размышления, Правила, Начала); Ньютон (Оптика); Коперник/Кеплер/Галилей (Wikipedia); Научная революция (Wikipedia) |
| 07 | Бэкон (Новый Органон — 3 изд., О достоинстве…, Новая Атлантика); Гоббс (Левиафан — 2 изд.); Локк (Опыт…, Второй трактат, Об управлении разумом, Мысли о воспитании); Рид (Wikipedia); Гоббс/Локк (Wikipedia); `catalog/empiricism-07-sources.json` |
| 08 | Декарт (Рассуждение, Правила, Начала философии, Возражения и ответы); Спиноза (Этика — 3 изд., лат.); Лейбниц (Монадология, Теодицея, Новые опыты, нем. Monadologie; Wundt «Лейбниц») |
| 09 | **Беркли**: Принципы (IA+Gutenberg), Три диалога, Новая теория зрения; **Юм**: Трактат (Gutenberg+SE), Исследование (IA+Gutenberg+SE), Принципы морали, Диалоги о естественной религии, Политические рассуждения; Wikipedia: George Berkeley, Subjective idealism, David Hume, A Treatise of Human Nature, Hume's fork, Bundle theory, Phenomenalism, Sense data, Problem of induction, Causality, Empiricism (en+ru); OA-статьи |
| 10 | Кант: Критика чистого разума (Мюллер + Кемп Смит), Пролегомены, Критика практического разума; Комментарий Кемпа Смита; Wikipedia: Critique of Pure Reason, Synthetic a priori, Transcendental idealism, Phenomenon, Noumenon, Antinomy, Immanuel Kant (en+ru) |
| 11 | Конт (Позитивная философия; Wikipedia en+ru; Law of three stages); Милль (Система логики, О свободе, Утилитаризм; Wikipedia); Спенсер (Основные начала, Начала этики; Wikipedia) |
| 12 | Мах (Анализ ощущений, Механика, Популярные лекции); Пуанкаре (Наука и гипотеза, Основания науки); Лаплас; Рассел; Wikipedia: Classical physics, Old quantum theory, Introduction to quantum mechanics |
| 13 | Мах (3 текста; Wikipedia en+ru); Пуанкаре (2 текста; Wikipedia en+ru); Дюгем (Wikipedia en+ru, Duhem–Quine thesis, Conventionalism) |
| 14 | Рассел (Проблемы философии — 2 изд., Анализ разума — 2 изд.); Витгенштейн (Трактат — 2 изд.; Wikipedia en+ru); Уайтхед (Наука и современный мир — 2 изд., Символизм); Мур (Principia Ethica); Wikipedia: Logical atomism |
| 15 | Юм; Конт; Рассел; Витгенштейн; Шлик (Пространство и время…); Wikipedia: Logical positivism, Vienna Circle (en+ru), Verificationism, Rudolf Carnap, Otto Neurath, Carl Hempel, Analytic–synthetic distinction |
| 16 | Юм (Исследование — проблема индукции); Куайн (Wikipedia, Duhem–Quine); Wikipedia: Karl Popper (en+ru), Falsifiability, Critical rationalism, Demarcation problem, Problem of induction; OA: Falsificationism…, Critical Rationalism and Post Truth, Karl Popper and… |
| 17 | Wikipedia: Thomas Kuhn (en+ru), Paradigm, Paradigm shift, The Structure of Scientific Revolutions, Incommensurability, Scientific revolution; OA-статьи о Куне; Коперник (Wikipedia) |
| 18 | Wikipedia: Imre Lakatos (en+ru), Research programme; OA: Popper et Kuhn…, Lakatosian perspective; Ньютон (Оптика) |
| 19 | Wikipedia: Paul Feyerabend (en+ru), Epistemological anarchism, Against Method; Галилей (Wikipedia, Звёздный вестник); Кеплер/Коперник |
| 20 | Бэкон (4 текста); Милль (Система логики — методы); Дюгем (Wikipedia, Duhem–Quine); Wikipedia: Observation, Experiment, Measurement, Fact; OA-статьи |
| 21 | Пуанкаре (2 текста); Декарт; Уэвелл (Novum Organon Renovatum, История научных идей); Wikipedia: Hypothesis, Scientific theory, Theory-ladenness, Scientific explanation |
| 22 | Бэкон; Декарт (Рассуждение — о методе); Милль (Система логики); Wikipedia: Scientific method (en+ru), Deductive reasoning, Inductive reasoning, Abductive reasoning |
| 23 | Аристотель (корреспондентная — Этика, Категории); Спиноза/Лейбниц (когерентная); Пуанкаре (конвенциональная); Пирс (Chance Love and Logic, Прагматическая теория истины, Фиксация веры, Как делать идеи ясными); Джеймс (Прагматизм — 2 изд., Смысл истины, Воля верить); Wikipedia: Truth (en+ru), все теории истины, Pragmatism, William James, Charles Sanders Peirce; OA: Five Answers on Pragmatism |
| 24 | Лаплас (Опыт…); Юм (причинность); Мах; Wikipedia: Determinism, Causal determinism, Free will, Causality, Quantum indeterminacy, Interpretations of quantum mechanics, Copenhagen interpretation, EPR paradox, Bell's theorem |
| 25 | Ньютон (Оптика); Лейбниц (Монадология, Теодицея); Мах (Механика); Пуанкаре; Wikipedia: Spacetime, Philosophy of space and time, Absolute space and time, Relationalism, Special/General relativity |
| 26 | Декарт (Размышления, Рассуждение); Кант; Wikipedia: Philosophy of artificial intelligence, Philosophy of mind, Chinese room, Functionalism, Philosophical zombie, Turing test, Qualia, Hard problem of consciousness, Physicalism, Epiphenomenalism |

Полный перечень файлов корпуса — в `PROVENANCE.md` (происхождение и
лицензии: публичное достояние + статьи Wikipedia CC BY-SA 4.0) и
`CORPUS.md`; контрольные суммы — в `index-manifest.json`; автоматическая
верификация — `verification/REPORT.md`.