import sqlite3

import config as cfg
import logs
import ticket

from datetime import datetime


def add_number(user_id, phone):
    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    cur.execute(f'update user set phone = {phone} where id_telegram = {user_id}')

    func_name = logs.whoami()


    con.commit()


def check_number(user_id):
    global check_result

    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    result = cur.execute(f'select * from user where id_telegram = {user_id}')

    for row in result:
        print(row[4])

        check_result = row[4]

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, check_result)

    return check_result


def first_login(user_id, first_name, last_name, username):
    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    cur.execute(f'select count(*) from user where id_telegram = {user_id}')

    row = cur.fetchone()[0]
    con.commit()
    print(row)

    time = ticket.current_time()

    if row == 0:

        cur.execute(
            f'insert into user (id_telegram, first_name, last_name, phone, username, register_time) values ({user_id}, '
            f'"{first_name}", '
            f'"{last_name}", '
            f'"", '
            f'"{username}", '
            f'"{time}")')
        print(cur.rowcount)

        con.commit()

    con.close()

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, 'Success')


def statistics(user_id):
    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    register_date = ''
    ticket_count = 0
    summ_ticket = 0

    list = []
    ticket_type_id = []

    # finding date
    result = cur.execute(f'select * from user where id_telegram = {user_id}')

    for row in result:
        register_date = row[6]
        list.append(register_date)

    # finding count of bought tickets
    cur.execute(f'select count(*) from tickets where user_id = {user_id}')

    cur_result = cur.fetchone()

    ticket_count = cur_result[0]
    list.append(ticket_count)

    # finding summ of ticket
    result = cur.execute(f'select * from tickets where user_id = {user_id}')

    for row in result:
        ticket_type_id.append(row[8])

    for i in ticket_type_id:
        price = cur.execute(f'select * from ticket_type where id = {i}')

        for n in price:
            summ_ticket += n[3]

    list.append(summ_ticket)

    # finding date

    current_time = datetime.strptime(ticket.current_time(), "%m/%d/%Y, %H:%M:%S")

    register_time = cur.execute(f'select * from user where id_telegram = {user_id}')
    for row in register_time:
        register_time = datetime.strptime(row[6], "%m/%d/%Y, %H:%M:%S")

    time = (current_time - register_time).days

    list.append(time)

    return list











