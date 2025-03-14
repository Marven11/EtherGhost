# 游魂

![头图](./assets/social-preview.jpg)

<!-- social preview from https://pixabay.com/photos/fog-forest-conifers-trees-1535201/ -->

[English](./README_en.md) | [文档](./docs.md) | [下载绿色exe](https://github.com/Marven11/EtherGhost/releases) | [V我50](https://github.com/Marven11/Marven11/blob/main/buy_me_a_coffee.md)

游魂是一个开源的Webshell管理器，它提供更为方便的界面和更为简单易用的功能，可配合或代替其他webshell管理器，帮助用户在各类渗透场景中控制目标机器。

游魂不仅支持常见的一句话webshell以及常见Webshell管理器的功能，还支持添加冰蝎的webshell，以及将任何webshell提供给蚁剑进行连接的功能。通过使用游魂，用户可以使用蚁剑操控冰蝎webshell，在冰蝎webshell上使用蚁剑的各类插件，同时享受蚁剑的丰富生态以及冰蝎的流量加密和免杀特性。

游魂使用了B/S架构，用户可以将游魂架设在服务器上，通过本地浏览器进行连接，彻底移除了本地机器被感染的风险。

游魂自带上手即用RSA2048+AES256-CBC强加密，AES密钥在连接时生成并使用RSA加密传输，彻底阻止重放攻击和流量分析。

## 特点

- 同时支持PHP一句话webshell和冰蝎PHP webshell
- 流量防重放和流量强加密
- TCP正向代理
- 异步上传下载文件
- chunked transfer encoding分块发包
- 对接蚁剑
- 默认使用随机User Agent
- HTTP填充垃圾数据
- 自定义encoder和decoder
  - 支持导入部分蚁剑encoder和decoder
- 自定义主题和背景图片（？）
- 。。。。。。


## 预览

![preview](assets/preview-homepage.png)

![preview](assets/preview-terminal.png)

![preview](assets/preview-files.png)

## 当前功能

- 支持的webshell
  - PHP一句话
  - 冰蝎PHP
- webshell操作
  - 命令执行
    - 支持伪终端和普通的命令执行
  - 文件管理
    - 异步文件上传下载
  - PHP代码执行
  - TCP正向代理
  - 查看基本信息
  - 下载phpinfo
- webshell编码
  - HTTP参数混淆
  - 蚁剑类encoder和decoder
  - session暂存payload
  - 防流量重放
  - RSA+AES加密

## 安装使用

### Windows - 绿色exe

到[Release](https://github.com/Marven11/EtherGhost/releases)页面下载绿色exe即可

> 绿色exe会被Windows Defender报毒，虽然我也不知道为什么，但是建议有条件的人使用下面两种方法，直接运行源码或者手动打包exe

### Windows - 直接运行源码

如果用pip那同样是创建venv并激活，安装好所有依赖，然后运行`python -m ether_ghost`就行

如果用poetry则直接用poetry安装所有的依赖运行`python -m ether_ghost`就行

注意：下载源码的时候还是会被微软报毒，这是因为源码中的测试webshell文件被微软检测，可以直接删了整个`test_environment`文件夹，不影响程序运行

### Windows - 手动打包

创建venv，安装所有依赖，然后查阅[pyinstaller_package.bat](./pyinstaller_package.bat)文件，将里面的虚拟环境路径换成你的`site-packages`文件夹，最后运行即可。

注意：如果之前打包过旧版本的话可能需要重新创建venv

### Linux - 使用pip

```shell
pip install ether-ghost
ether_ghost # 启动
# 或者python -m ether_ghost
```

### Linux - 使用pip+venv

安装并打开：

```shell
cd EtherGhost
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m ether_ghost
```

使用：

```shell
cd EtherGhost
. .venv/bin/activate
python -m ether_ghost
```

### Linux - 使用poetry

安装并打开：

```shell
cd EtherGhost
poetry install
poetry shell
python -m ether_ghost
```

使用：

```shell
cd EtherGhost
poetry shell
python -m ether_ghost
```

## 为什么不用蚁剑？

我自从学习渗透开始就一直在用蚁剑，蚁剑是一个非常优秀的webshell管理器，但是在我想要二开蚁剑的时候才发现蚁剑的架构存在一些问题，无法实现我想要的功能。具体来说：

- 蚁剑基于早已过时的Electron 4，其Chromium内核存在多个安全漏洞，存在被反制的风险。同时Electron 4的开发环境难以配置，给二开带来困难。
- 蚁剑的PHP webshell不支持GET参数传参，在CTF环境下较为不便
  - 这里虽然可以在GET参数下指定eval另一个POST参数，但是有这时间填参数为什么不去直接拿flag？
- 蚁剑使用的Electron导致XSS漏洞极易被提升为RCE漏洞，导致攻击机被反制
- 蚁剑的encoder需要经过复杂配置之后才可支持AES和RSA加密
- 虽然蚁剑可以使用php_raw配合encoder连接冰蝎webshell，但蚁剑的插件生态仅支持php类型的webshell，无法在冰蝎webshell上使用各类插件

蚁剑的encoder生态和插件生态还是很丰富的，encoder可以通过让python调用nodejs直接使用，插件移植难度比较大，可以让游魂假装是一个webshell，接受蚁剑传来的代码就可以解决。

## 为什么不用冰蝎？

冰蝎可以选择AES CBC加密或者异或加密，看起来是给payload上了强加密，无法被检测。但是异或加密存在一些密码学上的缺陷，导致中间人只要利用异或的一些特性就能直接得到密码，进而解密所有payload

那AES CBC呢？它总该安全了吧？并不，冰蝎在使用AES CBC的时候使用了全0的iv, 导致AES CBC退化，失去随机性（尤其是前16个字节），也存在一些密码学的缺陷，极易被中间人检出。而且冰蝎使用AES的缺陷是写死在webshell文件中，暂时无法使用其他手段解决的。

如果需要真正的强加密可以考虑在游魂上使用冰蝎的php webshell, 并打开强加密选项，可以随机化大部分请求的内容，缓解这个问题。

## TODO

- 对接蚁剑、冰蝎、哥斯拉
  - [done] 导入冰蝎webshell
  - 从哥斯拉的本地数据库导入哥斯拉webshell
  - 从蚁剑的本地目录导入蚁剑webshell
  - 从冰蝎的本地目录导入冰蝎webshell
  - [done] 以webshell形式对接蚁剑
- 游魂专用的webshell类型
  - 一键生成webshell
  - padding功能
  - 流量混淆
    - 4B head 8B xor密钥 nB实际的payload 4B tail
  - 可选生成带公钥的webshell, 即使有源码也骑不上
- i18n
- 改进文件管理的文件夹管理功能
- 支持冰蝎4.1的自定义类型webshell
- 批量测试webshell是否存活
- 数据库连接功能
- 写安装使用的文档，然后把文档分割为多个文件，存到`docs/`里
- 让用户决定是否将AES密钥在session中持久化，当前审计可以通过提取目标机上的session解密流量
- 加密（或者至少混淆的）反弹Shell
  - 可以用类似TCP正向代理的思路搞
  - 或者绑定本地端口等着目标连过来
- [done] 下载phpinfo
- [done] 显示机器信息
- [done] 真正的正向代理和~~反向代理~~
  - PHP貌似很难支持绑定本地端口
- [done] pyinstaller打包，给windows用户提供一个绿色的exe

## 关于流量强加密功能

流量强加密功能一开始是为了AWD设计的，主要目标是防止流量重放，以及防止流量分析分析出实际执行的操作。打开流量强加密之后流量分析端理论上能分析出webshell的存在，能分析出加解密相关的PHP代码，而不能分析出具体执行的命令或代码。

当然流量强加密是存在一些问题的。当前的流量加解密和整个握手功能都需要在目标上执行代码，这个过程对中间人来说是完全透明的。虽然中间人不知道具体执行的代码，但是可以分析出握手时传递的代码，从而查杀webshell.

当然这个功能是可以改进的。只要把握手过程藏到webshell源码里，像冰蝎一样先解密再运行就好了。但是这样的话就需要改进传统一句话木马，也许需要推出游魂特定的webshell.

目前除了常规功能更新还有增加流量混淆webshell的计划，计划是将webshell流量伪装成图片上传等流量，可以随着上述功能添加。

## 赞助

这里空空如也

## 免责声明

```
本声明适用于任何使用本工具的个人或组织。在进行任何网络安全活动之前，请仔细阅读并理解以下声明：

1. 目的：本声明的目的是提醒和教育用户，网络安全攻击有潜在违法风险且可能对他人造成损害。通过使用该工具或技术，您确认您已理解并承担使用该工具或技术所带来的一切风险。

2. 合法性：请注意，未经授权的网络安全攻击是违法的，并且可能会导致法律后果。本工具不鼓励或支持任何非法活动。用户需要确保自己的行为符合适用的法律和道德准则。

3. 授权：使用网络安全攻击工具或技术应遵守授权范围以及适用的法律和法规。未经授权的访问或干涉他人的网络、系统或数据是违法的，用户需要获得适当的授权才能进行相关活动。

4. 免责：本工具的源代码完全开源，使用该工具或技术的风险由用户自行承担。对于因使用该工具或技术而产生的任何直接或间接损害，包括但不限于数据丢失、系统瘫痪、法律责任或任何其他损失，我们不承担任何责任。

5. 教育目的：本工具仅供教育和研究目的使用，并且在遵守适用法律和法规的前提下，用于合法的安全测试、渗透测试或其他授权的活动。

6. 共享责任：用户应意识到网络安全是一个共同责任，使用本工具时应始终保证他人的利益和隐私不受损害。

请用户谨慎使用本工具，并确保始终合法、道德和负责任地进行网络安全活动。
```
