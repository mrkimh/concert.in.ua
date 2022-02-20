import sqlite3
import inspect

import config as cfg
import ticket


def whoami():
    return inspect.stack()[1][3]
    print(inspect.stack()[1][3])


def user_logging(user_id, log_type):
    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    time = ticket.current_time()

    cur.execute(f'insert into logs (user_id, log_type, time) VALUES ({user_id}, "{log_type}", "{time}")')

    con.commit()


def func_logging(user_id, func_name, result):
    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    time = ticket.current_time()

    cur.execute(f'insert into logs (user_id, log_type, time) VALUES ({user_id}, "Function: {func_name} - {result}", "{time}")')

    con.commit()
