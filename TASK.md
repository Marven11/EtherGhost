# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 测试上一个commit添加的http发送请求功能
  - [ ] php和linux shell的已经检查过，需要检查jsp的
  - [ ] 在dell nixos的/tmp文件夹写一个有漏洞的spring项目，支持被攻击者上传jsp shell
  - [ ] 使用docker在dell nixos上搭建那个有漏洞的spring项目，然后从当前机器访问
  - [ ] 尝试上传恶意的test_environment/shell.jsp
  - [ ] 启动ether_ghost，尝试配置刚刚上传的恶意jsp shell并测试基本功能
  - [ ] 尝试http发送请求功能

# 暂时搁置

无