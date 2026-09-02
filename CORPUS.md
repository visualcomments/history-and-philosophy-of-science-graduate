# CORPUS — корпус источников курса

Курс опирается на **верифицированный корпус** философских и научных
текстов **публичного достояния** (классика философии науки: Аристотель,
Бэкон, Декарт, Локк, Беркли, Юм, Кант, Конт, Милль, Спенсер, Мах,
Пуанкаре, Джеймс, Лаплас и др.; смешанный русский/английский). Авторы
XX в. (охраняемые авторским правом) в корпус **не входят** — в занятиях
они излагаются авторским синтезом («вне корпуса»).

Репозиторий содержит карту источников, правила цитирования и отчёт
верификации; сами тексты и RAG-индекс — вне репозитория.

## Раскладка (environments)

```
<FALT_CORPUS_ROOT>/
├── txt/           ← тексты корпуса (UTF-8, *.txt)
├── index/         ← RAG-индекс: annoy.index, embeddings.npy, chunks.jsonl, config.json
└── (scripts/, catalog/ — опционально, инструменты локали)
```

## Установка индекса (Google Диск)

Индекс корпуса распространяется через Google Диск (`docs/GOOGLE-DRIVE.md`):

```bash
make index-fetch URL="<share-ссылка>"   # скачивание + SHA-256 + атомарная установка
make search QUERY="Кант"
make verify                              # проверка цитат
```

Управляется переменными: `FALT_CORPUS_ROOT`, `FALT_TXT_DIR`,
`FALT_INDEX_DIR`, `FALT_REPO_DIR`. Жёстких путей в репозитории нет.

## Источники корпуса (целевой состав)

PD-переводы/оригиналы: Bacon «Novum Organum»; Hobbes «Leviathan»;
Descartes «Discourse on Method»; Spinoza «Ethics»; Leibniz «Monadology»;
Locke «Essay Concerning Human Understanding»; Berkeley «Principles»;
Hume «Enquiry Concerning Human Understanding»; Kant «Critique of Pure
Reason» (перевод Мюллера, 1881); Comte «Positive Philosophy» (Мартино);
Mill «System of Logic»; Spencer «First Principles»; Mach «Analysis of
Sensations» (1914); Poincaré «Science and Hypothesis» (1905); James
«Pragmatism»; Laplace «A Philosophical Essay on Probabilities»; Newton
«Principia» (Motte); Aristotle «Physics»; плюс историко-научные PD-труды
(для вопросов 3–6, 12).

## Лицензионная чистота

- Только публичное достояние и документы, свободные от авторского права.
- Переводы: только PD-переводы (до 1930 г. к публикации / переводчики
  которых умерли давно). Modern (!) переводы в корпус не включаются.
- Появление недопустимых файлов выявляется на этапе верификации и
  чистки индекса.

Детали и контрольные суммы — `docs/GOOGLE-DRIVE.md`, `index-manifest.json`.