## Список команд
- `add` [Путь к файлу/папке]
  - Ошибки
    - Наблюдаемый файл не найден
    - Дублирование наблюдаемых файлов
    - Дублирование файлов (файл был добавлен ранее)
    - Не удалось добавить файл (не удалось создать хеш)
- `remove` [Путь к файлу/папке]
  - Примечание: если файл/папка не найдена, то ничего не произойдет
- `check`
  - Ошибки
    - Наблюдаемый файл не найден
    - Не удалось проверить файл (не удалось создать хеш)

## Конфигурация (см. `config.json`)
- `db` - расположение базы данных

## Архитектура базы данных
- Таблицы
  - `watch` наблюдаемый файл/папка
    - id
    - path
  - `file` фиксируемый файл
    - id
    - watch_id
    - path
    - hash
