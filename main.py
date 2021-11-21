from cryptography import fernet
import requests
from datetime import datetime

import telebot
from auth_data import token, Key, host, user, password, db_name
from telebot import types

import psycopg2
from cryptography.fernet import Fernet

import matplotlib.pyplot as plt



print(Key)
def insertinf_conf (chat_id = 1, coin1 = "btc", total_trade_ask = 1, total_trade_bid = 1):
    print(f"""INSERT INTO inf_coin (chatID, namecoin, sell, buy) VALUES
            (PGP_SYM_ENCRYPT('{str(chat_id)}', '{Key}')::text, PGP_SYM_ENCRYPT('{coin1}', '{Key}')::text, PGP_SYM_ENCRYPT('{str(round(total_trade_ask, 2))}', '{Key}')::text, PGP_SYM_ENCRYPT('{str(round(total_trade_bid, 2))}', '{Key}')::text);""")
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO inf_coin (chatID, namecoin, sell, buy) VALUES
            (PGP_SYM_ENCRYPT('{str(chat_id)}', '{Key}')::text, PGP_SYM_ENCRYPT('{coin1}', '{Key}')::text, PGP_SYM_ENCRYPT('{str(round(total_trade_ask, 2))}', '{Key}')::text, PGP_SYM_ENCRYPT('{str(round(total_trade_bid, 2))}', '{Key}')::text);"""
        )

def selectSellinf_conf ():
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT PGP_SYM_DECRYPT(sell::bytea, '{Key}') as sell FROM inf_coin"""
            )
        s = ''
        x_list = []
        for record in cursor:
            s = str(record)
            ss = s.replace("('","")
            sss = ss.replace("',)","")
            x = float(sss)
            x_list.append(x)
    return x_list

def selectBuyinf_conf ():
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT PGP_SYM_DECRYPT(buy::bytea, '{Key}') as buy FROM inf_coin"""
            )
        s = ''
        x_list = []
        for record in cursor:
            s = str(record)
            ss = s.replace("('","")
            sss = ss.replace("',)","")
            x = float(sss)
            x_list.append(x)
    return x_list

def selecXinf_conf ():
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT id FROM inf_coin"""
            )
        s = ''
        x_list = []
        for record in cursor:
            s = str(record)
            ss = s.replace("(","")
            sss = ss.replace(",)","")
            x = int(sss)
            x_list.append(x)
    return x_list
    
    


try:
    # connect to exist database
    connection = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name    
    )
    connection.autocommit = True

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT version();"
        )
        print(f"Server version: {cursor.fetchone()}")
    #create a inf_coin table
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE inf_coin(
                id serial PRIMARY KEY,
                chatid text NOT NULL,
                namecoin text NOT NULL,
                sell text NOT NULL,
                buy text NOT NULL);
                """
        )
except Exception as _ex:
    print("[INFO] Error while working with PostgreSQL", _ex)
finally:
    if connection:
        # cursor.close()
        #connection.close()
        print("[INFO] PostgreSQL connection closed")


def telegram_bot(token):
    bot = telebot.TeleBot(token)
    markup = types.ReplyKeyboardMarkup()
    buttonPrice = types.KeyboardButton('price')
    buttonDepth = types.KeyboardButton('depth')
    buttonTrades = types.KeyboardButton('trades')
    markup.row(buttonPrice,buttonDepth, buttonTrades)
    @bot.message_handler(commands=["start"])
    def start_message(message):
        bot.send_message(message.chat.id, "начнём делать бабки!", reply_markup=markup)
        
    @bot.message_handler(content_types=["text"])
    #@bot.message_handler(commands=['price'])
    def send_text(message):
        if message.text.lower() == "price":
            try:
                #bot.send_message(message.chat.id, введите валюту, стандартно биткоинт(пример ввода btc))
                sell_price = get_price()
                bot.send_message(
                    message.chat.id,
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n средняя цена на аукционе битка(BTC к USD): {round(sell_price, 2)}"
                )
                
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "что-то пошло не поплану"
                )
        elif message.text.lower() == "depth":
            try:
                sell_price = get_depth()
                bot.send_message(
                    message.chat.id,
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n готовых закупить битка на сумму (BTC глубина) : {sell_price}"
                )
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "что-то пошло не поплану"
                )
        elif message.text.lower() == "trades":
            try:
                sell_price = get_trades(chat_id=message.chat.id)
                bot.send_message(
                    message.chat.id,
                    f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\n {sell_price}"
                )
                x_list = selecXinf_conf()
                y1_list = selectSellinf_conf()
                y2_list = selectBuyinf_conf()
                plt.title('trades')
                plt.xlabel('request')
                plt.ylabel('amount')
                plt.plot(x_list, y1_list, label = "Sell", marker = 'o')
                plt.plot(x_list, y2_list, label = "Buy", marker = '^')
                plt.legend()
                plt.savefig('saved_figure.png')
                plt.clf()
                photo = open('saved_figure.png', 'rb')
                bot.send_photo(message.chat.id, photo)
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "что-то пошло не поплану"
                )
        else:
            bot.send_message(message.chat.id, "нет такой команды")
        
    bot.polling()
    
def get_price():
    req = requests.get("https://yobit.net/api/3/ticker/btc_usd")
    response = req.json()
    sell_price = response["btc_usd"]["sell"]
    #print(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell BTC price: {sell_price}")
    return sell_price

def get_info():
    response = requests.get(url="https://yobit.net/api/3/info")
    return response.text

def get_depth(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f"https://yobit.net/api/3/depth/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")
    #Метод возвращает информацию о списках активных ордеров указанных пар.
    bids = response.json()[f"{coin1}_usd"]["bids"] 

    total_bids_amount = 0 #общая сумма поставленых на закуп валюты 
    for item in bids:
        price = item[0]
        coin_amount = item[1]

        total_bids_amount += price * coin_amount

    return f"общая сумма активных ордеров на покупку: {round(total_bids_amount,2)} $"


def get_trades(coin1="btc", coin2="usd", limit=150, chat_id='873804475'):
    response = requests.get(url=f"https://yobit.net/api/3/trades/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")
    #Метод возвращает информацию о последних сделках указанных пар.

    total_trade_ask = 0 #сумма ордеров на продажу валюты 
    total_trade_bid = 0 #сумма ордеров на покупку валюты

    for item in response.json()[f"{coin1}_{coin2}"]:
        if item["type"] == "ask":
            total_trade_ask += item["price"] * item["amount"]
        else:
            total_trade_bid += item["price"] * item["amount"]

    info = f"[-] сумма проданных ордеров {coin1} : {round(total_trade_ask, 2)} $\n[+] сумма купленных ордеров {coin1} : {round(total_trade_bid, 2)} $"
    # insert data into a table
    
    insertinf_conf(chat_id, coin1, total_trade_ask, total_trade_bid)
    '''with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO inf_coin (chatID, namecoin, sell, buy) VALUES
            ({chat_id}, '{coin1}', {round(total_trade_ask, 2)}, {round(total_trade_bid, 2)});"""
        )
    '''
    return info



def main():
    telegram_bot(token)
    connection.close()




if __name__ == '__main__':
    main()
