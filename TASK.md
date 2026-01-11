# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 我们需要准备开始重构前端，首先需要跑通同时启动前端和后端的流程
  - 你需要完成以下流程
  - 在终端启动ether_ghost服务端，使用--no-browser以只启动api服务
  - 进入frontend/在另一个终端启动npm run dev
  - 连接浏览器mcp并访问npm run dev提示的端口
  - 导出截图，查看截图报告是否看到界面
    - 界面上半部分20-30%有大块绿色圆角矩形header,其中左边有软件名，右边有一排按钮


# 暂时搁置

- [ ] 重构当前的右键菜单系统
- [ ] 添加批量测试webshell的功能 - 得先重构当前的右键菜单系统
