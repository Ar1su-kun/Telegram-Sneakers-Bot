import telebot
from telebot import types
import sqlite3 as sq
import configparser
import pyimgur
import time
client_id = '1a181eedd6e9b13'

im = pyimgur.Imgur(client_id)

config = configparser.ConfigParser()
config.read("config.ini")

bot = telebot.TeleBot(config["Telegram"]["telegram_bot_token"])

admin_id = config["Telegram"]["admin_id"]

info_msg = '''BIJIS - молодой и развивающийся магазин уличной обуви, основанный в 2021 году, который тесно сотрудничает с проверенными поставщиками. Наша команда собралась представить вам качественную и комфортную обувь по довольно разумной цене среди других популярных магазинов.

Мы хотим сделать наше детище одним из крупнейших интернет-магазинов в России. Просто попробуйте надеть наши кроссовки и вы всё поймете сами. '''
start_msg = 'СТАРТОВОЕ СООБЩЕНИЕ'
brand_select_msg = 'Выберите бренд'

welcome_menu = types.InlineKeyboardMarkup(row_width=2)
reviews_b = types.InlineKeyboardButton('💬 Отзывы', url='https://t.me/bijotsivi')
shop_b = types.InlineKeyboardButton('🛒 Наши товары', callback_data='cb_shop')
info_b = types.InlineKeyboardButton('ℹ️ Информация', callback_data='cb_info')
# search_b = types.InlineKeyboardButton('🔎 Поиск', callback_data='cb_search')
welcome_menu.add(shop_b, row_width=1)
welcome_menu.add(info_b, reviews_b, row_width=2)

terminal_menu = types.InlineKeyboardMarkup(row_width=2)
add_b = types.InlineKeyboardButton('Добавить товар', callback_data='tr_add')
del_b = types.InlineKeyboardButton('Удалить товар', callback_data='tr_del')
red_b = types.InlineKeyboardButton('Редактировать товар', callback_data='tr_red')
not_b = types.InlineKeyboardButton('Написать опповещение', callback_data='tr_not')
terminal_menu.add(add_b, del_b, red_b, not_b)


index=0
while True:
    try:
        with sq.connect('database.db', check_same_thread=False) as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS products(
            id        INTEGER PRIMARY KEY AUTOINCREMENT
                              UNIQUE,
            brand     TEXT    NOT NULL
                              DEFAULT none,
            model     TEXT    NOT NULL
                              DEFAULT none,
            size      TEXT    NOT NULL
                              DEFAULT (0),
            price     TEXT    NOT NULL
                              DEFAULT (0),
            photo_url TEXT    NOT NULL
                              DEFAULT (0) )""")



            @bot.message_handler(commands=['term'])
            def terminal(message):
                        if str(message.from_user.id) == str(admin_id):
                            bot.send_message(message.chat.id, 'Терминал', reply_markup=terminal_menu)
                        else:
                            bot.send_message(message.chat.id, 'У вас недостаточно прав для этого действия.')

            def nterminal(message):
                        if str(message.from_user.id) == str(admin_id):
                            bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                                  text='Терминал',
                                                  reply_markup=terminal_menu)
                        else:
                            bot.send_message(message.message.chat.id, 'Ты как, блять, вообще сюда залез?')

            @bot.message_handler(commands=['start'])
            def start(message):

                        start_call = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        start = types.KeyboardButton('/start')
                        term = types.KeyboardButton('/term')

                        if str(message.from_user.id) == str(admin_id):
                            start_call.add(term, start, row_width=2)
                        else:
                            start_call.add(start)
                        bot.send_message(message.chat.id, f'Приветствую {message.from_user.first_name}', reply_markup=start_call)

                        bot.send_photo(message.chat.id, 'https://imgur.com/17lXEYu', reply_markup=welcome_menu)

            def nstart(message):
                        bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media='https://imgur.com/17lXEYu'), chat_id=message.message.chat.id, message_id=message.message.id, reply_markup=welcome_menu)

            @bot.callback_query_handler(func=lambda message: True)
            def ans(message):
                        if message.data == 'cb_shop':
                            shop_brand(message)
                        elif message.data == 'cb_info':
                            info(message)
                        elif message.data == 'cb_search':
                            bot.send_message(message.message.chat.id, message.data)
                        elif message.data == 'start':
                            nstart(message)
                        elif message.data == 'tr':
                            nterminal(message)
                        elif message.data == 'tr_add':
                            add_product(message)
                        elif message.data == 'tr_red':
                            red_product(message)
                        elif message.data == 'tr_del':
                            del_product(message)
                        elif message.data == 'tr_n_b':
                            add_brand(message)
                        elif len(message.data.split(',')) >= 2:
                            brand_data = message.data.split(',')
                            if brand_data[0] == 'cb_s_b':
                                select_product(message, brand_data)
                            elif brand_data[0] == 'y':
                                buy1(message, brand_data[1])
                            elif brand_data[0] == 'ch_brand':
                                change_data(message, 'brand', brand_data[1])
                            elif brand_data[0] == 'ch_model':
                                change_data(message, 'model', brand_data[1])
                            elif brand_data[0] == 'ch_size':
                                change_data(message, 'size', brand_data[1])
                            elif brand_data[0] == 'ch_price':
                                change_data(message, 'price', brand_data[1])
                            elif brand_data[0] == 'ch_photo':
                                change_data(message, 'photo', brand_data[1])
                            elif brand_data[0] == 'sh_r':
                                global index
                                if index == max_index-1:
                                    index = 0
                                else:
                                    index += 1
                                select_product2(message, brand_data, index)
                            elif brand_data[0] == 'sh_b':
                                buy(message, brand_data[1])
                            elif brand_data[0] == 'sh_l':
                                if index == 0:
                                    index = max_index - 1
                                else:
                                    index -= 1
                                select_product2(message, brand_data, index)
                            elif brand_data[0] == 'tr_s_b':
                                add_product2(message, brand_data)

            def info(message):
                        info_menu = types.InlineKeyboardMarkup(row_width=1)
                        # ref1 = types.InlineKeyboardButton('Ссылка 1', url='https://t.me/+OLtWNdeD-MdhYWIy')
                        # ref2 = types.InlineKeyboardButton('Ссылка 2', url='https://t.me/+OLtWNdeD-MdhYWIy')
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='start')
                        info_menu.add(ex)
                        bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media='https://imgur.com/yN'
                                                                                                  ''
                                                                                                  'AKsGS', caption=info_msg),
                                               chat_id=message.message.chat.id, message_id=message.message.id, reply_markup=info_menu)

            def shop_brand(message):
                        shop_menu = types.InlineKeyboardMarkup(row_width=2)
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='start')
                        cur.execute(f"SELECT brand FROM products")
                        brand = cur.fetchall()
                        brand_sorted = sorted(list(set(brand)))
                        brand_num = len(brand_sorted)
                        if brand_num % 2 == 0:
                            for i in range(brand_num):
                                if i % 2 == 0:
                                    a = types.InlineKeyboardButton(f'{brand_sorted[i][0]}', callback_data=f'cb_s_b,{brand_sorted[i][0]}')
                                    j = i + 1
                                    b = types.InlineKeyboardButton(f'{brand_sorted[j][0]}', callback_data=f'cb_s_b,{brand_sorted[j][0]}')
                                    shop_menu.add(a, b, row_width=2)
                                else:
                                    continue
                        else:
                            for i in range(brand_num):
                                if i == brand_num - 1:
                                    a = types.InlineKeyboardButton(f'{brand_sorted[i][0]}',
                                                                   callback_data=f'cb_s_b,{brand_sorted[i][0]}')
                                    shop_menu.add(a, row_width=1)
                                else:
                                    if i % 2 == 0:
                                        a = types.InlineKeyboardButton(f'{brand_sorted[i][0]}', callback_data=f'cb_s_b,{brand_sorted[i][0]}')
                                        j = i + 1
                                        b = types.InlineKeyboardButton(f'{brand_sorted[j][0]}', callback_data=f'cb_s_b,{brand_sorted[j][0]}')
                                        shop_menu.add(a, b, row_width=2)
                                    else:
                                        continue
                        shop_menu.add(ex)
                        bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media='https://imgur.com/oAn4vLp'),
                                               chat_id=message.message.chat.id, message_id=message.message.id,
                                               reply_markup=shop_menu)

            def select_product(message, brand_data):
                        cur.execute(f'SELECT * FROM products WHERE brand = "{brand_data[1]}"')
                        products_data = cur.fetchall()
                        global max_index
                        max_index = len(products_data)
                        global index
                        index = 0
                        name = products_data[index][2]
                        size = products_data[index][3]
                        price = products_data[index][4]
                        products_num = len(products_data)
                        if products_data[index][5] == '0':
                            foto = 'https://imgur.com/dIrBk2M'
                        else:
                            foto = products_data[index][5]
                        shop_product_menu = types.InlineKeyboardMarkup()
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='cb_shop')
                        right = types.InlineKeyboardButton('Следующий ➡', callback_data=f'sh_r,{brand_data[1]}')
                        left = types.InlineKeyboardButton('⬅ Предыдущий', callback_data=f'sh_l,{brand_data[1]}')
                        buy = types.InlineKeyboardButton('🛒 Купить', callback_data=f'sh_b,{products_data[index][0]}')
                        shop_product_menu.add(left, right, row_width=2)
                        shop_product_menu.add(buy, ex, row_width=1)
                        capt = f'''[{index + 1} из {products_num}]
        
id: {products_data[index][0]}
<b>{brand_data[1]} {name}</b>
        
Цена: {price}₽
        
Размеры в наличии: {size}'''
                        bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media=foto, caption=capt, parse_mode='HTML'),
                                               chat_id=message.message.chat.id, message_id=message.message.message_id, reply_markup=shop_product_menu)


            def select_product2(message, brand_data, ind):
                        cur.execute(f'SELECT * FROM products WHERE brand = "{brand_data[1]}"')
                        products_data = cur.fetchall()
                        name = products_data[index][2]
                        size = products_data[index][3]
                        price = products_data[index][4]
                        products_num = len(products_data)
                        shop_product_menu1 = types.InlineKeyboardMarkup()
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='cb_shop')
                        right = types.InlineKeyboardButton('Следующий ➡', callback_data=f'sh_r,{brand_data[1]}')
                        left = types.InlineKeyboardButton('⬅ Предыдущий', callback_data=f'sh_l,{brand_data[1]}')
                        buy = types.InlineKeyboardButton('🛒 Купить', callback_data=f'sh_b,{products_data[ind][0]}')
                        shop_product_menu1.add(left, right, row_width=2)
                        shop_product_menu1.add(buy, ex, row_width=1)
                        if products_data[index][5] == '0':
                            foto = 'https://imgur.com/dIrBk2M'
                        else:
                            foto = products_data[ind][5]

                        capt = f'''[{ind+1} из {products_num}]
                        
id: {products_data[ind][0]}
<b>{brand_data[1]} {name}</b>
        
Цена: {price}₽
        
Размеры в наличии: {size}
'''
                        bot.edit_message_media(media=telebot.types.InputMedia(type='photo', media=foto, caption=capt, parse_mode='HTML'),
                                               chat_id=message.message.chat.id, message_id=message.message.message_id,
                                               reply_markup=shop_product_menu1)

            def del_product(message):
                        global msg5
                        ex_k = types.InlineKeyboardMarkup()
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='tr')
                        ex_k.add(ex)
                        msg5 = bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                              text='Отправьте id товара, который хотите удалить.', reply_markup=ex_k)
                        bot.register_next_step_handler(msg5, del_product2)

            def del_product2(message):
                        del_product_menu = types.InlineKeyboardMarkup(row_width=1)
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='tr')
                        del_product_menu.add(ex)
                        global msg5
                        bot.delete_message(message.chat.id, message.id)
                        cur.execute(f'SELECT * FROM products WHERE id = {message.text}')
                        productd = cur.fetchall()
                        if len(productd) == 1:
                            with sq.connect('database.db', check_same_thread=False) as con:
                                cur1 = con.cursor()
                                cur1.execute(f'DELETE FROM products WHERE id = {message.text}')
                        bot.edit_message_text(chat_id=message.chat.id, message_id=msg5.id, text=f'Товар удалён', reply_markup=del_product_menu)


            def add_product(message):
                        add_brand_menu = types.InlineKeyboardMarkup(row_width=2)
                        ex = types.InlineKeyboardButton('⬅ Назад', callback_data='tr')
                        add_new_brand = types.InlineKeyboardButton('Добавить новый бренд', callback_data='tr_n_b')
                        add_brand_menu.add(add_new_brand)
                        cur.execute(f"SELECT brand FROM products")
                        brand = cur.fetchall()
                        brand_sorted = sorted(list(set(brand)))
                        brand_num = len(brand_sorted)

                        if brand_num % 2 == 0:
                            for i in range(brand_num):
                                if i % 2 == 0:
                                    a = types.InlineKeyboardButton(f'{brand_sorted[i][0]}',
                                                                   callback_data=f'tr_s_b,{brand_sorted[i][0]}')
                                    j = i + 1
                                    b = types.InlineKeyboardButton(f'{brand_sorted[j][0]}',
                                                                   callback_data=f'tr_s_b,{brand_sorted[j][0]}')
                                    add_brand_menu.add(a, b, row_width=2)
                                else:
                                    continue
                        else:
                            for i in range(brand_num):
                                if i == brand_num - 1:
                                    a = types.InlineKeyboardButton(f'{brand_sorted[i][0]}',
                                                                   callback_data=f'tr_s_b,{brand_sorted[i][0]}')
                                    add_brand_menu.add(a, row_width=1)
                                else:
                                    if i % 2 == 0:
                                        a = types.InlineKeyboardButton(f'{brand_sorted[i][0]}',
                                                                       callback_data=f'tr_s_b,{brand_sorted[i][0]}')
                                        j = i + 1
                                        b = types.InlineKeyboardButton(f'{brand_sorted[j][0]}',
                                                                       callback_data=f'tr_s_b,{brand_sorted[j][0]}')
                                        add_brand_menu.add(a, b, row_width=2)
                                    else:
                                        continue
                        add_brand_menu.add(ex, row_width=1)

                        bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                              text='Выберите бренд товара, который вы хотите добавить.',
                                              reply_markup=add_brand_menu)


            def add_product2(message, brand_data):
                        global bul
                        bul = False
                        global brand_selected
                        brand_selected = brand_data[1]
                        global msg7
                        msg7 = bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                          text=f'''Итак, добавляем новый товар бренда {brand_selected}
Напишите модель товара, размеры и цену на него без символа рубля, разделяя это всё запятыми, пример:
air max skepta,38 39 43 45,6800''')
                        bot.register_next_step_handler(msg7, add_product3)

            def add_product3(message):
                            global brand_selected
                            global product
                            global msg7
                            product = message.text.split(',')
                            print(1)
                            if len(product) == 3:
                                print(2)
                                mes = bot.edit_message_text(chat_id=message.chat.id, message_id=msg7.id,
                                                      text=f'Введённые вами данные: {brand_selected} {product[0]} {product[1]} {product[2]}Р\nТеперь отправите фотографию товара. (напишите no, если не хоите добовлять фото)')
                                bot.register_next_step_handler(mes, add_product4)
                                bot.delete_message(message.chat.id, message.id)
                                print(product)
                            else:
                                bot.send_message(message.chat.id, 'Вы не правильно ввели данные (сликшом много или слишком мало запятых.)')
                                nterminal(message)


            def add_product4(message):
                            global brand_selected
                            global product
                            try:
                                if message.text == 'no':
                                    photo = 'https://imgur.com/dIrBk2M'
                                else:
                                    file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                                    downloaded_file = bot.download_file(file_info.file_path)
                                    with open('img.jpg', 'wb') as new_file:
                                        new_file.write(downloaded_file)
                                    uploaded_img = im.upload_image('img.jpg')
                                    photo = uploaded_img.link

                                with sq.connect('database.db', check_same_thread=False) as con:
                                    cur = con.cursor()
                                    cur.execute(f"""INSERT INTO products (brand,model,size,price,photo_url) VALUES ('{brand_selected}','{product[0]}','{product[1]}','{product[2]}','{photo}')""")
                                    bot.send_message(message.chat.id, 'Фото добавлено')
                            except Exception:
                                bot.send_message(message.chat.id, 'Что-то пошло не так')

            def add_brand(message):
                        global mss
                        mss = bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id, text='Напишите имя нового бренда')
                        bot.register_next_step_handler(mss, add_brand2)

            def add_brand2(message):
                        global bul
                        bul = True
                        global brand_selected
                        brand_selected = message.text
                        global msg7
                        msg7 = bot.edit_message_text(chat_id=mss.chat.id, message_id=mss.id,
                                                    text=f'''Итак, добавляем новый товар бренда {brand_selected}
Напишите модель товара, размеры и цену на него без символа рубля, разделяя это всё запятыми, пример:
air max skepta,38 39 43 45,6800''')
                        bot.register_next_step_handler(msg7, add_product3)


            def red_product(message):
                global msg6
                ex_k = types.InlineKeyboardMarkup()
                ex = types.InlineKeyboardButton('⬅ Назад', callback_data='tr')
                ex_k.add(ex)
                msg6 = bot.edit_message_text(chat_id=message.message.chat.id, message_id=message.message.id,
                                             text='Отправьте id товара, который хотите изменить.', reply_markup=ex_k)
                bot.register_next_step_handler(msg6, red_product2)

            def red_product2(message):
                red_product_menu = types.InlineKeyboardMarkup(row_width=1)
                ex = types.InlineKeyboardButton('⬅ Назад', callback_data='tr')
                red_product_menu.add(ex)
                global msg6
                bot.delete_message(message.chat.id, message.id)
                cur.execute(f'SELECT * FROM products WHERE id = {message.text}')
                productd = cur.fetchall()
                if len(productd) == 1:
                    ch_brand_b = types.InlineKeyboardButton('Брэнд', callback_data=f'ch_brand,{productd[0][0]}')
                    ch_model_b = types.InlineKeyboardButton('Модель', callback_data=f'ch_model,{productd[0][0]}')
                    ch_size = types.InlineKeyboardButton('Размеры', callback_data=f'ch_size,{productd[0][0]}')
                    ch_price_b = types.InlineKeyboardButton('Цену', callback_data=f'ch_price,{productd[0][0]}')
                    ch_photo = types.InlineKeyboardButton('Фото', callback_data=f'ch_photo,{productd[0][0]}')
                    red_product_menu.add(ch_brand_b, ch_model_b, ch_size, ch_price_b, ch_photo)
                    bot.edit_message_text(chat_id=message.chat.id, message_id=msg6.id,
                                          text=f'Выберите пункт, который хотие изменить.', reply_markup=red_product_menu)
                else:
                    bot.edit_message_text(chat_id=message.chat.id, message_id=msg6.id, text=f'Товар не найден',
                                          reply_markup=red_product_menu)

            def change_data(message, st, id):
                global msg6
                global ch_id
                global ms
                global gst
                gst = st
                ch_id = id
                if st == 'photo':
                    ms = bot.edit_message_text(chat_id=message.message.chat.id, message_id=msg6.id,
                                               text=f'Отправьте новое фото, напишите no, если хотите убрать фото:')
                    bot.register_next_step_handler(ms, change_photo)
                else:
                    name = "Хз"
                    if st == 'brand':
                        name = 'Напишите название новго бренда.'
                    if st == 'size':
                        name = 'Напишите новые рамзеры (одним сообщением без запятых)'
                    if st == 'price':
                        name = 'Напишите новую цену (без символа рубля)'
                    if st == 'model':
                        name = 'Напишите новое название модели'
                    ms = bot.edit_message_text(chat_id=message.message.chat.id, message_id=msg6.id,
                                               text=name)
                    bot.register_next_step_handler(ms, change_data2)

            def change_data2(message):
                global ms
                global ch_id
                global gst
                if gst in ('brand', 'size', 'price', 'model'):
                    with sq.connect('database.db', check_same_thread=False) as con2:
                        cur2 = con2.cursor()
                        cur2.execute(f'UPDATE products SET "{gst}" = "{message.text}" WHERE id = "{ch_id}"')
                        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
                        bot.edit_message_text(chat_id=message.chat.id, message_id=ms.id, text ='Данные изменены')
                else:
                    bot.delete_message(chat_id=message.chat.id, message_id=ms.id)
                    nterminal(message)

            def change_photo(message):
                global msg6
                global ch_id
                # try:
                if message.text == 'no':
                        photo = 'https://imgur.com/dIrBk2M'
                else:
                        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                        downloaded_file = bot.download_file(file_info.file_path)
                        with open('img.jpg', 'wb') as new_file:
                            new_file.write(downloaded_file)
                        uploaded_img = im.upload_image('img.jpg')
                        photo = uploaded_img.link
                        bot.edit_message_text(chat_id=message.chat.id, message_id=msg6.id,
                                               text='Фото изменено')
                        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
                with sq.connect('database.db', check_same_thread=False) as con1:
                    cur1 = con1.cursor()
                    cur1.execute(f'UPDATE products SET photo_url = "{photo}" WHERE id = "{ch_id}"')

            def buy(message, id):
                Y_or_N = types.InlineKeyboardMarkup()
                y = types.InlineKeyboardButton('✅ Да', callback_data=f'y,{id}')
                n = types.InlineKeyboardButton('❌ Отмена', callback_data='start')
                Y_or_N.add(y, n)
                cur.execute(f"SELECT * FROM products WHERE id = {id}")
                product = cur.fetchone()
                bot.send_message(message.message.chat.id, f'Вы уверены, что хотите купить товар {product[1]} {product[2]}', reply_markup=Y_or_N)

            def buy1(message, id):
                cur.execute(f"SELECT * FROM products WHERE id = {id}")
                product = cur.fetchone()
                bot.send_message(message.message.chat.id, f'Мы отправили запрос о покупке товара {product[1]} {product[2]} нашему оператору, он свяжется с вами в ближайшее время.')
                bot.send_message(admin_id, f'✅ Пришёл запрос на покупку товара {product[1]} {product[2]} от @{message.from_user.username}')
                with open('log.txt', 'a+') as fl:
                    print(f'Пришёл запрос на покупку товара {product[1]} {product[2]} от @{message.from_user.username} время: {time.ctime(time.time())}', file=fl)



            bot.polling(none_stop=True)

    except Exception:
        continue
        print('Ч-то пошло не так')








        # except Exception:
        #     print("Произошёл неопознаный пиздец")
        #     continue

