#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import io
import time
from datetime import date, datetime, timedelta
import numpy as np
from twitter import *
import matplotlib.pyplot as plt
from matplotlib.widgets import Button


def main_func(twitterID):
    # initialize
    n = 1000
    checknum = 0
    today = datetime.now()
    dayrange = 28
    tweetnum = np.zeros((7, 24))
    tweetdaynum = np.zeros(dayrange)
    plotarray = np.zeros((480, 420))
    dayl = np.array(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    monthl = np.array(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    day = 0
    hour = 0
    # APIで取得可能な最大ツイート数（3200件だけど，念のため3000件に制限）
    API_get_max_tweet_num = 3000
    maxtweetnum = 1
    maxtweetdaynum = 1
    nowpage = 1
    display_new_date = ""
    display_old_date = ""

    # ツイッターから渡される時間はグリニッジ時間なのでJSTに直す
    class Tweetdate:
        def __init__(self, datestr):
            for i in range(12):
                if (datestr[4:7] == monthl[i]):
                    self.tm = i+1;
                    break
            self.td = int(datestr[8:10])
            self.ty = int(datestr[26:30])
            self.th = int(datestr[11:13])
            self.tmin = int(datestr[14:16])
            self.ts = int(datestr[17:19])
        def strtodatetime(self):
            return datetime(self.ty, self.tm, self.td, hour=self.th, minute=self.tmin, second= self.ts)+timedelta(hours=9)
        def __str__(self):
            return "%04d-%02d-%02d %02d:%02d:%02d" % (self.ty, self.tm, self.td, self.th, self.tmin, self.ts)

# get tweets
    with open("secret.json") as f:
        secretjson = json.load(f)

    t = Twitter(auth=OAuth(secretjson["access_token"], secretjson["access_token_secret"], secretjson["consumer_key"], secretjson["consumer_secret"]))
    try:
        apiresults = t.statuses.user_timeline(screen_name=twitterID, count=200, page=1)
    except TwitterHTTPError as err:
        return "4_error in getting tweets: " + str(err.response_data)
    print("nowpage: %d, %dth Tweet" % (nowpage, len(apiresults)))
    print(Tweetdate(apiresults[len(apiresults) - 1]['created_at']).strtodatetime().strftime("%Y-%m-%d %H:%M:%S"))
# analize
    displayID = ("@" + twitterID)
    before_resultcount = 0
    while True:
        now_max_id = apiresults[len(apiresults)-1]['id']
        nowpage += 1
        try:
            apiresults.extend(t.statuses.user_timeline(screen_name=twitterID, count=200, max_id=now_max_id-1))
        except TwitterHTTPError as err:
            return "4_error in getting tweets: " + str(err.response_data)
        print("nowpage: %d, %dth Tweet" % (nowpage, len(apiresults)))
        print(Tweetdate(apiresults[len(apiresults) - 1]['created_at']).strtodatetime().strftime("%Y-%m-%d %H:%M:%S"))
        if len(apiresults) >= API_get_max_tweet_num:
            dayrange = 7 * (((today.date()-Tweetdate(apiresults[len(apiresults) - 1]['created_at']).strtodatetime().date()).days) // 7)
            print("Automatically, we set dayrange: %d" % dayrange)
            break
        elif (today.date()-Tweetdate(apiresults[len(apiresults) - 1]['created_at']).strtodatetime().date()).days > dayrange:
            break
        if before_resultcount < len(apiresults):
            before_resultcount = len(apiresults)
        else:
            break
    before_resultcount = len(apiresults)
    i = 0
    display_new_date = ""
    display_old_date = ""
    while True:
        if i >= before_resultcount:
            if (display_new_date != ""):
                display_old_date = ("The oldest checked tweet date: " + str(Tweetdate(apiresults[before_resultcount - 1]['created_at']).strtodatetime()))
            else:
                display_new_date = ("This account has not tweeted for %d days." % (dayrange))
            break
        s = apiresults[i]['created_at']
        if ((today.date()-Tweetdate(s).strtodatetime().date()).days < 1):
            i += 1
            continue
        elif ((today.date()-Tweetdate(s).strtodatetime().date()).days > dayrange):
            if (display_new_date != ""):
                display_old_date = ("The oldest checked tweet date: " + str(Tweetdate(apiresults[i-1]['created_at']).strtodatetime()))
            else:
                display_new_date = ("This account has not tweeted for %d days." % (dayrange))
            break
        elif (checknum == 0):
            display_new_date = ("The newest checked tweet date: " + str(Tweetdate(apiresults[i]['created_at']).strtodatetime()))
        for j in range(7):
            if (s[0:3] == dayl[j]):
                day = j
                break
        hour = int(s[11:13]) + 9
        if (hour > 23):
            day = (day + 1) % 7
            hour -= 24
        tweetnum[day][hour] += 1
        tweetdaynum[(today.date()-Tweetdate(s).strtodatetime().date()).days-1] += 1
        checknum += 1
        i += 1

    display_check_num = ("Recent %d tweets are checked" % (checknum))

# display
    templist = [np.max(tweetnum[a]) for a in range(7)]
    templist.extend([1.0])
    maxtweetnum = max(templist)
    templist = [tweetdaynum[a] for a in range(dayrange)]
    maxtweetdaynum = max(templist)
    for x in range(420):
        for y in range(480):
            plotarray[y][x] = tweetnum[int(x/60)][int(y/20)]
    plt.figure(figsize=(12, 9))
    plt.title(displayID+"\n"+display_check_num)

    fig = plt.gcf()
    a = plt.gca();
# heat map
    a.cla()
    plt.sca(a)
    plt.imshow(plotarray, cmap="hot", clim=(0.0, maxtweetnum))
    c = plt.colorbar()
    plt.title(displayID+"\n"+display_check_num)
    plt.xticks([30+60*i for i in range(7)], dayl)
    plt.yticks([20*i for i in range(25)], [str(i)+":00" for i in range(25)])
    plt.xlabel("Day" +"\n"+display_new_date+"\n"+display_old_date)
    plt.ylabel("Time")
    plt.savefig("result/" + twitterID + "_1.png")

# bar graph
    a.cla()
    plt.sca(a)
    plt.title(displayID+"\n"+display_check_num)
    interval = (maxtweetdaynum+3.0)/dayrange
    X = [interval * (dayrange - i - 1) for i in range(dayrange)]
    plt.bar(X, tweetdaynum[0:dayrange], width=(interval/2.0) ,align="center")
    daylabel_list = []
    for i in range(dayrange):
        if i == dayrange - 1 or (today-timedelta(days=i+1)).month != (today-timedelta(days=i+2)).month:
            daylabel_list.extend([str((today-timedelta(days=i+1)).month)+"/"+str((today-timedelta(days=i+1)).day)])
        else:
            daylabel_list.extend([str((today-timedelta(days=i+1)).day)])
    plt.xticks(X, daylabel_list)
    plt.xlabel("Day" +"\n"+display_new_date+"\n"+display_old_date)
    plt.ylabel("Tweet num")
    plt.xlim([-interval/2.0,interval*dayrange-interval/2.0])
    plt.ylim([0,maxtweetdaynum+3])
    for i in range(dayrange):
        plt.text(X[i]-interval/4.0, tweetdaynum[i]+0.7, str(int(tweetdaynum[i])), fontsize=13)
    plt.savefig("result/" + twitterID + "_2.png")
    return "0_complete"


if __name__ == "__main__":
    args = sys.argv
    if len(args) == 2:
        twitterID = args[1]
    else:
        twitterID = input("Input TwitterID which you want to analize: @")
    print(main_func(twitterID))

'''
class Mode(object):
    def __init__(self):
        self.mode = 0
    def dayhour(self, event):
        #曜日と時間帯
        if (self.mode != 0):
            a.cla()
            plt.sca(a)
            plt.title(displayID+"\n"+display_check_num)
            plt.imshow(plotarray, cmap="hot", clim=(0.0, maxtweetnum))
            plt.xticks([30+60*i for i in range(7)], dayl)
            plt.yticks([20*i for i in range(25)], [str(i)+":00" for i in range(25)])
            plt.xlabel("Day" +"\n"+display_new_date+"\n"+display_old_date)
            plt.ylabel("Time")
            plt.draw()
        self.mode = 0
    def daynum(self, event):
        #日付とツイート数
        if (self.mode != 1):
            a.cla()
            plt.sca(a)
            plt.title(displayID+"\n"+display_check_num)
            interval = (maxtweetdaynum+3.0)/dayrange
            X = [interval * (dayrange - i - 1) for i in range(dayrange)]
            plt.bar(X, tweetdaynum[0:dayrange], width=(interval/2.0) ,align="center")
            plt.xticks(X, [str((today-timedelta(days=i+1)).month)+"/"+str((today-timedelta(days=i+1)).day) for i in range(dayrange)])
            plt.xlabel("Day" +"\n"+display_new_date+"\n"+display_old_date)
            plt.ylabel("Tweet num")
            plt.xlim([-interval/2.0,interval*dayrange-interval/2.0])
            plt.ylim([0,maxtweetdaynum+3])
            for i in range(dayrange):
                plt.text(X[i]-interval/4.0, tweetdaynum[i]+0.7, str(int(tweetdaynum[i])), fontsize=13)
            plt.draw()
        self.mode = 1
callback = Mode()
plt.imshow(plotarray, cmap="hot", clim=(0.0, maxtweetnum))
plt.xticks([30+60*i for i in range(7)], dayl)
plt.yticks([20*i for i in range(25)], [str(i)+":00" for i in range(25)])
plt.xlabel("Day" +"\n"+display_new_date+"\n"+display_old_date)
plt.ylabel("Time")
a = plt.gca();
c = plt.colorbar()
#axes [x位置, ｙ位置, 幅, 高さ]
axdh = plt.axes([0.7, 0.01, 0.1, 0.05])
axdn = plt.axes([0.81, 0.01, 0.1, 0.05])
bdayhour = Button(axdh, 'dayhour')
bdayhour.on_clicked(callback.dayhour)
bdaynum = Button(axdn, 'daynum')
bdaynum.on_clicked(callback.daynum)

plt.show()
'''
