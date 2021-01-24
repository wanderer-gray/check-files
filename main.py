#!/usr/bin/python

import db
import os
import json
import sqlite3
import hashlib

def get_config() -> dict:
  with open('config.json') as file:
    return json.load(file)

def watch_add(data: db.DB, path: str) -> None:
  path = os.path.abspath(path)

  if not os.path.exists(path):
    print(f'\tНаблюдаемый файл не найден: {path}')
    return
  
  try:
    watch_id = data.create_watch(path)
  except sqlite3.IntegrityError:
    print(f'\tДублирование наблюдаемых файлов: {path}')
    return
  
  for file_path in get_file_paths(path):
    try:
      file_add(data, watch_id, file_path)
    except sqlite3.IntegrityError:
      print(f'\tДублирование файлов: {file_path}')
    except:
      print(f'\tНе удалось добавить файл: {file_path}')

def watch_remove(data: db.DB, path: str) -> None:
  path = os.path.abspath(path)

  data.delete_watch(path)

def watches_check(data: db.DB) -> None:
  watches = data.select_watch()

  if len(watches) == 0:
    print('\tСписок наблюдаемых файлов пуст')

  for watch in watches:
    watch_check(data, watch)
  
def watch_check(data: db.DB, watch: dict) -> None:
  path = watch['path']
  watch_id = watch['id']

  if not os.path.exists(path):
    print(f'\tНаблюдаемый файл не найден: {path}')
    return

  curr_file_paths = get_file_paths(path)
  prev_files = data.select_file(watch_id)
  
  print('\tДобавленные файлы')
  for add_file_path in get_add_file_paths(curr_file_paths, prev_files):
    print(f'\t\t{add_file_path}')

  print('\tУдалённые файлы')
  for remove_file_path in get_remove_file_paths(curr_file_paths, prev_files):
    print(f'\t\t{remove_file_path}')
  
  print('\tИзменённые файлы')
  for shared_file in get_shared_files(curr_file_paths, prev_files):
    shared_file_path = shared_file['path']

    try:
      check = file_check(shared_file_path, shared_file['hash'])

      if not check:
        print(f'\t\t{shared_file_path}')
    except:
      print(f'\t\tНе удалось проверить файл: {shared_file_path}')

def get_file_paths(path: str) -> list:
  file_paths = list()

  if not os.path.exists(path):
    return file_paths
  
  if os.path.isfile(path):
    file_paths.append(path)

  if os.path.isdir(path):
    for file_path in os.listdir(path):
      file_paths += get_file_paths(os.path.join(path, file_path))

  return file_paths

def get_add_file_paths(curr_file_paths: list, prev_files: list) -> list:
  add_file_paths = list()

  for curr_file_path in curr_file_paths:
    exist = False

    for prev_file in prev_files:
      exist = curr_file_path == prev_file['path']

      if exist:
        break
    
    if not exist:
      add_file_paths.append(curr_file_path)
  
  return add_file_paths

def get_remove_file_paths(curr_file_paths: list, prev_files: list) -> list:
  remove_file_paths = list()

  for prev_file in prev_files:
    exist = False
    prev_file_path = prev_file['path']

    for curr_file_path in curr_file_paths:
      exist = curr_file_path == prev_file_path

      if exist:
        break
    
    if not exist:
      remove_file_paths.append(prev_file_path)
  
  return remove_file_paths

def get_shared_files(curr_file_paths: list, prev_files: list) -> list:
  shared_files = list()

  for prev_file in prev_files:
    exist = False

    for curr_file_path in curr_file_paths:
      exist = curr_file_path == prev_file['path']

      if exist:
        break
    
    if exist:
      shared_files.append(prev_file)

  return shared_files

def file_add(data: db.DB, watch_id: int, file_path: str) -> None:
  file_hash = get_file_hash(file_path)

  data.create_file(watch_id, file_path, file_hash)

def file_check(file_path: str, prev_file_hash: str) -> bool:
  return get_file_hash(file_path) == prev_file_hash

def get_file_hash(file_path: str) -> str:
  BUFFER_SIZE = 65536

  file_hash = hashlib.sha256()

  with open(file_path, 'rb') as file:
    while True:
      buffer = file.read(BUFFER_SIZE)

      if not buffer:
        break

      file_hash.update(buffer)
  
  return file_hash.hexdigest()

def help():
  print("""
Список команд:
\tadd    - добавить наблюдаемый файл;
\tremove - удалить наблюдаемый файл;
\tcheck  - проверить наблюдаемый файл;
\texit   - выйти из программы.
  """)

def main():
  config = get_config()
  data = db.DB(config['db'])

  while True:
    cmd = input('Команда: ')

    if cmd == 'exit':
      break
    elif cmd == 'add':
      watch_add(data, input('\tФайл: '))
    elif cmd == 'remove':
      watch_remove(data, input('\tФайл: '))
    elif cmd == 'check':
      watches_check(data)
    else:
      help()
  
  data.close()

if __name__ == '__main__':
  main()
