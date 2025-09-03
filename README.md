### **[Download 點我下載](https://github.com/Lucienwooo/ChroLens_Sentinel/releases/download/1.0/ChroLens_Sentinel.exe)**
# ChroLens_Sentinel

![ChroLens_Sentinel](./pic/clse1.png)

---

### 定時關閉與封鎖指定程式，避免它們在背景偷偷運行。
### 指定したプログラムを定期的に終了・ブロックし、バックグラウンドでの動作を防ぎます。
### Schedule and block specified programs to prevent them from running in the background.

可自訂清單與間隔，啟動後自動巡檢，停用也一鍵搞定。
リストと実行間隔をカスタマイズ可能。起動後は自動で巡回監視し、ワンクリックで無効化もできます。
You can customize the list and interval. Once activated, it automatically patrols and can be disabled with a single click.

---

## 📜 起因 (きっかけ / Origin)

前兩天自己手殘去按到更新並重開機，導致 Windows 版本更新。結果遇到一個奇怪的 Bug —— 工作管理員中那幾個程式會無限增長，一直重複執行，CPU 使用率就會慢慢撐到 **100%**。

先日、うっかり更新と再起動をしてしまい、Windowsがアップデートされました。その結果、タスクマネージャーの特定のプログラムが無限に増殖・繰り返し実行され、CPU使用率が徐々に**100%**まで上昇する奇妙なバグに遭遇しました。

Two days ago, I accidentally updated and rebooted, which led to a Windows version update. This caused a strange bug where certain programs in Task Manager would endlessly multiply and repeat, slowly pushing the CPU usage to **100%**.

小丑終究是我自己 🤡
結局、私がピエロでした 🤡
I was the clown all along 🤡

起初寫了個 `.bat` 來跑，但成效不彰，最後還是寫成 **Python** 打包成 `.exe`。

最初は`.bat`ファイルで対応しましたが、効果が不十分でした。最終的に**Python**でプログラムを書き、`.exe`としてパッケージ化しました。

Initially, I wrote a `.bat` script, but it wasn't effective. Ultimately, I wrote the program in **Python** and packaged it into an `.exe`.

---

## ✨ 功能特色 (特徴 / Features)

- **可自訂封鎖清單** — 欄位中的檔案名稱可以修改。
  **ブロックリストのカスタマイズ可能** — フィールド内のファイル名は変更できます。
  **Customizable Block List** — The file names in the fields can be modified.

- **可增減監控項目** — 欄位可自由增減。
  **監視項目の追加・削除可能** — フィールドは自由に増減できます。
  **Add/Remove Monitored Items** — Fields can be freely added or removed.

- **定時巡檢** — 重複執行時間可自訂。
  **定期的な巡回** — 繰り返し実行する時間をカスタマイズできます。
  **Scheduled Patrol** — The repetition interval can be customized.

- **持續守護** — 啟動後自動監控並封鎖目標程式。
  **継続的な保護** — 起動後、自動的に対象プログラムを監視しブロックします。
  **Continuous Guarding** — Automatically monitors and blocks target programs once activated.

- **一鍵停用** — 想要解除封鎖，直接按下按鈕即可。
  **ワンクリックで無効化** — ブロックを解除したい場合は、ボタンを押すだけです。
  **One-Click Disable** — To unblock, simply press the button.

---

## ⚠️ 注意 (注意 / Note)

這是一個相對冷門的工具，正常情況下你可能永遠不會需要它。但一旦遇到類似 **Windows 更新後的背景程式無限啟動 Bug**，它或許能救你一命。

これは比較的ニッチなツールで、通常は必要ないかもしれません。しかし、**Windowsアップデート後のバックグラウンドプログラム無限起動バグ**のような問題に遭遇した際には、あなたの命を救うかもしれません。

This is a relatively niche tool that you might never need under normal circumstances. However, if you encounter a bug similar to the **endless background program loop after a Windows update**, it might just save you.

> 希望大家不要遇到比較好 🙏
> 皆さんがこのツールを必要としないことを願っています 🙏
> Hopefully, no one will ever need this 🙏