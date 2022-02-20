import sqlite3
import threading

import config as cfg
import ticket
import logs


def get_all_city(user_id):
    global get_all_city_list

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute('select * from city')

    get_all_city_list = {}

    for row in result:
        get_all_city_list[row[1]] = row[2]

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, get_all_city_list)

    print(get_all_city_list)
    return get_all_city_list


def find_id_city(user_id, city):
    global find_id_city_result

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from city where name_en = "{city}"')
    row = cur.fetchone()

    print(row[0])

    find_id_city_result = row[0]

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, find_id_city_result)

    return find_id_city_result


def find_event(user_id, city_id):
    global find_event_list

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from events where city_id = {city_id}')

    find_event_list = {}

    for row in result:
        find_event_list[str(row[0])] = row[1]

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, find_event_list)

    print(find_event_list)
    return find_event_list


def find_type_tickets(user_id, event_id):
    global find_type_tickets_list
    global event_id_

    event_id_ = event_id

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from ticket_type where event_id = {event_id}')

    find_type_tickets_list = {}

    for row in result:
        find_type_tickets_list[str(row[0])] = row[2]

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, find_type_tickets_list)

    print(find_type_tickets_list)
    return find_type_tickets_list


def calculate_price(user_id, id, qty):
    global summ

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from ticket_type where id = {id}')

    for row in result:
        price = row[3]
        count = row[4]

    summ = price * qty

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, summ)

    print(summ)
    return summ


def minus_count_tickets(qty):
    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select count - {qty} from ticket_type')


def create_ticket(qty, user_id, event_id, payment_type, ticket_type):
    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    unique_id = ticket.generate_number_ticket()

    current_time = ticket.current_time()

    loop = 0

    if qty == 1:

        result = cur.execute(
            f'insert into tickets (user_id, event_id, time, unique_id, enter_time, status, purchase_type, ticket_type) '
            f'values ('
            f'{user_id}, '
            f'{event_id}, '
            f'"{current_time}", '
            f'"{unique_id}", '
            f'"", '
            f'"1", '
            f'"{payment_type}", '
            f'"{ticket_type}")')

        con.commit()

        minus_count_tickets(qty)

    else:
        while loop != qty:
            loop += 1

            unique_id = ticket.generate_number_ticket()

            result = cur.execute(
                f'insert into tickets (user_id, event_id, time, unique_id, enter_time, status, purchase_type, ticket_type) '
                f'values ('
                f'{user_id}, '
                f'{event_id}, '
                f'"{current_time}", '
                f'"{unique_id}", '
                f'"", '
                f'"1", '
                f'"{payment_type}", '
                f'"{ticket_type}")')

            con.commit()

        minus_count_tickets(qty)

    func_name = logs.whoami()
    logs.func_logging(user_id, func_name, result)

    print(result)
    return result


def city_by_id(id):
    global city_name

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from city where id = {id}')

    for row in result:
        city_name = row[2]

    return city_name


def event_by_id(id):
    global event_name
    global event_date
    global event_time
    global event_city

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from events where id = {id}')

    for row in result:
        event_name = row[1]
        event_date = row[3]
        event_time = row[4]
        event_city = city_by_id(row[2])

    return event_name


def get_tickets(user_id):
    global tickets_list
    tickets_list = []

    chat_id = user_id

    con = sqlite3.connect(cfg.db)

    cur = threading.local()
    cur = con.cursor()

    result = cur.execute(f'select * from tickets where user_id = {chat_id} and status = 1')

    for row in result:
        event_name_ = event_by_id(row[2])
        unique_id = row[4]

        event_date_ = event_date
        event_time_ = event_time
        event_city_ = event_city

        if row[7] == 'Готівка':
            status = 'Не оплачений'
        else:
            status = 'Оплачений'

        tickets_list.append(
            f'🎉Назва заходу: {event_name_}\n'
            f'🔑Унікальний код: {unique_id}\n'
            f'📅Дата заходу: {event_date_}\n'
            f'⏰Час заходу: {event_time_}\n'
            f'Місто заходу: {event_city_}\n '
            f'Тип квитка: {get_ticket_type(user_id, unique_id)}\n'
            f'🗂Статус квитка: {status}\n\n')

    func_name = logs.whoami()
    logs.func_logging(chat_id, func_name, tickets_list)

    return tickets_list


def get_ticket_type(user_id, unique_id):
    global ticket_type_name

    ticket_type_name = ''

    con = sqlite3.connect(cfg.db)

    cur = con.cursor()

    result = cur.execute(f'select * from tickets where user_id = {user_id} and unique_id = "{unique_id}"')

    for row in result:
        event_id = row[2]
        ticket_type = row[8]

    print(event_id)
    print(ticket_type)

    result_ = cur.execute(f'select * from ticket_type where event_id = {event_id} and id = {ticket_type}')

    for i in result_:
        ticket_type_name = i[2]

    return ticket_type_name

