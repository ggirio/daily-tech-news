# トラブルシューティング

## cron実行時に「Selected provider is forbidden」エラーが発生する

### 問題
手動で`python main.py`を実行すると成功するが、cronから実行すると全てのAI APIコールが「Selected provider is forbidden」エラーで失敗し、デフォルトコメント「チェックしておきたいニュースです!」が使用される。

### 症状
```
Error summarizing news with AI: Selected provider is forbidden
Error type: PermissionDeniedError
```

### 確認済みの項目
- ✅ `.env`ファイルの環境変数は正しく読み込まれている
- ✅ `AWS_SESSION_TOKEN`(PAT)は設定されている
- ✅ cronスクリプトはユーザープロファイルを読み込んでいる
- ✅ 手動実行では同じ環境変数で成功する

### 原因
GenAI Gateway (LINE社内Bedrockプロキシ)が、cronから実行されたリクエストを拒否している可能性があります。以下の理由が考えられます:

1. **セッションコンテキストの違い**: PATトークンに実行コンテキスト(対話的セッション vs バックグラウンドジョブ)に基づいた制限がある
2. **レート制限**: cronの実行頻度が高い場合、レート制限に引っかかっている
3. **アクセス制御ポリシー**: GenAI Gateway側で、特定の実行環境からのアクセスを制限している

### 推奨される解決策

#### オプション1: GenAI Gatewayチームに確認
社内のSlackチャンネルで問い合わせ:
- `#ext-help-genai-gateway` または類似のチャンネル
- エラーメッセージと実行環境(cron vs 手動)の違いを説明

#### オプション2: 実行方法を変更
cronから直接Pythonスクリプトを実行するのではなく、以下の方法を検討:

1. **GitHub Actions**: すでにGitHub Actionsで実行されている場合は、そちらを使用
2. **対話的セッションでのスケジューリング**: `tmux`や`screen`を使った対話的セッション内でスクリプトを実行
3. **ラッパースクリプト**: ユーザーのログインシェル環境を完全に再現するラッパーを作成

#### オプション3: エラーハンドリングの改善(一時的な対処)
現在の実装では、APIエラー時にデフォルトメッセージを返していますが、以下を検討:

1. **リトライロジックの追加**: 一時的なエラーの場合はリトライする
2. **通知の改善**: AI APIが失敗した場合は、Issue内で明示的に失敗を通知
3. **フォールバックモード**: 簡易的な要約(最初の200文字など)を使用

### 一時的な回避策

cron実行時のエラーを明示的に表示するように修正:

```python
# src/ai_analyzer.py の summarize_and_comment メソッド
except Exception as e:
    import traceback
    print(f"Error summarizing news with AI: {e}")
    print(f"Error type: {type(e).__name__}")
    return {
        "summary": news_item.description[:200] if news_item.description else "詳細は記事をご覧ください。",
        "comment": "⚠️ AI分析が利用できませんでした。" # エラーを明示
    }
```

### 次のステップ
1. GenAI Gatewayのドキュメントを確認: https://chatai.workers-hub.com/dashboard/
2. 社内のSlackチャンネルで問い合わせ
3. 必要に応じて、標準のAnthropic APIへの切り替えを検討(費用が発生)
