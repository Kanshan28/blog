---
layout: post
title: Shell中if的-e,-d,-f使用
slug: 2020-04-30-Linux-shell中if的使用
date: 2020-4-30 22:55
status: publish
author: Kanshan
categories: 
  - Linux_shell_if
tags:
  - Shell
excerpt: Shell编程中用来判断的一些参数说明
---



![wallhaven-478940.jpg](https://upload-images.jianshu.io/upload_images/3507931-2100088cfcf436c8.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

- **文件比较运算符** `if [参数]`

For example
```
if [ -e /etc/systemd/system/getty@tty1.service.d ]
then
	echo "login file is exist"
else
    mkdir "/etc/systemd/system/getty@tty1.service.d"
fi
```
| 序号 |      参数       |              说明               |
| :--: | :-------------: | :-----------------------------: |
|  1   |   -e filename   |    如果 filename存在，则为真    |
|  2   |   -d filename   |   如果 filename为目录，则为真   |
|  3   |   -f filename   | 如果 filename为常规文件，则为真 |
|  4   |   -L filename   | 如果 filename为符号链接，则为真 |
|  5   |   -r filename   |    如果 filename可读，则为真    |
|  6   |   -w filename   |    如果 filename可写，则为真    |
|  7   |   -x filename   |   如果 filename可执行，则为真   |
|  8   |   -s filename   |    如果文件长度不为0，则为真    |
|  9   |   -h filename   |    如果文件是软链接，则为真     |
|  10  | file1 -nt file2 |  如果 file1比 file2新，则为真   |
|  1   | file1 -ot file2 |  如果 file1比 file2旧，则为真   |

- **整数变量表达式**`if [参数]`

| 序号 | 参数 |   说明   |
| :--: | :--: | :------: |
|  1   | -eq  |   等于   |
|  2   | -ne  |  不等于  |
|  3   | -gt  |   大于   |
|  4   | -ge  | 大于等于 |
|  5   | -lt  |   小于   |
|  6   | -le  | 小于等于 |

- **字符串变量表达式** `if [参数]`

| 序号 |           参数            |                说明                |
| :--: | :-----------------------: | :--------------------------------: |
|  1   |          `$a=$b`          |   如果string1等于string2，则为真   |
|  2   | ` $string1 !=  $string2 ` |  如果string1不等于string2，则为真  |
|  3   |       `-n $string`        | 如果string 非空(非0），返回0(true) |
|  4   |       ` -z $string`       |      如果string 为空，则为真       |
|  5   |         `$sting`          | 如果string 非空，返回0 (和-n类似)  |
|  6   |        `! 表达式`         |      条件表达式的相反[逻辑非]      |
|  7   |  `表达式1  –a  表达式2`   |      条件表达式的并列[逻辑与]      |
|  8   |  `表达式1  –o  表达式2`   |       条件表达式的或[逻辑或]       |

- **特殊变量** `if [参数]`

| 序号 | 参数 |                             说明                             |
| :--: | :--: | :----------------------------------------------------------: |
|  1   |  $0  |                       当前脚本的文件名                       |
|  2   |  $n  | 传递给脚本或函数的参数。n 是一个数字，表示第几个参数。例如，第一个参数是$1，第二个参数是$2 |
|  3   |  $#  |                  传递给脚本或函数的参数个数                  |
|  4   |  $*  |                  传递给脚本或函数的所有参数                  |
|  5   |  $@  | 传递给脚本或函数的所有参数。被双引号(" ")包含时，与 $* 稍有不同 |
|  6   |  $?  |              上个命令的退出状态，或函数的返回值              |
|  7   |  $$  |  当前Shell进程ID。对于 Shell 脚本，就是这些脚本所在的进程ID  |
|  8   |  $!  | Shell最后运行的后台Process的PID(后台运行的最后一个进程的[进程ID](https://www.baidu.com/s?wd=%E8%BF%9B%E7%A8%8BID&tn=SE_PcZhidaonwhc_ngpagmjz&rsv_dl=gh_pc_zhidao)号) |
- 参考处[```Shell特殊变量：Shell $0, $#, $*, $@, $?, $$和命令行参数```]