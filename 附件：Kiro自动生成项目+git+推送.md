# 完整操作：GitHub Token 生成 + 本地环境变量配置

## 一、生成 GitHub Personal Access Token (PAT)（浏览器操作）

### 步骤 1：进入 GitHub Token 生成页面

1. 打开浏览器，登录你的 GitHub 账号（jjdayj）；

2. 点击右上角头像 → 选择「Settings」（设置）；

3. 在左侧菜单栏拉到最底部，点击「Developer settings」（开发者设置）；

4. 继续点击左侧「Personal access tokens」→ 选择「Tokens (classic)」（经典 Token，必须选这个，新版 Token 配置更复杂）；

5. 点击右上角「Generate new token (classic)」（生成新的经典 Token）。

### 步骤 2：配置 Token 权限和有效期

1. **Note（备注）**：输入一个易记的名称，比如「AI-Development - 自动创库」（方便后续识别用途）；

2. Expiration（有效期）

   ：

   - 选「No expiration」（永不过期，推荐，避免后续频繁重新生成）；
   - 若担心安全，也可选 30/90 天，到期后重新生成即可；

   

3. Scopes（权限）

   ：

   - 必须勾选 `repo` 分类下的**所有选项**（这是创建仓库、推送代码的核心权限）；

   - 其他权限无需勾选（避免权限过大）；

     

   
   
   
4. 拉到页面最底部，点击「Generate token」（生成 Token）。

### 步骤 3：保存 Token（关键！仅显示一次）

1. 生成成功后，页面会显示一串以 `ghp_` 开头的字符串（比如 `ghp_8X7Y6Z5A4B3C2D1E0F9G8H7J6K5L4M3N2B1`）；

2. **立即复制**：点击 Token 右侧的复制按钮，或手动选中复制；

3. 安全保存

   ：粘贴到记事本 / 密码管理器中（一旦关闭页面，Token 将永久无法查看，只能重新生成）；

   

   ⚠️ 重要提醒：Token 等同于 GitHub 密码，不要分享给任何人，不要上传到代码仓库！

## 二、配置本地环境变量（Windows + Kiro 终端操作）

### 方式 1：通过 Kiro 终端配置（推荐，仅需执行一次）

1. 打开 Kiro 软件，调出终端（快捷键：Ctrl +・或 点击左下角「终端」图标）；

2. 确保终端是 **PowerShell 环境**（Kiro 默认就是，无需切换）；

3. 执行以下命令（把 

   ```
   你的Token
   ```

    替换为刚才复制的 ghp_ 开头字符串）：

   powershell

   

   

   ```
   # 配置用户级环境变量（仅当前用户生效，无需管理员权限）
   [Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "ghp_8X7Y6Z5A4B3C2D1E0F9G8H7J6K5L4M3N2B1", "User")
   ```
   
   
   
4. 执行后无报错即配置成功（终端不会输出内容，这是正常的）；

5. **必须重启 Kiro**：关闭 Kiro 所有窗口（包括后台），重新打开，环境变量才会生效。

### 方式 2：手动在系统设置中配置（备选，可视化操作）

若终端命令执行失败，可手动配置：

1. 按下 Win + R，输入 `sysdm.cpl`，回车打开「系统属性」；

2. 点击「高级」选项卡 → 点击「环境变量」；

3. 在「用户变量」区域（上方），点击「新建」；

   - 变量名：`GITHUB_TOKEN`（必须大写，和脚本中一致）；

   - 变量值：粘贴你的 Token（ghp_ 开头的字符串）；

     

     ![img](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%27400%27%20height=%27256%27/%3e)

     ![image](https://img-blog.csdnimg.cn/20240105103510987.png)

     

     （示意图）

   

4. 点击「确定」保存（需点击 3 次确定，关闭所有弹窗）；

5. 重启 Kiro 生效。

## 三、验证 Token 是否配置成功

1. 重新打开 Kiro 终端，执行以下命令：

   powershell

   

   

   

   

   

   ```
   # 读取环境变量，验证Token是否存在
   $env:GITHUB_TOKEN
   ```

   

2. 若终端输出你的 Token 字符串（ghp_ 开头），说明配置成功；

3. 若输出为空，检查：

   - 变量名是否为 `GITHUB_TOKEN`（大小写一致）；
   - 是否重启了 Kiro；
   - Token 是否复制正确（无多余空格）。

   

## 四、Token 失效 / 重新生成的处理

若后续 Token 失效（比如权限变更、泄露），按以下步骤处理：

1. 回到 GitHub Token 页面（Settings → Developer settings → Personal access tokens → Tokens (classic)）；
2. 找到旧 Token，点击「Revoke」（撤销）；
3. 按「步骤一」重新生成新 Token；
4. 按「步骤二」重新配置环境变量（覆盖旧值）；
5. 重启 Kiro 即可。

------

### 总结

1. **Token 生成核心**：必须选「Tokens (classic)」+ 勾选 `repo` 全权限 + 保存好生成的字符串；
2. **环境变量配置核心**：变量名固定为 `GITHUB_TOKEN`，配置后必须重启 Kiro；
3. **验证关键**：执行 `$env:GITHUB_TOKEN` 能输出 Token 即配置成功；
4. **安全提醒**：Token 不要泄露，若担心可设置有效期，到期重新生成。

配置完成后，你执行 `/ai-dev` 指令时，Kiro 会自动读取这个 Token，帮你一键创建远端 GitHub 仓库，无需手动操作。