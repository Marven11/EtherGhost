# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 让各个webshell都支持发送HTTP请求
  - 这是一个很大的重构，修改代码前需要输出markdown规划，修改代码后需要使用pyright检查
  - 发送HTTP请求功能
    - 让攻击者可以通过webshell发送HTTP请求
  - 修改SessionInterface使其支持定义http请求
    - 函数输入: url, method, header, param, data
    - 函数返回一个typeddict，包含: status code, header, body
  - 修改各个webshell/反弹shell的实现，让它们支持发送HTTP请求
    - PHP使用curl模块而非curl命令/Linux Shell使用curl命令，JSP尝试使用java内置库发送HTTP请求
    - 应该检查curl库是否存在、curl命令是否存在
  - 修改api使其暴露这个功能
- [ ] 测试
  - 启动当前项目
  - 上传test_environment到secret中的dell nixos主机，搭建测试docker+php 7.4环境
    - 使用scp上传文件到/tmp
    - 启动测试docker环境
    - 尝试访问index.html和shell.php测试是否可以使用
  - 使用当前项目通过IP连接搭建的shell.php测试webshell，随意发送一个HTTP请求获得结果
  - 暂时不需要测试jsp的HTTP请求功能

# 暂时搁置

无