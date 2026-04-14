'''
This program requires the following modules:
- python-telegram-bot==22.5
- urllib3==2.6.2
'''
from ChatGPT_HKBU import ChatGPT
gpt = None

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import configparser
import logging
from pymongo.server_api import ServerApi
from pymongo import MongoClient
from bson import InvalidDocument
import os

# 从环境变量获取 MongoDB 连接地址（Docker 内部用服务名访问）
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = os.getenv("MONGO_DB", "chatbot_logs")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "logs")

global logger
global help_string

help_string = '''The functions of this chatbot are as follows. Please enter the corresponding commands to switch.
\help   -View all commands
\QA   -Help answer questions in learning
\event   -Recommend activities as needed
\default   -A helper for university students. 
'''


class MongoDbHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]


    def emit(self, record):
        data = record.__dict__.copy()

        try:
            self.collection.insert_one(data)
        except InvalidDocument:
            data['msg'] = 'err:InvalidDocument'
            data['levelname'] = 'critical'
            self.collection.insert_one(data)

# 配置全局日志
def get_logger(name="chatbot"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()  # 避免重复日志

    # 日志格式
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 添加 MongoDB 处理器
    mongo_handler = MongoDbHandler()
    mongo_handler.setFormatter(formatter)
    logger.addHandler(mongo_handler)

    # 可选：同时输出到控制台（方便调试）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger



def main():
    global logger
    global config
    
    logger = get_logger()
    
    # Load the configuration data from file
    logger.info('INIT: Loading configuration...')
    config = configparser.ConfigParser()
    config.read('config.ini')

    global gpt
    gpt = ChatGPT(config)

    # Create an Application for your bot
    logger.info('INIT: Connecting the Telegram bot...')
    app = ApplicationBuilder().token(config['TELEGRAM']['ACCESS_TOKEN']).build()

    # Register a message handler
    logger.info('INIT: Registering the message handler...')
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback))

    # Start the bot
    logger.info('INIT: Initialization done!')
    app.run_polling()

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # await update.message.reply_text(response)

    global config
    global logger
    global gpt
    global help_string

    try:
        input = update.message.text
        if(input == None or input == ''):
            return
    except:
        return
    
    logger.info("UPDATE: " + input)

    loading_message = await update.message.reply_text('Thinking...')

    if(input.startswith('\\')):
        logger.info('switch to ' + input)   
        if input == '\QA' :      
            gpt = ChatGPT(config, input)
            await loading_message.edit_text('Please enter your question')
        elif input == '\event':         
            gpt = ChatGPT(config, input)
            await loading_message.edit_text('Please enter your request')
        elif input == '\default':         
            gpt = ChatGPT(config, input)
            await loading_message.edit_text('Switched to AI assistant')
        elif input == '\help':
            await loading_message.edit_text(help_string)
        else:
            await loading_message.edit_text('Unknown command'+help_string)
        return
    
    
    logger.info("Call gpt:" + input)



    # send the user message to the ChatGPT client
    response = gpt.submit(input)

    # send the response to the Telegram box client
    await loading_message.edit_text(response)

'''async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("UPDATE: " + str(update))

    # send the echo back to the client
    text = update.message.text.upper()
    await update.message.reply_text(text)'''

if __name__ == '__main__':
    main()
