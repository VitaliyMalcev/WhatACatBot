
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
from keras.models import load_model
import cv2
import numpy as np

model = load_model('model.h5') # https://www.kaggle.com/vitaliymalcev/my-pet-project


breeds = { "1": "Abyssinian", "2":"Bengal", "3":"Birman", "4":"Bombay","5":"British Shorthair", "6":"Egyptian Mau", "7":"Maine Coon","8":"Persian", "9":"Ragdoll","10":"Russian Blue", "11":"Siamese","12":"Sphynx"}
indices = ['1', '10', '11', '12', '2', '3', '4', '5', '6', '7', '8', '9']
final_breed = []
for i in indices:
    final_breed.append(breeds.get(i))

def predict_breed(image):
    img = cv2.imread(image)
    img = cv2.resize(img,(350,350))
    img = np.reshape(img,[1,350,350,3])
    img = img/255.
    result = model.predict([img])
    return sorted(zip(result[0], final_breed), reverse=True)[:3]


bot = telebot.TeleBot(token_name) #token name

@bot.message_handler(commands=["start"])
def handle_start(message):
    #print("нажали старт")
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("INFO")
    bot.send_message(message.from_user.id,'Отправляйте боту фото вашего кота что бы определить его породу. Впрочем, можете отправить и свое фото что бы узнать какой породы кошкой вы могли бы быть. Точность 83% из 12 пород кошек. {}'.format(final_breed), reply_markup=user_markup)

@bot.message_handler(content_types=["text"])
def handle_command(message):
    #print("пришло сообщение",message.text)
    if message.text == "INFO":
        bot.send_message(message.from_user.id,'Здравствуйте! Отправляйте боту фото вашего кота что бы определить его породу. Впрочем, можете отправить и свое фото что бы узнать какой породы кошкой вы могли бы быть. Точность 83% из 12 пород кошек. {}'.format(final_breed))

@bot.message_handler(content_types=["photo"])
def handle_command(message):
    #print("отправили фото")
    try:
        raw = message.photo[2].file_id
        name = raw + ".jpg"
        file_info = bot.get_file(raw)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(name,'wb') as new_file:
                new_file.write(downloaded_file)
        img = open(name, 'rb')
        print(predict_breed(name))
        bot.send_message(message.from_user.id,
                         "*{name} {last}*, фото получено идет обработка".format(name=message.chat.first_name, last=message.chat.last_name),
                         parse_mode="Markdown")  # от кого идет сообщение и его содержание
        bot.send_photo(123286860, img)
        print(message.from_user.id)
        bot.send_message(message.chat.id,
                         "*{name}!*\n\n На фото: {breed}".format(name=message.chat.first_name, last=message.chat.last_name,
                                                               text=message.text, breed=predict_breed(name)),
                         parse_mode="Markdown")  # то что пойдет юзеру после отправки сообщения
    except:
        bot.send_message(message.from_user.id,
                         "Ошибка, попробуйте фото другого размера.")
        

bot.polling(none_stop=True, interval=0)