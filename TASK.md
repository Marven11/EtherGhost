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
  - 需要用浏览器测试右键点击对应元素，用js检查是否弹出对应的右键菜单
  - 需要将右键菜单截图，询问qwen界面排布是否正常
    - 期望：
      - 右键菜单为一个圆角矩形，其中有多行内容，每行内容有各自的图标和文本
      - 如果有二级选项：二级选项背景更深
    - 分别截图并询问：
      - 单纯的右键菜单
      - 展开某个二级菜单

# 暂时搁置

- [ ] 添加批量测试webshell的功能 - 得先重构当前的右键菜单系统
- [ ] 通过api访问当前“测试dell nixos”webshell是否可以使用
- [ ] 重构，统一创建PHP webshell和反弹shell的逻辑
  - 这是一个巨大的重构，需要完全替换项目的核心逻辑，需要仔细思考，大量修改
  - 重构不应该修改数据库保存格式，必须使用原有的表结构读取webshell信息
  - 问题
    - 当前php webshell等session可以直接通过init函数创建，但是反弹shell则需要通过ReverseShellConnector连接
  - 任务
    - 将所有session都统一为通过connector连接
    - 需要重新设计SessionConnector的逻辑：运行、列出session，根据uuid获得session
      - 有些connector支持添加session配置，例如添加php webshell连接配置，但是诸如反弹shell connector等则不支持，只能等待目标反向连接以获得session
    - 重构session_type_info等旧的，用于直接构建session的逻辑
  - 需要仔细规划以下问题
    - api如何通过session connector获得每个session type的定义
    - session connector如何设置
    - api在构建session时如何通过session connector获得session的实例
- [ ] 再次通过api访问当前“测试dell nixos”webshell是否可以使用

# 注意

- 使用nix develop --command poetry run python -m ether_ghost --no-browser启动API服务器，不要自动带起浏览器
- 测试前端时，先在一个终端中启动API服务器，再进入frontend/在另一个终端启动npm run dev
- 缺少frontend/时: 使用nix develop --command poetry run build-frontend构建前端
- 需要在浏览器中右键元素时：使用event而非.click函数
- 使用浏览器时避免使用verbose查看html

