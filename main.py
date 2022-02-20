import telebot
from telebot import types
from telebot.types import LabeledPrice

import ast

import config as cfg
import db
import logs
import profile

bot = telebot.TeleBot(cfg.token)

countList = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5'}

# payList = {'cash': 'Готівка', 'card': 'Картка'}
payList = {'cash': 'Готівка'}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    first_name = message.chat.first_name
    last_name = message.chat.last_name
    username = message.chat.username

    global keyboardmain

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    profile_button = types.InlineKeyboardButton(text='📝Профіль', callback_data='profile')
    tickets_button = types.InlineKeyboardButton(text='✉️Білети', callback_data='tickets')
    buy_button = types.InlineKeyboardButton(text='💵Придбати', callback_data='buy')
    help_button = types.InlineKeyboardButton(text='📞Допомога', callback_data='help')
    keyboard.add(profile_button, tickets_button, buy_button, help_button)

    bot.send_message(message.chat.id, 'Головне меню', reply_markup=keyboard)
    profile.first_login(user_id, first_name, last_name, username)

    logs.user_logging(message.chat.id, 'Start command')


@bot.message_handler(commands=['contact'])
def contact(message):
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    reg_button = types.KeyboardButton(text="Номер телефону", request_contact=True)
    keyboard.add(reg_button)

    bot.send_message(message.chat.id, 'Відправте номер телефону', reply_markup=keyboard)

    logs.user_logging(message.chat.id, 'Contact send command')


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    print(message.contact.phone_number)
    profile.add_number(message.chat.id, message.contact.phone_number)

    global keyboardmain
    keyboardmain = types.InlineKeyboardMarkup(row_width=3)
    profile_button = types.InlineKeyboardButton(text='📝Профіль', callback_data='profile')
    tickets_button = types.InlineKeyboardButton(text='✉️Білети', callback_data='tickets')
    buy_button = types.InlineKeyboardButton(text='💵Придбати', callback_data='buy')
    help_button = types.InlineKeyboardButton(text='📞Допомога', callback_data='help')
    keyboardmain.add(profile_button, tickets_button, buy_button, help_button)
    bot.send_message(message.chat.id, 'Головне меню', reply_markup=keyboardmain)

    logs.user_logging(message.chat.id, 'Contact was send ')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data == 'mainmenu':
        keyboardmain = types.InlineKeyboardMarkup(row_width=3)
        profile_button = types.InlineKeyboardButton(text='📝Профіль', callback_data='profile')
        tickets_button = types.InlineKeyboardButton(text='✉️Білети', callback_data='tickets')
        buy_button = types.InlineKeyboardButton(text='💵Придбати', callback_data='buy')
        help_button = types.InlineKeyboardButton(text='📞Допомога', callback_data='help')
        keyboardmain.add(profile_button, tickets_button, buy_button, help_button)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Головне меню',
                              reply_markup=keyboardmain)

        logs.user_logging(call.message.chat.id, 'Main menu')

    elif call.data == 'help':
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Напишіть @concertinuasupport_bot якщо виникнуть питання', reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Help menu')

    elif call.data == 'profile':
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)

        if call.message.chat.last_name is None:
            call.message.chat.last_name = ''

        if call.message.chat.first_name is None:
            call.message.chat.last_name = ''

        number = profile.check_number(call.message.chat.id)

        if len(number) == 0:

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Нема номера телефону, щоб його додати, натисність /contact "
                                       f"\nФамілія: {call.message.chat.first_name}"
                                       f"\nІм'я: {call.message.chat.last_name}"
                                       f"\nНікнейм: {call.message.chat.username}",
                                  reply_markup=keyboard)

        else:
            stat = profile.statistics(call.message.chat.id)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=f"Фамілія: {call.message.chat.first_name}"
                                       f"\nІм'я: {call.message.chat.last_name}"
                                       f"\nНікнейм: {call.message.chat.username}"
                                       f"\nНомер телефону: {profile.check_number(call.message.chat.id)}"
                                       f"\nЗагалом Ви купили {stat[1]} білет(-ів), на сумму {stat[2]}"
                                       f"\nВи зареєстровані в боті вже {stat[3]} дня(-ів)",
                                  reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Profile menu')

    elif call.data == 'tickets':
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)

        tickets = db.get_tickets(call.message.chat.id)

        if len(tickets) == 0:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text='У Вас ще немає білетів', reply_markup=keyboard)
        else:
            text = ''

            for i in tickets:
                text += i

            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                                  reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Tickets menu')

    elif call.data == 'buy':
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        db.get_all_city(call.message.chat.id)

        for key, value in db.get_all_city_list.items():
            keyboard.add(types.InlineKeyboardButton(text=value,
                                                    callback_data="['value', '" + value + "', '" + key + "']"))

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🏡Оберіть місто',
                              reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Buy menu(city choose)')

    elif call.data.startswith("['value'"):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        valueFromCallBack = ast.literal_eval(call.data)[1]
        keyFromCallBack = ast.literal_eval(call.data)[2]

        id_city = db.find_id_city(call.message.chat.id, keyFromCallBack)
        db.find_event(call.message.chat.id, id_city)

        for key, value in db.find_event_list.items():
            keyboard.add(types.InlineKeyboardButton(text=value,
                                                    callback_data="['name', '" + value + "', '" + key + "']"))

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Ви обрали {valueFromCallBack}', reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Buy menu(event choose)')

    elif call.data.startswith("['name'"):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        valueFromCallBack = ast.literal_eval(call.data)[1]
        keyFromCallBack = ast.literal_eval(call.data)[2]

        global event_name
        global event_id

        event_name = ast.literal_eval(call.data)[1]
        event_id = ast.literal_eval(call.data)[2]

        print(event_name)

        db.find_type_tickets(call.message.chat.id, keyFromCallBack)

        for key, value in db.find_type_tickets_list.items():
            keyboard.add(types.InlineKeyboardButton(text=value,
                                                    callback_data="['ticket', '" + value + "', '" + key + "']"))

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Ви обрали {valueFromCallBack}', reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Buy menu(ticket type choose)')

    elif call.data.startswith("['ticket'"):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        valueFromCallBack = ast.literal_eval(call.data)[1]
        # keyFromCallBack = ast.literal_eval(call.data)[2]

        global ticket_type
        global ticket_type_id

        ticket_type = ast.literal_eval(call.data)[1]
        ticket_type_id = ast.literal_eval(call.data)[2]

        for key, value in countList.items():
            keyboard.add(types.InlineKeyboardButton(text=value,
                                                    callback_data="['count', '" + value + "', '" + key + "']"))

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Ви обрали "{valueFromCallBack}" білет', reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Buy menu(ticket count choose)')

    elif call.data.startswith("['count'"):
        global ticket_valueFromCallBack
        global ticket_keyFromCallBack

        keyboard = types.InlineKeyboardMarkup(row_width=1)

        ticket_valueFromCallBack = ast.literal_eval(call.data)[1]
        ticket_keyFromCallBack = ast.literal_eval(call.data)[2]

        print(ticket_valueFromCallBack, '---', ticket_keyFromCallBack)

        db.calculate_price(call.message.chat.id, ticket_type_id, int(ticket_valueFromCallBack))

        for key, value in payList.items():
            keyboard.add(types.InlineKeyboardButton(text=value,
                                                    callback_data="['pay', '" + value + "', '" + key + "']"))

        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f'Ви замовили {ticket_valueFromCallBack} білет(-ів) вартістю {db.summ} '
                                   f'грн. Оберіть спосіб оплати',
                              reply_markup=keyboard)

        logs.user_logging(call.message.chat.id, 'Buy menu(payment method)')

    elif call.data.startswith("['pay'"):
        global pay_valueFromCallBack

        pay_valueFromCallBack = ast.literal_eval(call.data)[1]
        # keyFromCallBack = ast.literal_eval(call.data)[2]

        # prices = [LabeledPrice(label=f"{db.event_name} - {int(ticket_valueFromCallBack)} шт. - {db.ticket_type}",
        # amount=db.summ * 100)]

        global qty
        qty = int(ticket_valueFromCallBack)

        number = profile.check_number(call.message.chat.id)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        backbutton = types.InlineKeyboardButton(text='⬅️Назад', callback_data='mainmenu')
        keyboard.add(backbutton)

        if len(number) == 0:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Додайте спершу свій номер телефону у вкладці "Профіль".',
                                  reply_markup=keyboard)
            logs.user_logging(call.message.chat.id, 'Buy menu(final - no number)')
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f'Вітаємо! Ви придбали щойно білети. З Вами скоро зв"яжеться менеджер',
                                  reply_markup=keyboard)
            db.create_ticket(qty, call.message.chat.id, event_id, pay_valueFromCallBack, ticket_type_id)
            logs.user_logging(call.message.chat.id, 'Buy menu(final - success)')

        # if keyFromCallBack == 'card':

        #    bot.send_invoice(call.message.chat.id,
        #    title=f"{event_name} - {int(ticket_valueFromCallBack)} шт. - {ticket_type}",
        #                 description=' ',
        #                 provider_token=provider_token,
        #                 currency='uah',
        #                 is_flexible=False,  # True If you need to set up Shipping Fee
        #                 prices=prices,
        #                 start_parameter='time-machine-example',
        #                 invoice_payload='HAPPY FRIDAYS COUPON')

        # else:
        #    keyboard = types.InlineKeyboardMarkup(row_width=1)
        #    backbutton = types.InlineKeyboardButton(text='Назад', callback_data='mainmenu')
        #    keyboard.add(backbutton)
        #    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
        #    text=f'horay. you just bought ticket for cash', reply_markup=keyboard)
        #    create_ticket(qty, call.message.chat.id, event_id, pay_valueFromCallBack)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, "
                                                "but we successfully protected your credentials, "
                                                "try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id,
                     'Hoooooray! Thanks for payment! We will proceed your order for `{} {}` as fast as possible! '
                     'Stay in touch.\n\nUse /buy again to get a Time Machine for your friend!'.format(
                         message.successful_payment.total_amount / 100, message.successful_payment.currency),
                     parse_mode='Markdown')

    db.create_ticket(qty, message.chat.id, event_id, pay_valueFromCallBack, ticket_type_id)


# for test
if __name__ == '__main__':
    bot.polling(none_stop=True)

# for production
# while True:
#    try:
#        bot.polling(none_stop=True, interval=0, timeout=0)
#    except:
#        time.sleep(10)
