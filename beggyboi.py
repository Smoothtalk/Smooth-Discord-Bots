import asyncio
import os
import sys
import random
import datetime
import discord
import operator

token = ""

DUCKWAD_SERVER_ID = ""
BOTTESTING_CHANNEL_ID = ""

DUCKWAD_ID = ''
SMOOTH_ID = ''

stats = {}

discordClient = discord.Client()

@discordClient.event
async def on_message(message):
    global stats
    upperCase = message.content.upper()
    testingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)

    if((upperCase.find("DUCK") != -1 or upperCase.find("DUCKWAD") != -1) and (upperCase.find("MISS") != -1 or upperCase.find("REMEMBER") != -1)):
        if(stats.get(message.author.id) == None): #first mention
            counter = {'dailyCounter' : 1, 'weeklyCounter' : 1, 'monthlyCounter' : 1, 'allTimeCounter' : 1};
            stats[message.author.id] = counter
        else:
            #raise all counters
            stats[message.author.id]['dailyCounter'] = stats[message.author.id]['dailyCounter'] + 1
            stats[message.author.id]['weeklyCounter'] = stats[message.author.id]['weeklyCounter'] + 1
            stats[message.author.id]['monthlyCounter'] = stats[message.author.id]['monthlyCounter'] + 1
            stats[message.author.id]['allTimeCounter'] = stats[message.author.id]['allTimeCounter'] + 1
        print (message.author.id + ": " + str(stats[message.author.id]))
    else:
        try:
            targetUserIndex = (message.raw_mentions).index(DUCKWAD_ID)
            if(stats.get(message.author.id) == None): #first mention
                counter = {'dailyCounter' : 1, 'weeklyCounter' : 1, 'monthlyCounter' : 1, 'allTimeCounter' : 1};
                stats[message.author.id] = counter
            else:
                #raise all counters
                stats[message.author.id]['dailyCounter'] = stats[message.author.id]['dailyCounter'] + 1
                stats[message.author.id]['weeklyCounter'] = stats[message.author.id]['weeklyCounter'] + 1
                stats[message.author.id]['monthlyCounter'] = stats[message.author.id]['monthlyCounter'] + 1
                stats[message.author.id]['allTimeCounter'] = stats[message.author.id]['allTimeCounter'] + 1
            print (stats[message.author.id])
        except: #target mention not triggered (Duck wasn't @'d)
            e = sys.exc_info
            # print ("This went wrong: " + str(e))

    if (upperCase == '!TEST' and message.channel == testingChannel):
        stats['359692323363487745'] = {'dailyCounter' : 8, 'weeklyCounter' : 7, 'monthlyCounter' : 6, 'allTimeCounter' : 5}
        stats['359824852300988417'] = {'dailyCounter' : 1, 'weeklyCounter' : 2, 'monthlyCounter' : 3, 'allTimeCounter' : 4}
        stats['412821848750030850'] = {'dailyCounter' : 9, 'weeklyCounter' : 10, 'monthlyCounter' : 11, 'allTimeCounter' : 12}
        stats['357606444830294017'] = {'dailyCounter' : 9, 'weeklyCounter' : 10, 'monthlyCounter' : 11, 'allTimeCounter' : 0}
        print(stats)

    if (upperCase == '!PRINT' and message.channel == testingChannel):
        print (stats)

    if (upperCase == '!BBSTATSALL' and message.channel == testingChannel):
        sortedAllStats = {}
        for element in stats:
            sortedAllStats[element] = stats[element]['allTimeCounter']
        sortedAllStats = sorted(sortedAllStats.items(), key=operator.itemgetter(1), reverse=True)
        messageToSendTitle = "----- All Time Top Stats -----\n"
        await discordClient.send_message(message.channel, messageToSendTitle)
        for element in sortedAllStats:
            if(element[1] != 0):
                userName = await discordClient.get_user_info(element[0])
                messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                await discordClient.send_message(message.channel, messageToSend)
        if(sortedAllStats[0]['allTimeCounter'] != 0):
            topBeggerUserName = await discordClient.get_user_info(sortedAllStats[0][0])
            messageToSend = '```Holy fuck ' + topBeggerUserName.name + ' could you be anymore needy```'
            await discordClient.send_message(message.channel, messageToSend)

    if (upperCase == '!BBSTATSMONTHLY' and message.channel == testingChannel):
        sortedAllStats = {}
        for element in stats:
            sortedAllStats[element] = stats[element]['monthlyCounter']
        sortedAllStats = sorted(sortedAllStats.items(), key=operator.itemgetter(1), reverse=True)
        messageToSendTitle = "----- Month Top Stats -----\n"
        await discordClient.send_message(message.channel, messageToSendTitle)
        for element in sortedAllStats:
            if(element[1] != 0):
                userName = await discordClient.get_user_info(element[0])
                messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                await discordClient.send_message(message.channel, messageToSend)
        if(sortedAllStats[0]['monthlyCounter'] != 0):
            topBeggerUserName = await discordClient.get_user_info(sortedAllStats[0][0])
            messageToSend = '```Holy fuck ' + topBeggerUserName.name + ' could you be anymore needy```'
            await discordClient.send_message(message.channel, messageToSend)

    if (upperCase == '!BBSTATSWEEKLY' and message.channel == testingChannel):
        sortedAllStats = {}
        for element in stats:
            sortedAllStats[element] = stats[element]['weeklyCounter']
        sortedAllStats = sorted(sortedAllStats.items(), key=operator.itemgetter(1), reverse=True)
        messageToSendTitle = "----- Weekly Top Stats -----\n"
        await discordClient.send_message(message.channel, messageToSendTitle)
        for element in sortedAllStats:
            if(element[1] != 0):
                userName = await discordClient.get_user_info(element[0])
                messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                await discordClient.send_message(message.channel, messageToSend)
        if(sortedAllStats[0]['weeklyCounter'] != 0):
            topBeggerUserName = await discordClient.get_user_info(sortedAllStats[0][0])
            messageToSend = '```Holy fuck ' + topBeggerUserName.name + ' could you be anymore needy```'
            await discordClient.send_message(message.channel, messageToSend)

    if (upperCase == '!BBSTATSDAILY' and message.channel == testingChannel):
        sortedAllStats = {}
        for element in stats:
            sortedAllStats[element] = stats[element]['dailyCounter']
        sortedAllStats = sorted(sortedAllStats.items(), key=operator.itemgetter(1), reverse=True)
        messageToSendTitle = "----- Daily Top Stats -----\n"
        await discordClient.send_message(message.channel, messageToSendTitle)
        for element in sortedAllStats:
            if(element[1] != 0):
                userName = await discordClient.get_user_info(element[0])
                messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                await discordClient.send_message(message.channel, messageToSend)
        if(sortedAllStats[0]['dailyCounter'] != 0):
            topBeggerUserName = await discordClient.get_user_info(sortedAllStats[0][0])
            messageToSend = '```Holy fuck ' + topBeggerUserName.name + ' could you be anymore needy```'
            await discordClient.send_message(message.channel, messageToSend)

# check every 24hrs
# when displaying the results skip any 0
async def dailyCheck():
    await discordClient.wait_until_ready()
    while not discordClient.is_closed:
        testingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)
        timeStamp = datetime.datetime.today().time()
        stringTimeStamp = str(timeStamp)
        hour = stringTimeStamp[0:2]
        minute = stringTimeStamp[3:5]
        print ("full time: " + stringTimeStamp)
        print ("hour: " + hour)
        print ("minute: " + minute)

        if((hour == "23" and minute == "59") or (hour == "00" and minute == "00") or (hour == "00" and minute == "01")): #accounting for desync
            # reset daily counter
            # if Sunday (Today Code = 0) reset weekly counter
            # if Month End(check if yesterday has a difference month code) reset monthly counter
            todayCode = str(datetime.date.today().strftime("%w"))
            yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
            yesterdayMonth = str(yesterday.strftime("%m"))
            todayMonth = str(datetime.date.today().strftime("%m"))
            print("Day Change")

            sortedDailyStats = {}
            for element in stats:
                sortedDailyStats[element] = stats[element]['dailyCounter']
            sortedDailyStats = sorted(sortedDailyStats.items(), key=operator.itemgetter(1), reverse=True)

            messageToSendTitle = "----- Daily Top Stats -----\n"
            await discordClient.send_message(testingChannel, messageToSendTitle)
            for element in sortedDailyStats:
                if(element[1] != 0):
                    userName = await discordClient.get_user_info(element[0])
                    messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                    await discordClient.send_message(testingChannel, messageToSend)

            # Clear daily stats
            for user in stats:
                stats[user]['dailyCounter'] = 0

            if(todayCode == '0'): #rolled over to Sunday
                # sort weekly counter into new array and send that, then clear
                sortedWeeklyStats = {}
                for element in stats:
                    sortedWeeklyStats[element] = stats[element]['weeklyCounter']
                sortedWeeklyStats = sorted(sortedWeeklyStats.items(), key=operator.itemgetter(1), reverse=True)

                messageToSendTitle = "----- Weekly Top Stats -----\n"
                await discordClient.send_message(testingChannel, messageToSendTitle)
                for element in sortedWeeklyStats:
                    if(element[1] != 0):
                        userName = await discordClient.get_user_info(element[0])
                        messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                        await discordClient.send_message(testingChannel, messageToSend)

                for user in stats:
                    stats[user]['weeklyCounter'] = 0

            if(todayMonth != yesterdayMonth): #rolled over to next month
                # sort monthly counter into new array and send that, then clear
                sortedMonthlyStats = {}
                for element in stats:
                    sortedMonthlyStats[element] = stats[element]['monthlyCounter']
                sortedMonthlyStats = sorted(sortedMonthlyStats.items(), key=operator.itemgetter(1), reverse=True)

                messageToSendTitle = "----- Monthly Top Stats -----\n"
                await discordClient.send_message(testingChannel, messageToSendTitle)
                for element in sortedMonthlyStats:
                    if(element[1] != 0):
                        userName = await discordClient.get_user_info(element[0])
                        messageToSend = userName.name + ' begged ' + str(element[1]) + ' times'
                        await discordClient.send_message(testingChannel, messageToSend)

                for user in stats:
                    stats[user]['monthlyCounter'] = 0

            print ("sleeping for 86400 seconds")
            await asyncio.sleep(86400)
        else:
            hoursLeft = 23 - int(hour)
            minutesLeft = (60 - int(minute)) + (60 * hoursLeft)
            secondsLeft = (60 * minutesLeft)

            print (str(minutesLeft) + " minutes left till next sync")
            print ("sleeping for " + str(secondsLeft) + " seconds")
            await asyncio.sleep(secondsLeft)

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    discordClient.loop.create_task(dailyCheck())
    print('-------')

discordClient.run(token)
