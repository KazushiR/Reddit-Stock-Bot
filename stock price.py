import yfinance as yf
import time, praw, json, re
import pandas as pd
import FinNews as fn

#Get password for going int the reddit account
with open("config_cred.json") as r:
    data = json.load(r)
    reddit = praw.Reddit(client_id = data["client_id"],
                         client_secret = data["client_secret"],
                         username = data["username"],
                         password = data["password"],
                         user_agent = data["user_agent"])
    r.close()

def Respond_to_comment():
    while True:
        #Tries to make a comment and it fails as it can't access the subreddit, then it continues on with the program.
        try:
            time.sleep(6)
            #Gets the message from the account and if the profile is called upon in the comments, then it responds to the coment if it starts with !
            for message in reddit.inbox.unread(limit=None):
                    subject = message.subject.lower()
                    #Tries to look up the stock in the yfinance library. If it can't find it, then it responds to the original comment saying that it cannot find the stock ticker
                    try:
                        if subject == "username mention":
                            #parses the comments and see if anything starts with a !
                                pattern = re.compile("!\w+")
                                stocks_message = (pattern).findall(message.body)
                                print(stocks_message)
                                reply = message.id
                                if len(stocks_message) == 1:
                                    ticker = ("".join(stocks_message)).strip("!")
                                    #once it finds the stock, this portion goes and see's if it's on the US exchange, if not, it will send a message to the commenter to use a stock on the US exchange
                                    try:
                                        #Takes the stock ticker and then, from there, it parses the FinNews and see's if any recent articles are published or if any recent posts are made on Reddit
                                        Yahoo_feed = (fn.Yahoo(topics =['financial', f'${ticker}'], save_feeds=True)).get_news()
                                        Redd_feed = (fn.Reddit(topics =['financial', f'${ticker}'], save_feeds=True)).get_news()
                                        #uses the ticker to go through each stock information and gets the appropriate info.
                                        stocks = yf.Ticker(ticker)
                                        stock_data = stocks.info
                                        stock_price = ((stock_data["bid"] + stock_data["ask"])/2)
                                        stock_holders = (stocks.institutional_holders[["Holder", "Shares", "Value"]]).to_dict("index")
                                        stock_holders_major = stocks.major_holders.to_dict("index")
                                        stock_mutual_fund = stocks.mutualfund_holders[["Holder", "Shares", "Date Reported", "Value"]].to_dict("index")
                                        #This part parses through the  "stock_holders" from the panda's data and from there, converts it into a dictionary with the specific columns taken from Panda's and makes it into a reddit table format and posts this information on a forumn
                                        place_holder = ""
                                        for i, j in stock_holders.items():
                                            place_holder += str(j["Holder"]) + "|" + str("{:,}".format(j["Shares"]))+ "|" + "$" +str("{:,}".format(j["Value"])) + "\n"
                                            temporary_split = "|".join(place_holder.split("|"))

                                        #This part parses through the dictionary to get the percetnage held.
                                        major_holder = ""
                                        for i, j in stock_holders_major.items():
                                            major_holder += str(j[0]) + "|" + str(j[1]) + "\n"
                                            temporary_holders = "|".join(major_holder.split("|"))
                                        #This part gets the "stock_mutual_fund" and goes through each column and turns it into a table for reddit
                                        mutual_holders = ""
                                        for i, j in stock_mutual_fund.items():
                                            mutual_holders += str(j["Holder"]) + "|" + str("{:,}".format(j["Shares"])) + "|" + str(j["Date Reported"]) + "|" + str("{:,}".format(j["Value"])) + "\n"
                                            mutual_split = "|".join(mutual_holders.split("|"))
                                        message.reply(f"""
Hello, I am a bot that pulls stock information and posts some data about the company. Look at the information below and hopefully, this will  help you out.
\n
\n
**Company Name**: {stock_data["shortName"]}
\n
\n

**Company Website**:  {stock_data["website"]}

\n
\n

**Summary of Company**: {stock_data["longBusinessSummary"]}
\n
\n
**Approximate Stock Price**: ${round(stock_price, 2)}
\n
\n

**Shares owned by institution by percentage**: {round(stock_data["heldPercentInstitutions"], 2)}%
\n
\n

**Peg Ratio**: {stock_data["pegRatio"]}

\n
\n


**Short Ratio**: {stock_data["shortRatio"]}

\n
\n

**Stock Prices Fifty Day Average**: ${round(stock_data["fiftyDayAverage"], 2)}

\n
\n

**Short Interest**: {"{:,}".format(stock_data["dateShortInterest"])}

\n
\n

**Profit Margins**: {stock_data["profitMargins"]}



\n
\n

Share Holders|Shares Owned|Value of Shares
:--|:--|:--
{temporary_split}

\n
\n

Percentage of Shares|Description of Each Percentage
:--|:--|:--
{temporary_holders}

\n
\n

Mutual Fund Holders|Number of Shares Held|Date Reported|Value of Shares
:--|:--|:--|:--
{mutual_split}

\n
\n

**Links About {stock_data["longName"]}**:

\n
\n

**Yahoo Financial News**\n
{dict(Yahoo_feed[0])["link"]} \n\n
{dict(Yahoo_feed[1])["link"]} \n\n
{dict(Yahoo_feed[2])["link"]} \n\n
{dict(Yahoo_feed[3])["link"]} \n\n
{dict(Yahoo_feed[4])["link"]} \n\n
{dict(Yahoo_feed[5])["link"]} \n\n
{dict(Yahoo_feed[6])["link"]} \n\n
\n


**Reddit Threads**

{dict(Redd_feed[0])["link"]} \n\n
{dict(Redd_feed[1])["link"]} \n\n
{dict(Redd_feed[2])["link"]} \n\n
{dict(Redd_feed[3])["link"]} \n\n
{dict(Redd_feed[4])["link"]} \n\n
{dict(Redd_feed[5])["link"]} \n\n
{dict(Redd_feed[6])["link"]} \n\n

\n
\n
^Note: ^I ^am ^just ^giving ^finacial ^information. ^If ^you ^want ^to ^request ^information, ^please ^type ^! ^before ^the ^ticker ^symbol ^such ^as ^!GME""")
                                        message.mark_read()
                                    except KeyError:
                                        print("Stock might not exist in US Exchange")
                                        message.reply("Hey, that stock might not exist in the US Exchange, please try again. Please be sure to type something like !AMC")
                                        message.mark_read()
                                        continue
                                else:
                                    message.reply("Hey, I'm having trouble findind any stock information when you referenced me. Please type ! followed by the ticker symbol of the stock, such as !USB to get more information on a particular stock")
                                    message.mark_read()

                    except ImportError:
                        message.reply("Sorry, I don't recognize that stock, please check your spelling and send me a message again")
                        message.mark_read()
                        continue
        except TypeError:
            message.mark_read()
            continue


Respond_to_comment()
