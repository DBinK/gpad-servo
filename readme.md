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


### Debian / Ubuntu 相关

```bash
# 设置源
sudo sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
sudo apt edit-sources

sudo apt update 
sudo apt upgrade

sudo apt install fish htop python neofetch

# 设置中文
sudo apt install language-pack-zh-hans  
sudo dpkg-reconfigure locales
sudo nano /etc/default/locale  
# 设置为 
LANG="zh_CN.UTF-8"
LC_ALL="zh_CN.UTF-8"
```

### Python 相关

```bash
sudo apt install python

# 设置源为阿里源
pip install -i https://mirrors.aliyun.com/pypi/simple/ pip -U
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
# 查看是否配置成功
pip config list

pip show [package] # 查看环境路径

# 虚拟环境相关
python3 -m venv myenv --system-site-packages
source myenv/bin/activate.fish
pip3 install adafruit-circuitpython-pca9685

pip freeze > requirements.txt
```

### supervisor

```bash
sudo apt install supervisor
sudo nano /etc/supervisor/supervisord.conf

[program:myapp]
command=python /home/pi/gpad-servo/stream.py
directory=/home/pi/gpad-servo
environment=PYTHONPATH="/home/pi/.local/lib/python3.11/site-packages"
autostart=true
autorestart=false
stderr_logfile=/var/log/myapp.err.log
stdout_logfile=/var/log/myapp.out.log

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl reload

sudo supervisorctl stop myapp
sudo supervisorctl start myapp
```

### git

```bash
# 代理设置
git config --global http.proxy http://192.168.100.49:7897
git config --global https.proxy https://192.168.100.49:7897

git config --global --unset http.proxy
git config --global --unset https.proxy

# 强制远程覆盖本地分支
git fetch origin              # 获取远程分支的最新更新
git reset --hard origin/main  # 将本地分支重置到远程分支的最新提交
```

### 双抗双

## 供奉·

```python
print()
```

- dffdsf
- sdf
- sdfsdf
- sdf
- 

---

---