# 环境

这里是EtherGhost的源码，EtherGhost是一个webshell管理器，支持PHP Linux Shell JSP等webshell

EtherGhost在启动后会对外提供API，并且尝试启动用户的浏览器管理

EtherGhost使用poetry管理代码，使用pyright保证代码质量

这个项目没有在MacOS上测试过，需要注意兼容性

# 任务

- [ ] 我们要重构主页等的右键菜单
  - 开始前：先启动API服务器和npm run dev
  - 目标：编写ClickMenuDualLayer
    - 包含ClickMenuManager和frontend/src/components/ClickMenu.vue的功能
    - 代码极简易懂可维护
  - 当前问题
    - 上层需要手动控制右键菜单的开启和关闭
  - 当前header行为
    - 点击按钮时出现右键菜单clickMenuRightClick/clickMenuOthers
    - clickMenuRightClick: 包含选项“打开”/“在新标签页打开”
    - clickMenuOthers
      - 包含更多功能，如“对接蚁剑”
      - 右键对接蚁剑等弹出clickMenuOthersRightClick，覆盖当前右键菜单
    - clickMenuOthersRightClick
      - 包含选项“打开”/“在新标签页打开”
  - 重新设计
    - CSS保持基本不变
    - 有一列选项，选项：
      - 支持自定义图标、文本、颜色和点击时的行为
    - 选项分为两种：有些点击之后直达对应功能，有些点击之后展开二级菜单
    - 二级菜单
      - 点击二级菜单选项后会展开二级菜单，在选项的下面新增一系列子选项，再次点击时折叠
      - 子选项背景更黑，样式基本不变
  - 应用到header上
    - 右键点击按钮时出现右键菜单
    - 对接蚁剑等本来会弹出clickMenuOthersRightClick的选项改为二级菜单，点击时展开显示“打开”/“在新标签页打开”
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

