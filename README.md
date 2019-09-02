# WATT CHECKER Client

## 動作環境

- [ラトックシステム株式会社 Bluetoothワットチェッカー REX-BTWATTCH1](http://www.ratocsystems.com/products/subpage/btwattch1.html)
- [サンワサプライ株式会社 Bluetooth 4.0 USBアダプタ（Class 2） MM-BTUD44](https://www.sanwa.co.jp/product/syohin.asp?code=MM-BTUD44)
- Raspberry Pi 2 Model B
    - OS: Ubuntu 18.04.2


## インストール＆起動手順

### 1. インストール

依存パッケージをインストールする。

```
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv libbluetooth3-dev
```

リポジトリを `/opt/wattchecker-client` にクローンする。

```
sudo git clone https://github.com/j3iiifn/wattchecker-client /opt/wattchecker-client
```

`wattchecker` ユーザを作成し、 `/opt/wattchecker-client` の所有者を変える。

```
sudo adduser --system --group --home /opt/wattchecker-client --no-create-home --shell /bin/false wattchecker
sudo chown -R wattchecker:wattchecker /opt/wattchecker-client
```

venvを作成し、`pybluez`, `crcmod`, `pyyaml`, `google-cloud-bigquery` をインストールする。

```
cd /opt/wattchecker-client
sudo -u wattchecker python3 -m venv venv
sudo -u wattchecker -H venv/bin/pip install wheel
sudo -u wattchecker -H venv/bin/pip install -r requirements.txt
```

設定ファイルを作成する。

```
sudo -u wattchecker cp config_sample.yaml config.yaml
```

`log` ディレクトリを作成する。

```
sudo -u wattchecker mkdir log
```

### 2. Bluetooth ペアリング

`bluetoothctl` コマンドでワットチェッカーとペアリングする。

`bluetoothctl` を実行し、`bluetoothctl` のシェルに入る。

```
bluetoothctl
```

スキャンをONにして、周囲にあるBluetooth機器のMACアドレスを表示する。
`WATT CHECKER` のMACアドレスを探す。

```
agent on
scan on
devices
scan off
```

`WATT CHECKER` のMACアドレスを指定してペアリングする。PINコードは`0000`。

```
pair 00:0C:BF:XX:XX:XX
```

`info` コマンドの出力で `Paired:` が `yes` になっていることを確認する。

```
info 00:0C:BF:XX:XX:XX
```

`bluetoothctl` から出る。

```
exit
```

### 3. systemd設定

```
sudo cp wattchecker_client.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable wattchecker_client.service
sudo systemctl start wattchecker_client.service
```


## 謝辞

Bluetoothワットチェッカー（REX-BTWATTCH1）との通信プログラムは株式会社アットマークテクノ様のサンプルプログラム[1]を参考に実装した。

[1] [Armadillo-IoT G3で「Bluetooth ワットチェッカー」から計測データを表示 | 組み込みLinuxのArmadilloサイト](https://armadillo.atmark-techno.com/howto/armadillo_rex-btwattch1)
