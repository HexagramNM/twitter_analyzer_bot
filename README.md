# twitter_analyzer_bot
ツイッター分析bot（@twianaNM_bot）のソース．

実際の実行にはTwitter APIのアクセストークン等の情報や，データベース用のファイル"account_history.txt", 
"processed_follower.txt", "processed_newest_id.txt", エラーログ用のファイル"error_log.txt"が必要．

定期的（10分に1度）twitter_analyzer_continualbot.pyを実行することで，まとめて返信をもらったアカウントのツイート状況を
分析，可視化，返信を行う．自動フォロー，自動リムーブ，鍵垢に対する案内DM送信機能付き

