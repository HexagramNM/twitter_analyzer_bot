# twitter_analyzer_bot
ツイッター分析bot（@twianaNM_bot）のソース．

![ヒートマップ](https://github.com/HexagramNM/twitter_analyzer_bot/blob/master/HexagramNM_1.png)
![棒グラフ](https://github.com/HexagramNM/twitter_analyzer_bot/blob/master/HexagramNM_2.png)

実際の実行にはTwitter APIのアクセストークン等の情報や，データベース用のファイル"account_history.txt", "processed_newest_id.txt", エラーログ用のファイル"error_log.txt"が必要．

定期的（10分に1度）twitter_analyzer_continualbot.pyを実行することで，返信をもらったアカウントのツイート状況を
分析，可視化，返信をまとめて行う．

・その日2回目以降のツイートに対しては1回目での結果ツイートのリンクを返信

・まとめて処理の際に同一アカウントから複数回の返信があったとしても，1回だけ返信．

・自動フォロー，自動リムーブ

・エラーが生じた際のエラーログ記録＋管理者に通知ツイート送信機能

・利用してから28日経過した鍵垢でないフォローしているアカウントに対して自動分析＋返信
