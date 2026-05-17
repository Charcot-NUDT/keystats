# Keystats - Linux 键盘活动监视器

> 一个轻量级、注重隐私的 Linux 键盘活动统计工具。

Keystats 在后台静默运行，记录你每天的按键次数。它追踪**每个按键的单独统计**（哪个键按了多少次）、小时分布、每日趋势等——所有数据都保存在本地 SQLite 数据库中。你的输入内容**永远不会被记录**，只保存计数。

---

## 功能特性

- **逐键统计** — 查看每个按键的按下次数（A、回车、空格、退格……）
- **每日按键总数** — 每天的总按键次数
- **24小时分布** — 全天活动热力图，找出你的高效时段
- **周趋势对比** — 对比最近7天的活跃度
- **历史排行榜** — 你打字最多的那些天
- **连续打卡** — 连续有打字记录的天数
- **隐私优先设计** — 只保存计数，**输入内容永不记录**
- **纯本地存储** — 所有数据保存在本地 SQLite 数据库
- **Systemd 集成** — 开机自启，作为系统服务运行
- **轻量级** — 内存占用约 10MB，CPU 占用极低

---

## 系统要求

| 组件 | 要求 |
|-----------|-------------|
| 操作系统 | Linux（推荐 Ubuntu/Debian） |
| 内核 | 2.6+（需要 evdev 支持） |
| Python | 3.7 或更高 |
| 依赖 | `python3-evdev`、`systemd` |
| 权限 | 需要 root 权限（访问 `/dev/input/event*`） |

---

## 安装

### 方式一：从 .deb 包安装（推荐）

```bash
# 下载安装包
wget https://github.com/Charcot-NUDT/keystats/releases/download/v1.0.0/keystats_1.0.0_all.deb

# 安装
sudo dpkg -i keystats_1.0.0_all.deb

# 如有依赖问题，自动修复
sudo apt-get install -f

# 启动服务
sudo systemctl start keystats
sudo systemctl enable keystats   # 开机自启

# 验证运行状态
sudo systemctl status keystats
```

### 方式二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/Charcot-NUDT/keystats.git
cd keystats/keystats-project

# 安装依赖
sudo apt-get install -y python3-evdev

# 复制文件
sudo mkdir -p /usr/lib/keystats /var/lib/keystats /var/log/keystats
sudo cp keystats/usr/lib/keystats/*.py /usr/lib/keystats/
sudo cp keystats/usr/bin/keystats-* /usr/bin/
sudo chmod +x /usr/bin/keystats-*
sudo chmod 777 /var/lib/keystats /var/log/keystats

# 安装 systemd 服务
sudo cp keystats/etc/systemd/system/keystats.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable keystats
sudo systemctl start keystats
```

---

## 使用指南

### CLI 命令

| 命令 | 简写 | 说明 |
|---------|-------|-------------|
| `keystats-cli` | — | 今日总按键数 |
| `keystats-cli summary` | `s` | 每日详细总结 |
| `keystats-cli keys` | `k` | 今日逐键统计排行榜 |
| `keystats-cli allkeys` | `ak` | 历史累计逐键统计 |
| `keystats-cli week` | `w` | 最近7天活动 |
| `keystats-cli top` | `t` | 最活跃的10天 |
| `keystats-cli date YYYY-MM-DD` | — | 指定日期的统计 |
| `keystats-cli help` | `-h` | 显示帮助 |

### 每日总结

```bash
$ keystats-cli summary

==================================================
  每日键盘活动总结
  2026年5月17日 星期日
==================================================

  今日
    按键总数: 12,847
    较昨日: +3,210 (+33.3%)
    估算字数: ~2,569
    估算平均WPM: ~36

  本周 (7天)
    总按键数: 78,234
    日均: 11,176

  历史总计
    总按键数: 456,789
    日均: 9,135
    连续打卡: 12 天

  今日高峰时段
    最活跃: 14:00-15:00 (2,341 次)

  今日热门按键
    1. 空格键          2,341  ████████████████████
    2. A键            1,892  ████████████████
    3. E键            1,543  █████████████
    4. 回车键            987  ████████
    5. 退格键            654  █████
    ...

  评估
    高强度打字日！你的手指很勤劳。
    太棒了！12天连续打卡！
==================================================
```

### 逐键统计

```bash
$ keystats-cli keys

==================================================
  逐键统计 - 2026年5月17日
==================================================

  热门按键 (共 62 种)
    按键                 |    次数 |   占比 | 柱状图
    ---------------------+----------+-------+--------------------
    空格键               |    2,341 | 18.2% | ██████████
    A键                  |    1,892 | 14.7% | ████████
    E键                  |    1,543 | 12.0% | ██████
    回车键               |      987 |  7.7% | ████
    退格键               |      654 |  5.1% | ██
    ...

  追踪总计: 12,847 次按键
  按键种类: 62
==================================================
```

---

## 项目架构

```
内核 evdev              守护进程                SQLite 数据库
/dev/input/event*  -->  keystats-daemon  -->  /var/lib/keystats/
                       (Python3)                keystats.db
                            |
                            v
                      systemd 服务
                      (开机自启)
                            ^
                            |
用户终端  -->  keystats-cli  (查询展示)
```

### 文件说明

| 文件 | 作用 |
|------|------|
| `daemon.py` | 后台守护进程，捕获键盘事件 |
| `db.py` | SQLite 数据库操作 |
| `cli.py` | 命令行界面，展示统计结果 |
| `keystats-daemon` | 守护进程启动脚本 |
| `keystats-cli` | CLI 启动脚本 |

---

## 数据库结构

### `keystats` — 每日总计
| 字段 | 类型 | 说明 |
|--------|------|-------------|
| `date` | TEXT (主键) | 日期，格式 YYYY-MM-DD |
| `key_count` | INTEGER | 当日总按键数 |
| `created_at` | TEXT | 首次记录时间 |
| `updated_at` | TEXT | 最后更新时间 |

### `hourly_stats` — 小时分布
| 字段 | 类型 | 说明 |
|--------|------|-------------|
| `date` | TEXT | 日期 |
| `hour` | INTEGER | 小时 (0-23) |
| `key_count` | INTEGER | 该小时按键数 |

### `key_type_stats` — 逐键统计
| 字段 | 类型 | 说明 |
|--------|------|-------------|
| `date` | TEXT | 日期 |
| `key_type` | TEXT | 按键名称 (如 `KEY_A`、`KEY_ENTER`) |
| `key_count` | INTEGER | 该按键按下次数 |

---

## 常见问题

### 服务无法启动

```bash
# 查看错误日志
sudo journalctl -xeu keystats.service --no-pager
sudo cat /var/log/keystats/daemon.log

# 常见原因1：缺少 python3-evdev
sudo apt-get install python3-evdev

# 常见原因2：权限问题
sudo chmod 777 /var/lib/keystats
sudo chmod 666 /var/lib/keystats/keystats.db
```

### 找不到键盘设备

```bash
# 检查设备是否存在
ls -la /dev/input/event*

# 检查是否能访问
python3 -c "from evdev import list_devices; print(list_devices())"

# 如为空，将用户加入 input 组
sudo usermod -a -G input $USER
# 然后重新登录
```

### 按键未被记录

1. 检查服务运行：`sudo systemctl status keystats`
2. 查看日志：`sudo cat /var/log/keystats/daemon.log`
3. 检查数据库：`sqlite3 /var/lib/keystats/keystats.db "SELECT * FROM keystats;"`

---

## 卸载

```bash
# 保留数据
sudo apt remove keystats

# 彻底删除（包括数据）
sudo apt purge keystats
```

---

## 隐私说明

**Keystats 不会记录你输入的内容。** 它只统计：

- 每个按键被按了多少次
- 按键的时间分布（按小时聚合）
- 每日总计

你的实际输入（密码、聊天内容、代码）**永远不会被保存、永远不会传输、永远不会被任何人访问**。所有数据仅保存在你本地的 SQLite 数据库中。

---

## 构建 .deb 包

```bash
# 安装构建工具
sudo apt-get install dpkg-dev

# 构建
cd keystats-project
dpkg-deb --build keystats

# 验证
dpkg-deb --info keystats_1.0.0_all.deb
```

---

## 调试模式

```bash
# 前台运行守护进程（不通过 systemd）
sudo /usr/bin/keystats-daemon --foreground

# 或直接用 Python
sudo python3 /usr/lib/keystats/daemon.py --foreground
```

---

## 开源协议

MIT 许可证 — 详见 LICENSE 文件。

---

## 致谢

- 使用 [python-evdev](https://github.com/gvalkov/python-evdev) 进行 Linux 输入事件处理
- 感谢开源社区的启发与支持
