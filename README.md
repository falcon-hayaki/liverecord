# 自用录播脚本

## 环境配置

```shell
bash install.sh
```

安装完成后自行配置`rclone`和`BaiduPCS`

## Usage

> 录播的频道配置在`resources/`下参考已有的文件。<br>脚本执行入口程序为`run.py`

```shell
bash start.sh "-l yukine"
```

参数说明

* `-l`, `-record_list`, 指定脚本执行的参数配置文件，传入不带文件后缀的文件名。默认为`run`