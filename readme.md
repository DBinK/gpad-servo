## 环境
```shell
       _,met$$$$$gg.           pi@WalnutPi
    ,g$$$$$$$$$$$$$$$P.        -----------
  ,g$$P"         """Y$$.".     OS: Debian GNU/Linux bookworm 12.5 aarch64
 ,$$P'               `$$$.     Host: walnutpi-1b
',$$P       ,ggs.     `$$b:    Kernel: 6.1.31
`d$$'     ,$P"'   .    $$$     Uptime: 37 mins
 $$P      d$'     ,    $$$P    Packages: 846 (dpkg)
 $$:      $.   -    ,d$$'      Shell: fish 3.6.0
 $$;      Y$b._   _,d$P'       Cursor: Adwaita
 Y$$.    `.`"Y$$$$P"'          Terminal: /dev/pts/2
 `$$b      "-.__               CPU: Cortex-A53 (4)
  `Y$$                         Memory: 304.19 MiB / 1.94 GiB (15%)
   `Y$$.                       Swap: Disabled
     `$$b.                     Disk (/): 3.32 GiB / 28.86 GiB (12%) - ext4
       `Y$$b.                  Local IP (wlan0): 192.168.100.171/24 *
          `"Y$b._              Locale: zh_CN.UTF-8
             `"""
```
- python3.11
- walnutpi 2.2.0 固件

## 开始
```shell
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
#source .venv/bin/activate.fish
pip install -r requirements.txt
```
