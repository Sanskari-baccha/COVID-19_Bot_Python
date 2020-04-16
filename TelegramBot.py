import os
from telegram.ext import Updater, CommandHandler
import requests
from pandas import json_normalize

START_TEXT = 'Hello there. Type /help to get list of supported commands'
ABOUT_TEXT = 'COVID-19 Bot made by Leela Manikanta.\n Linkdin profile https://www.linkedin.com/in/leela-manikanta-siraparapu/'
HELP_TEXT = """
List of available commands:
/help - Get list of available commands.
/about - About the bot.
/state <State Name>- To get covid-19 cases count state wide.
/dist_of <State Name> - To get covid-19 cases  count district wide in the given state.
/Cases_India - To get covid-19 cases cases count in India.
/advisory - Suggests Do's and Don'ts to prevent COVID-19 from spreading.
"""
ADVISORY = """
Do's\n
----------------------------------------------------------
Practice frequent hand washing. Wash hands with soap and water or use alcohol based hand rub. Wash hands even if they are visibly clean.\n
Cover your nose and mouth with handkerchief or tissue while sneezing and coughing.\n
Throw used tissues into closed bins immediately after use.\n
See a doctor if you feel unwell(fever, difficult breathing and cough). While visiting doctor wear a mask/cloth to cover your mouth and nose.\n
If you have these signs/symptoms please call State helpline number or Ministry of Health & Family Welfare’s 24X7 helpline at 011-23978046.\n
Avoid participating in large gatherings.\n

Don'ts\n
-------------------------------------------------------------
Have a close contact with anyone, if you’re experiencing cough and fever.\n
Touch your eyes,nose and mouth.\n
Spit in public.\n
"""


def start(update, context):
    update.message.reply_text(START_TEXT)


def about(update, context):
    update.message.reply_text(ABOUT_TEXT)


def get_help(update, context):
    update.message.reply_text(HELP_TEXT)

def advisory(update, context):
    update.message.reply_text(ADVISORY)


def state_wide(update, context):
    user_input = " ".join(context.args)
    if user_input != "":
        state = 'https://api.covid19india.org/data.json'
        state = requests.get(state)
        state = state.json()
        state_wise = json_normalize(data=state, record_path='statewise')
        state_wise = state_wise[['active', 'confirmed', 'deaths', 'recovered', 'lastupdatedtime', 'state']]
        state_wise = state_wise.set_index('state')
        user_input = user_input.title().strip()
        try:
            tabel = ""
            tabel += user_input + ' COVID-19 report' + '\n'
            tabel += '-' * 60 + '\n'
            for i in range(len(state_wise.loc[[user_input]].values[0])):
                tabel += str(state_wise.loc[user_input].index[i]).title() + " : " + str(
                    state_wise.loc[user_input].values[i]) + '\n'
            update.message.reply_text(tabel, parse_mode='Markdown')
        except:
            update.message.reply_text("Invalid State name.Check the valid names from 'www.covid19india.org'")
    else:
        update.message.reply_text("State name should not be empty.Try /dist Kerala")


def Country_wide(update, context):
    state = 'https://api.covid19india.org/data.json'
    state = requests.get(state)
    state = state.json()
    state_wise = json_normalize(data=state, record_path='statewise')
    state_wise = state_wise[['active', 'confirmed', 'deaths', 'recovered', 'lastupdatedtime', 'state']]
    state_wise = state_wise.set_index('state')
    user_input = 'Total'
    tabel = ""
    tabel += 'Total reported COVID-19 cases in India' + '\n'
    tabel += '-' * 40 + '\n'
    for i in range(len(state_wise.loc[[user_input]].values[0])):
        tabel += str(state_wise.loc[user_input].index[i]) + " : " + str(state_wise.loc[user_input].values[i]) + '\n'
    update.message.reply_text(tabel, parse_mode='Markdown')


def dist_wide(update, context):
    user_input = " ".join(context.args)
    if user_input != "":
        dist = 'https://api.covid19india.org/v2/state_district_wise.json'
        dist = requests.get(dist)
        dist = dist.json()
        dist_data = json_normalize(dist, record_path='districtData', meta=['state'])
        dist_data = dist_data[['district', 'confirmed', 'state']]
        dist_data = dist_data.set_index('state')
        user_input = user_input.title().strip()
        try:
            table = ""
            table = 'District wise Kerala report' + '\n'
            table += '-' * 40 + '\n'
            for row in dist_data.loc[[user_input]].values:
                table += str(row[0]).title() + ': ' + str(row[1]) + '\n'
            update.message.reply_text(table, parse_mode='Markdown')
        except:
            update.message.reply_text("Invalid State name.Check the valid names from 'www.covid19india.org'")
    else:
        update.message.reply_text("State name should not be empty.Try /dist_of Kerala")


if __name__ == "__main__":
    # TOKEN = '' #Provide token name if running locally
    TOKEN = os.environ.get('API_TOKEN')  # Here the API token will provide ENV variable in Heroku

    NAME = 'india-covid19-bot'

    # PORT = 5000 #Provide port number if running locally
    # Port is given by Heroku
    PORT = int(os.environ.get('PORT', '8443'))
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('about', about))
    updater.dispatcher.add_handler(CommandHandler('help', get_help))
    updater.dispatcher.add_handler(CommandHandler('dist_of', dist_wide))
    updater.dispatcher.add_handler(CommandHandler('state', state_wide))
    updater.dispatcher.add_handler(CommandHandler('Cases_India', Country_wide))
    updater.dispatcher.add_handler(CommandHandler('advisory',advisory))
    # Start the webhook

    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(NAME, TOKEN))
    # updater.bot.setWebhook("https://<>.ngrok.io/{}".format(TOKEN)) #provide url if running locally

    # updater.start_polling()
    updater.idle()
