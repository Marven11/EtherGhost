# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 你刚刚在commit 6733a5f实现了新的右键菜单，现在需要用其替换掉原有的右键菜单
  - 直接删除ClickMenu.vue和ClickMenuManager
  - 重写所有用到ClickMenu.vue的地方
  - 需要规划测试清单到NOTES.md以全面测试所有功能
  - 需要将右键菜单截图，询问qwen界面排布是否正常
    - 期望：
      - 右键菜单为一个圆角矩形，其中有多行内容，每行内容有各自的图标和文本
      - 如果有二级选项：二级选项背景更深
    - 分别截图并询问：
      - 单纯的右键菜单
      - 展开某个二级菜单

# 暂时搁置

- [ ] 添加批量测试webshell的功能 - 得先重构当前的右键菜单系统

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 使用浏览器时避免使用verbose查看html

