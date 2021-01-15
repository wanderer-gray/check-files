#!/usr/bin/python

import json
import sqlite3

class DB:
  def __init__(self, path: str) -> None:
    self.__conn = sqlite3.connect(path)
    self.__conn.row_factory = sqlite3.Row
    self.__conn.execute("PRAGMA foreign_keys = ON")

    self.init()

  def init(self) -> None:
    connect = self.__conn
    cursor = connect.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS watch (
      id   INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      path TEXT    NOT NULL UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS file (
      id        INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      watch_id  INT     NOT NULL,
      path      TEXT    NOT NULL UNIQUE,
      hash      TEXT    NOT NULL,
      FOREIGN KEY (watch_id) REFERENCES watch(id) ON DELETE CASCADE
    )
    """)

    connect.commit()
    cursor.close()
  
  def close(self) -> None:
    self.__conn.close()

  def select_watch(self) -> list:
    connect = self.__conn
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM watch")
    rows = cursor.fetchall()

    connect.commit()
    cursor.close()

    return rows
  
  def create_watch(self, watch_path: str) -> int:
    connect = self.__conn
    cursor = connect.cursor()

    cursor.execute("INSERT INTO watch (path) VALUES (?)", (watch_path,))
    id = cursor.lastrowid

    connect.commit()
    cursor.close()

    return id
  
  def delete_watch(self, watch_path: str) -> None:
    connect = self.__conn
    cursor = connect.cursor()

    cursor.execute("DELETE FROM watch WHERE path = ?", (watch_path,))

    connect.commit()
    cursor.close()

  def select_file(self, watch_id: int) -> list:
    connect = self.__conn
    cursor = connect.cursor()

    cursor.execute("SELECT * FROM file WHERE watch_id = ?", (watch_id,))
    rows = cursor.fetchall()

    connect.commit()
    cursor.close()

    return rows

  def create_file(self, watch_id: int, file_path: str, file_hash: str) -> int:
    connect = self.__conn
    cursor = connect.cursor()
    
    cursor.execute("INSERT INTO file (watch_id, path, hash) VALUES (?, ?, ?)", (watch_id, file_path, file_hash,))
    id = cursor.lastrowid

    connect.commit()
    cursor.close()

    return id