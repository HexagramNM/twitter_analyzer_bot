#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import twitter
import twitter_analyzer as ana
import io
import time
from datetime import date, datetime, timedelta
import sys
import traceback

log_file = open("error_log.txt", "a")
sys.stderr = log_file
error_message = "@HexagramNM botにエラーが発生しました."
long_time_message = "御無沙汰しております．\n"\
+ "前回のご利用から約1か月が経過いたしましたので，"\
+ "自動的に分析させていただきました．"
#dm_text = "この度は当botをフォローしていただき，ありがとうございます．このbotがあなたにフォローを返すことで，"\
#+ "鍵アカウントであるあなたも，botにリプライを飛ばすことによりbotの機能を利用いただけます．"\
#+ "ただし，次のデメリットがございます．\n"\
#+ "デメリット：このbotを通して，あなたのツイッターの頻度といった情報が漏れてしまいます．\n"\
#+ "デメリットを承諾して，当botを利用する際は，このDMでフォローを返して良いということをお伝えください．"\
#+ "確認次第，手動でフォローを返させていただきます．"
error_message_send = False
now_processed_account = []

try:
    with open("secret.json") as f:
        secretjson = json.load(f)
    t_auth=twitter.OAuth(secretjson["access_token"], secretjson["access_token_secret"], \
    secretjson["consumer_key"], secretjson["consumer_secret"])
    t = twitter.Twitter(auth=t_auth)
    pic_upload = twitter.Twitter(auth=t_auth, domain="upload.twitter.com")
#follower process
    follower_file = open("processed_follower.txt", "r")
    processed_follower_file = follower_file.readlines()
    follower_file.close()
    processed_follower = []
    for follower in processed_follower_file:
        processed_follower.extend([int(follower.strip('\n'))])
    follower_list = []
    before_follower_count = 0
    follower_list = t.followers.ids(screen_name="twianaNM_bot", stringify_id=True, count = 5000)['ids']
    follow_list = t.friends.ids(screen_name="twianaNM_bot", stringify_id=True, count=5000)['ids']
    for follow in follow_list:
        if not(follow in follower_list):
            t.friendships.destroy(user_id=follow)
#    while True:
#        follower_list.extend(follower_result['ids'])
#        if before_follower_count >= len(follower_list):
#            break
#        else:
#            before_follower_count = len(follower_list)
#        follower_result = t.followers.ids(screen_name="twianaNM_bot", stringify_id=True, count = 5000, cursor=follower_result['next_cursor'])

    not_processed_follower = []
    for follower in follower_list:
        if not follower in processed_follower:
            not_processed_follower.extend([str(follower)])

    if len(not_processed_follower) > 0:
        follower_details = t.users.lookup(user_id=','.join(not_processed_follower), include_entities=True)
        for detail in follower_details:
            t.friendships.create(user_id=detail['id'], follow=False)
            #DM警告機能OFF
            '''if detail['protected'] == True:
                t.direct_messages.new(user_id=detail['id'], text=dm_text)
            else:
                t.friendships.create(user_id=detail['id'], follow=False)'''

    follower_file = open("processed_follower.txt", "w")
    for follower in follower_list:
        follower_file.write(str(follower) + "\n")
    follower_file.close()
#tweet analysis activate
    follow_strID_list = []
    for follow_strID in follow_list:
        follow_strID_list.extend([str(follow_strID)])
    follow_detail_list = t.users.lookup(user_id=','.join(follow_strID_list))
    fa = open('account_history.txt')
    line_all_list = fa.readlines()
    fa.close()
#automatically analyze
    for follow_detail in follow_detail_list:
        print(follow_detail['screen_name'])
        if not follow_detail['protected']:
            i = 0
            for line in line_all_list:
                line_now = line.strip("\n")
                line_list = line_now.rsplit(" ", 3)
                if line_list[0] == follow_detail['screen_name']:
                    now_date = datetime.now()
                    if (now_date.date() - datetime.strptime(line_list[1], "%Y-%m-%d--%H-%M-%S").date()).days > 28:
                        replyerID = follow_detail['screen_name']
                        replyerIDnum = follow_detail['id']
                        this_account_num = i
                        result = ana.main_func(replyerID)
                        if result[0] == '0':
                            status = "@" + replyerID + " " + long_time_message + " " + now_date.strftime("%Y-%m-%d %H:%M:%S")
                            pic1 = "result/" + replyerID + "_1.png"
                            pic2 = "result/" + replyerID + "_2.png"
                            with open(pic1, "rb") as pic1_file:
                                pic1_data = pic1_file.read()
                            id_pic1 = pic_upload.media.upload(media=pic1_data)["media_id_string"]
                            with open(pic2, "rb") as pic2_file:
                                pic2_data = pic2_file.read()
                            id_pic2 = pic_upload.media.upload(media=pic2_data)["media_id_string"]
                            id_string = t.statuses.update(status=status, in_reply_to_screen_name=replyerID, media_ids=",".join([id_pic1, id_pic2]))['id_str']
                            line_all_list[this_account_num] = replyerID + " " + now_date.strftime("%Y-%m-%d--%H-%M-%S") + " " + id_string + " " + str(replyerIDnum) + "\n"
                            fa = open("account_history.txt", "w")
                            fa.writelines(line_all_list)
                            fa.close()
                            time.sleep(1)
                        now_processed_account.extend([replyerID])
                    break
                i += 1

#specifying analyze
    ni_file = open("processed_newest_id.txt", "r")
    newest_id = int(ni_file.readline())
    ni_file.close()
    tweets = t.statuses.mentions_timeline(count=200, since_id=newest_id, include_entities=True, trim_user=False)
    tweets.reverse()
    fa = open('account_history.txt')
    line_all_list = fa.readlines()
    fa.close()
    for tweet in tweets:
        replyerID = tweet['user']['screen_name']
        today_execute = False
        if (replyerID in now_processed_account) or (replyerID == "twianaNM_bot"):
            newest_id = int(tweet['id_str'])
            print(str(newest_id))
            time.sleep(1)
            ni_file = open("processed_newest_id.txt", "w")
            ni_file.write(str(newest_id))
            ni_file.close()
            continue
        replyerIDnum = tweet['user']['id']
        now_date = datetime.now()
        i = 0
        for line in line_all_list:
            line = line.strip("\n")
            line_list = line.rsplit(" ", 3)
            if replyerID == line_list[0]:
                this_account_num = i
                if now_date.date() == datetime.strptime(line_list[1], "%Y-%m-%d--%H-%M-%S").date():
                    today_execute = True
                break
            i += 1
        this_account_num = i
        if today_execute:
            status = "@" + replyerID + " すでに今日分析しております．（分析は1日1回までです．）\n"\
            + "以下のリンクが今日の結果です．\n" + "https://twitter.com/twianaNM_bot/status/" + line_list[2] + "\n" + now_date.strftime("%Y-%m-%d %H:%M:%S")
            t.statuses.update(status=status, in_reply_to_screen_name=replyerID)
        else:
            result = ana.main_func(replyerID)
            if result[0] == '0':
                status = "@" + replyerID + " " + now_date.strftime("%Y-%m-%d %H:%M:%S")
                pic1 = "result/" + replyerID + "_1.png"
                pic2 = "result/" + replyerID + "_2.png"
                with open(pic1, "rb") as pic1_file:
                    pic1_data = pic1_file.read()
                id_pic1 = pic_upload.media.upload(media=pic1_data)["media_id_string"]
                with open(pic2, "rb") as pic2_file:
                    pic2_data = pic2_file.read()
                id_pic2 = pic_upload.media.upload(media=pic2_data)["media_id_string"]
                id_string = t.statuses.update(status=status, in_reply_to_screen_name=replyerID, media_ids=",".join([id_pic1, id_pic2]))['id_str']

                if (this_account_num < len(line_all_list)):
                    line_all_list[this_account_num] = replyerID + " " + now_date.strftime("%Y-%m-%d--%H-%M-%S") + " " + id_string + " " + str(replyerIDnum) + "\n"
                else:
                    line_all_list.extend(replyerID + " " + now_date.strftime("%Y-%m-%d--%H-%M-%S") + " " + id_string + " " + str(replyerIDnum) + "\n")
                fa = open("account_history.txt", "w")
                fa.writelines(line_all_list)
                fa.close()
            elif result[0] == '4':
                status = "@" + replyerID + " ツイート取得時にエラーが発生しました．鍵垢になっていないかご確認ください．\n"\
                + "また，API切れの可能性がございますので，15分ほど待ってから再度返信してください． " + now_date.strftime("%Y-%m-%d %H:%M:%S")
                t.statuses.update(status=status, in_reply_to_screen_name=replyerID)
        now_processed_account.extend([replyerID])
        newest_id = int(tweet['id_str'])
        print(str(newest_id))
        time.sleep(1)
        ni_file = open("processed_newest_id.txt", "w")
        ni_file.write(str(newest_id))
        ni_file.close()
except:
    sys.stderr.write(traceback.format_exc())
    if not error_message_send:
        t.statuses.update(status=error_message + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),\
        in_reply_to_screen_name="@HexagramNM")
        error_message_send = True

log_file.close()
