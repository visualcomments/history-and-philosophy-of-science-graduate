# Индекс и эмбеддинги на Google Диске

Индекс корпуса курса «История и философия науки» (Annoy + эмбеддинги +
чанки) распространяется как **файлы на Google Диске**: репозиторий
самодостаточен. Агент или пользователь скачивает архив по ссылке,
инструмент проверяет SHA-256 и разворачивает индекс в локальный корпус
(`COURSE_CORPUS_ROOT/index/`), после чего работают `make search`,
`make verify` и локальный RAG-API.

## Состав архива

Один архив — **`grad-index-2026-09-13.zip`** (84 122 726 байт, 80,2 МБ):

| Файл | Размер | SHA-256 |
|---|---|---|
| `annoy.index` | 43 523 568 Б | `AFE333CB…F51186A4` |
| `chunks.jsonl` | 35 048 961 Б | `2A8AC087…DE3D9E3B` |
| `embeddings.npy` | 38 013 056 Б | `236848F8…278CE8D8` |
| `config.json` | 4 912 Б | `C506EB9C…6ABC08D9` |

`SHA-256` архива: `7C812F637A2282CB9E07DBF21D77A0440F8FBBCE380DC31DBEE27DF2D2636903`.
Точные значения — в `index-manifest.json`.

Индекс покрывает **98 файлов корпуса, 24 748 чанков** (модель
`paraphrase-multilingual-MiniLM-L12-v2`, 384 измерения, чанк 512/128 — как
и раньше для этого курса). Состав: 29 первоисточников общественного
достояния, 54 статьи Wikipedia (CC BY-SA 4.0), 15 научных статей под
CC-лицензиями.

**Где лежит:** папка `courses-indexes` на Google Диске. Прямая ссылка уже
вписана в `index-manifest.json` (`archive.url`) — достаточно
`make corpus-fetch` без параметров. Просмотр файла:
`https://drive.google.com/file/d/1ybX7Ls_EPnAvMTHwGehB8lTz6ILVc_x4/view`.

**Покрытие индексом проверено.** Для длинного источника
(`philosophy__Bacon_Novum_Organum.txt`, 885 тыс. знаков) все 200 случайных
60-символьных окон присутствуют в чанках — 100 % текста представлено.
Число чанков на файл меньше, чем в прежней сборке, потому что текст режется
по границам предложений, а не механически каждые 512 знаков; пробелов в
покрытии при этом нет.

**Сквозная проверка (2026-09-13).** `tools/corpus_fetch.py --index-only` по
ссылке из манифеста: SHA-256 подтверждена, индекс установлен,
`chunks: 24748, files: 98`.

## Как выложить и подключить

1. Соберите архив из `COURSE_CORPUS_ROOT/index/` (например,
   `Compress-Archive -Path index\annoy.index, index\chunks.jsonl, index\config.json, index\embeddings.npy -DestinationPath course-index-graduate-<дата>.zip`),
   посчитайте SHA-256 каждого файла и архива.
2. Загрузите архив на Google Диск; общий доступ: **«Все, у кого есть
   ссылка» → «Читатель»**.
3. Скопируйте share-ссылку и подключите индекс:
   ```bash
   make index-fetch URL="https://drive.google.com/file/d/FILE_ID/view?usp=sharing"
   # или
   export COURSE_INDEX_URL="https://drive.google.com/file/d/FILE_ID/view?usp=sharing"
   make index-fetch
   ```
4. Инструмент `tools/index_fetch.py` скачает архив, проверит SHA-256
   (по `index-manifest.json`, если заполнен), распакует и атомарно
   заменит `COURSE_CORPUS_ROOT/index/`.

После развёртывания: `make search QUERY="..."`, `make verify`,
`make serve` — как с любым локальным корпусом.

## Обновление индекса

```bash
# 1. Пересобрать индекс и собрать архив из index/ (4 файла в корне архива)
# 2. Посчитать SHA-256 архива и каждого файла
# 3. Залить на Диск (OAuth от личного аккаунта):
rclone copy grad-index-<дата>.zip gdrive:courses-indexes/
rclone link gdrive:courses-indexes/grad-index-<дата>.zip     # публичная ссылка
# 4. Обновить index-manifest.json (filename, size_bytes, sha256, url) и закоммитить
```

- `make corpus-fetch` сверяет сумму с манифестом; при несовпадении
  распаковка не производится (защита от повреждённой загрузки).

**Кто может загружать.** Сервисный аккаунт Google **не может** создавать
файлы (`403 Service Accounts do not have storage quota`, квота 0), а
API-ключ не может писать (`401: API keys are not supported by this API`).
Работает OAuth от личного аккаунта (rclone) либо ручная загрузка в браузере.
Выдача сервисному аккаунту прав «Редактор» на папку проблему **не решает**:
квота считается по создателю файла.

**Проверка после заливки обязательна:** прогнать
`python tools/corpus_fetch.py --index-only` — он проходит форму подтверждения
Google и сверяет SHA-256 (именно так будет скачивать студент).

## Переменные окружения

- `COURSE_CORPUS_ROOT` — корень корпуса (`txt/`, `index/`);
- `COURSE_INDEX_URL` — ссылка на архив (альтернатива `--url`/манифеста);
- `COURSE_TXT_DIR`, `COURSE_INDEX_DIR`, `COURSE_REPO_DIR` — переопределения
  каталогов корпуса и репозитория.