import telebot
import os
import threading
import queue
import time
import json
CWD = os.path.realpath(os.path.dirname(__name__))
def Input():
    while(True):
        print("Please enter your valid Telegram bot token. WARNING it will be saved in %s\config.json"%CWD)
        Input = str(input())
        try:
            telebot.TeleBot(Input).get_me()
            print("Token is valid. Program started.")
            break
        except Exception as E:
            print("%s, which means that your token is invalid"%E)
            continue
    bot = telebot.TeleBot(Input)
    return bot, Input
try:
    global bot
    if(os.access(CWD+"\config.json", os.F_OK)):
        print("Detected config. Using it's data")
        with open("{}\{}".format(CWD,"config.json"), "r") as f:
            data = json.load(f)
            token = data["BOT"]
            bot = telebot.TeleBot(token)
        print("Bot started.")
    else:
        print("No access to %s\config.json."%CWD)
        bot, token = Input()
        try:
            with open("{}\{}".format(CWD,"config.json"), "w") as f:
                data = {"BOT":str(token)}
                json.dump(data,f) 
        except Exception as E:
            print("Unable to save, because %s"%E)
except Exception as E:
    print(E)
    bot, token = Input()
    with open("{}\{}".format(CWD,"config.json"), "w") as f:
        data = {"BOT":str(token)}
        json.dump(data,f) 
HOME = "C:/"
PREVIOS_PATH = HOME
CURRENT_PATH = HOME
CHAT_ID = int()
list_of_messages = list()
def Dir(path):
    List = os.listdir(path)
    return List
DIR = Dir(CURRENT_PATH)
KEYWORDS = ("/home", "/back", "/list", "/stop")
eTL = threading.Event()
eTP = threading.Event()
eK = threading.Event()
eStop = threading.Event()
q = queue.Queue()
list_msgs = queue.LifoQueue()
def move(path):
    global PREVIOS_PATH
    global CURRENT_PATH
    global DIR
    PREVIOS_PATH = CURRENT_PATH
    CURRENT_PATH = path
    try:
        os.chdir(CURRENT_PATH)
        DIR = Dir(CURRENT_PATH)
        return True
    except:
        print("bruh")
        return False
def delete():
    print("deleting messages")
    global list_msgs
    if(list_msgs.empty()):
        return
    while(list_msgs.empty()!=True):
        bot.delete_message(CHAT_ID, list_msgs.get())
def send_file(name):
        try:
            file = open('{a}{b}'.format(a=CURRENT_PATH, b=name), 'rb')
            bot.send_document(CHAT_ID, file)
            return True
        except:
            return False
def THRDpick():
        while(1): 
            print("pick thread waiting")
            eTP.wait()
            eTP.clear()
            print("pick thread started")
            message = q.get()
            global KEYWORDS
            if (message.text in KEYWORDS):
                print("in keywords")
                if(message.text == "/back"):
                    global PREVIOS_PATH
                    if(move(PREVIOS_PATH)):
                        bot.send_message(message.chat.id, "Your current directory is: " + CURRENT_PATH)
                if(message.text == "/stop"):
                    print("\nSTOPPING\n")
                    global eStop
                    eStop.set()
                continue
            global DIR
            for every in DIR:
                if(str(message.text) == str(every)):
                    print("in list")
                        
                    DIR = dir(CURRENT_PATH)
                    print("trying to open")
                    if(send_file(message.text)==False):
                        print("failed, trying to go there")
                        move(CURRENT_PATH+message.text+"/")
                    else:
                        print("sent")
                    delete()
            bot.send_message(message.chat.id, "Your current directory is: " + CURRENT_PATH)
            print("pick thread finished")
def THRDlist():
        while(1):
            print("list thread waiting")
            eTL.wait() 
            eTL.clear()
            print("list thread started")
            message = q.get()
            dirlist = Dir(CURRENT_PATH)
            for num in range(len(dirlist)):
                bot.send_message(message.chat.id, dirlist[num])
                if(len(dirlist)>20 and len(dirlist)<50):
                    time.sleep(0.1)
                if(len(dirlist)>50 and len(dirlist)<100):
                    time.sleep(0.15)
                if(len(dirlist)>100):
                    time.sleep(0.2)
                if(eStop.is_set()==True):
                    print("stopping")
                    eStop.clear()
                    break
                global list_msgs
                list_msgs.put_nowait(message.message_id+num+1)
            global CHAT_ID
            CHAT_ID = message.chat.id
            if(list_msgs.qsize()>30):
                bot.send_message(message.chat.id, "{} total".format(list_msgs.qsize()))
                list_msgs.put_nowait(message.message_id+len(dirlist)+2) 
            print("list thread finished")   
t1 = threading.Thread(target=THRDlist, daemon=True)
t1.start()
t2 = threading.Thread(target=THRDpick, daemon=True)
t2.start()
def handler(type, text=None, regexp=None, commands=None):
    if(type=="home"):
        @bot.message_handler(regexp="/home")
        def home(message):
            if(move(HOME)):
                bot.send_message(message.chat.id, "Your current directory is: " + CURRENT_PATH)
            
    if(type=="List"):
        @bot.message_handler(regexp="/list")# триггер 
        def list_messages(message):
            #global Message
            #Message = message
            global q
            q.put(message)
            print("triggered list thread")
            eTL.set()
    if(type=="pick"):
        @bot.message_handler(content_types=["text"])
        def lookup(message):
            #global Message
            #Message = message
            global q
            q.put(message)
            print("triggered pick thread")
            eTP.set()
handler("home")
handler("List")
handler("pick")
bot.polling()   