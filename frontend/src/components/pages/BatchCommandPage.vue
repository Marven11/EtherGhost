<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import IconHash from "@/components/icons/iconHash.vue";
import IconFileDownload from "@/components/icons/iconFileDownload.vue";
import IconRun from "@/components/icons/iconRun.vue";
import { addPopup, getCurrentApiUrl, parseDataOrPopupError } from "@/assets/utils";

const router = useRouter();
const webshells = ref([]);
const commandInput = ref("");
const isExecuting = ref(false);
const hasNoData = ref(false);

// 加载选中的webshell数据
function loadSelectedWebshells() {
  try {
    const batchData = localStorage.getItem('batch_command_selection');
    console.log('从localStorage读取的数据:', batchData); // 添加调试日志
    if (batchData) {
      const data = JSON.parse(batchData);
      console.log('解析后的数据:', data); // 添加调试日志
      
      // 转换数据格式
      webshells.value = data.selectedSessions.map(session => ({
        id: session.id,
        name: session.name,
        type: session.type,
        readable_type: session.readable_type || session.type,
        location: session.location || "未知位置",
        note: session.note || "",
        status: "pending",
        result: "等待执行命令...",
        timestamp: ""
      }));
      console.log('转换后的webshells:', webshells.value); // 添加调试日志
      
      // 清除存储的数据 - 暂时注释掉以测试刷新
      // localStorage.removeItem('batch_command_selection');
      console.log('已读取localStorage数据，但不清除以测试刷新'); // 修改日志
      hasNoData.value = false;
    } else {
      // 如果没有传递数据，显示空状态
      console.log('未找到batch_command_selection数据'); // 添加调试日志
      webshells.value = [];
      hasNoData.value = true;
      return;
    }
  } catch (error) {
    console.error("加载选中webshell数据失败:", error);
    addPopup("red", "错误", "加载选中webshell数据失败喵~");
    webshells.value = [];
    hasNoData.value = true;
  }
}

// 执行命令
async function executeCommand() {
  if (!commandInput.value.trim()) {
    addPopup("red", "错误", "请输入要执行的命令喵~");
    return;
  }

  isExecuting.value = true;
  const command = commandInput.value.trim();
  
  // 更新所有webshell状态为执行中
  for (const webshell of webshells.value) {
    webshell.status = 'executing';
    webshell.result = '执行中...';
    webshell.timestamp = '';
  }

  try {
    // 并发执行所有webshell的命令
    const executionPromises = webshells.value.map(async (webshell) => {
      try {
        // 调用后端API执行命令 - 使用正确端点
        const response = await axios.get(
          `${getCurrentApiUrl()}/session/${webshell.id}/execute_cmd`,
          { params: { cmd: command } }
        );
        
        const result = parseDataOrPopupError(response);
        // parseDataOrPopupError成功返回，意味着code为0，执行成功
        webshell.status = 'success';
        webshell.result = result || "无输出"; // result是字符串输出
        webshell.timestamp = ""; // 后端未提供执行时间
        webshell.return_code = 0; // 默认成功返回码为0
      } catch (error) {
        console.error(`执行webshell ${webshell.id} 命令失败:`, error);
        webshell.status = 'error';
        webshell.result = error.message || "网络请求失败";
        webshell.timestamp = "";
        webshell.return_code = 1;
      }
    });

    // 等待所有执行完成
    await Promise.all(executionPromises);
    
    addPopup("green", "执行完成", "批量命令执行已完成喵~");
  } catch (error) {
    console.error("批量执行命令失败:", error);
    addPopup("red", "执行失败", "批量命令执行过程中发生错误喵~");
  } finally {
    isExecuting.value = false;
  }
}

// 导出结果
function exportResults() {
  const exportData = {
    command: commandInput.value,
    timestamp: new Date().toISOString(),
    webshells: webshells.value.map(ws => ({
      id: ws.id,
      name: ws.name,
      type: ws.type,
      status: ws.status,
      result: ws.result,
      timestamp: ws.timestamp,
      return_code: ws.return_code,
      location: ws.location
    }))
  };
  
  const dataStr = JSON.stringify(exportData, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  
  const downloadUrl = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = `batch-command-results-${Date.now()}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(downloadUrl);
  
  addPopup("green", "导出成功", "执行结果已导出为JSON文件喵~");
}

// 复制到剪贴板
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    addPopup("green", "复制成功", "内容已复制到剪贴板喵~");
  }).catch(err => {
    addPopup("red", "复制失败", "无法复制到剪贴板喵~");
  });
}

// 获取类型代码
function getTypeCode(typeName) {
  const typeMap = {
    'Linux命令执行': 'LINUX_CMD_ONELINER',
    'PHP一句话': 'ONELINE_PHP',
    'JSP一句话': 'ONELINE_JSP'
  };
  return typeMap[typeName] || typeName;
}

// 确保类型显示正确
function ensureTypeDisplay() {
  // 确保每个webshell都有readable_type
  for (const webshell of webshells.value) {
    if (!webshell.readable_type) {
      webshell.readable_type = webshell.type;
    }
  }
}

// 在mounted中调用
onMounted(() => {
  setTimeout(() => {
    loadSelectedWebshells();
    ensureTypeDisplay();
  }, 100); // 延迟加载确保数据传递完成
});

// 重置状态
function resetStatus() {
  for (const webshell of webshells.value) {
    webshell.status = 'pending';
    webshell.result = '等待执行命令...';
    webshell.timestamp = '';
    webshell.return_code = null;
  }
  commandInput.value = '';
}
</script>

<template>
  <div class="batch-command-page">
    <div class="page-header">
      <h1 class="page-title">批量执行命令</h1>
      <div class="page-subtitle">选择多个webshell并发执行相同命令喵~</div>
    </div>
    
    <div class="main-scroll-area">
      <div class="webshell-list-header">
        <div class="header-status">状态</div>
        <div class="header-info">WebShell信息</div>
        <div class="header-result">执行结果</div>
      </div>
      
      <div class="webshell-list">
        <div v-if="hasNoData" class="empty-state">
          <div class="empty-message">未选中任何webshell喵~</div>
        </div>
        <div v-else>
          <div 
            class="webshell-row" 
            v-for="webshell in webshells" 
            :key="webshell.id"
            :class="webshell.status"
          >
            <!-- 状态指示区 -->
            <div class="status-area">
              <div 
                class="status-indicator" 
                :class="webshell.status"
                :title="webshell.status === 'pending' ? '未开始' : webshell.status === 'executing' ? '执行中' : webshell.status === 'success' ? '成功' : '失败'"
              ></div>
            </div>
            
            <!-- WebShell信息区 -->
            <div class="info-area">
              <div class="info-main">
                <div class="webshell-name">{{ webshell.name }}</div>
                <div class="session-type-dot">
                  <div :data-type="getTypeCode(webshell.type)"></div>
                </div>
                <div class="webshell-type-label">{{ webshell.readable_type || webshell.type }}</div>
              </div>
              <div class="info-details">
                <span class="webshell-note" v-if="webshell.note">{{ webshell.note }}</span>
                <span class="webshell-location" v-if="webshell.location">{{ webshell.location }}</span>
              </div>
            </div>
            
            <!-- 结果区 -->
            <div class="result-area">
              <div class="result-content" :class="webshell.status">
                <div class="output-section" v-if="webshell.status !== 'pending' && webshell.status !== 'executing'">
                  <div class="output-text" @click="copyToClipboard(webshell.result)" title="点击复制">{{ webshell.result }}</div>
                </div>
                <div class="status-text" v-else>{{ webshell.status === 'executing' ? '执行中...' : '等待执行...' }}</div>
                <div class="meta-section" v-if="webshell.status !== 'pending' && webshell.status !== 'executing'">
                  <span class="meta-item return-code" :class="webshell.return_code === 0 ? 'success' : 'error'">
                    <span class="meta-icon">{{ webshell.return_code === 0 ? '✓' : '✗' }}</span>
                    <span class="meta-text">返回码: {{ webshell.return_code }}</span>
                  </span>
                  <span class="meta-separator" v-if="webshell.timestamp">•</span>
                  <span class="meta-item timestamp" v-if="webshell.timestamp">
                    <span class="meta-icon">⏱</span>
                    <span class="meta-text">{{ webshell.timestamp }}</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="command-footer">
      <div class="command-input-wrapper">
        <div class="input-icon">$</div>
        <input
          v-model="commandInput"
          type="text"
          class="command-input"
          placeholder="输入要批量执行的命令，例如：ls -la /tmp"
          :disabled="isExecuting"
        />
      </div>
      
      <div class="action-buttons">
        <button 
          class="action-button execute-button" 
          @click="executeCommand"
          :disabled="isExecuting || !commandInput.trim()"
          title="执行命令"
        >
          <IconRun class="button-icon" />
        </button>
        
        <button 
          class="action-button export-button" 
          @click="exportResults"
          :disabled="webshells.every(ws => ws.status === 'pending')"
          title="导出结果"
        >
          <IconFileDownload class="button-icon" />
        </button>
        
        <button 
          class="action-button reset-button" 
          @click="resetStatus"
          :disabled="isExecuting"
          title="重置状态"
        >
          <span class="reset-icon">↺</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.batch-command-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  padding: 20px 24px;
  box-sizing: border-box;
  background-color: var(--background-color-1);
  color: var(--font-color-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--font-color-primary);
  margin: 0 0 4px 0;
  letter-spacing: -0.2px;
}

.page-subtitle {
  font-size: 13px;
  color: var(--font-color-secondary);
  opacity: 0.7;
  margin: 0;
}

.main-scroll-area {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
  border-radius: 14px;
  background-color: var(--background-color-2);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.webshell-list-header {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background-color: rgba(0, 0, 0, 0.03);
  font-size: 13px;
  font-weight: 600;
  color: var(--font-color-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.header-status {
  width: 100px;
  padding-left: 8px;
}

.header-info {
  flex: 1;
}

.header-result {
  flex: 2;
  text-align: right;
  padding-right: 12px;
}

.webshell-list {
  display: flex;
  flex-direction: column;
}

.webshell-row {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  transition: all 0.25s ease;
  min-height: 68px;
}

.webshell-row:hover {
  background-color: var(--background-color-3);
}

.webshell-row:last-child {
  border-bottom: none;
}

.webshell-row:hover {
  background-color: var(--background-color-3);
}



.status-area {
  width: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0 8px;
}

.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  margin-bottom: 6px;
  position: relative;
}

.status-indicator.pending {
  background-color: transparent;
  border: 2px solid var(--font-color-secondary);
  opacity: 0.4;
}

.status-indicator.executing {
  background-color: var(--yellow);
  animation: subtle-pulse 1.5s infinite;
  box-shadow: 0 0 6px rgba(255, 193, 7, 0.5);
}

.status-indicator.success {
  background-color: var(--green);
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.4);
}

.status-indicator.error {
  background-color: var(--red);
  box-shadow: 0 0 8px rgba(244, 67, 54, 0.4);
}

@keyframes subtle-pulse {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}



.info-area {
  flex: 1;
  padding: 0 16px;
  border-right: 1px solid var(--border-color);
  margin-right: 16px;
  min-height: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.info-main {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.webshell-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--font-color-primary);
  margin-right: 12px;
  letter-spacing: -0.2px;
}

.session-type-dot {
  width: 1rem;
  height: 1rem;
  margin-right: 0;
}

.session-type-dot div {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 20px;
  margin: 0.25rem;
  margin-left: 0rem;
  background-color: var(--white);
}

.session-type-dot div[data-type="ONELINE_PHP"],
.session-type-dot div[data-type="BEHINDER_PHP_AES"],
.session-type-dot div[data-type="BEHINDER_PHP_XOR"] {
  background-color: var(--color-php);
}

.session-type-dot div[data-type="ONELINE_JSP"],
.session-type-dot div[data-type="BEHINDER_JSP_AES"] {
  background-color: var(--color-java);
}

.session-type-dot div[data-type="LINUX_CMD_ONELINER"] {
  background-color: var(--color-shell);
}



.webshell-type-label {
  font-size: 12px;
  color: var(--font-color-secondary);
  font-weight: 500;
  letter-spacing: 0.2px;
  opacity: 0.8;
}

.info-details {
  font-size: 13px;
  color: var(--font-color-secondary);
  display: flex;
  gap: 12px;
}

.webshell-note {
  opacity: 0.9;
}

.webshell-location {
  opacity: 0.7;
}

.result-area {
  flex: 2;
  padding: 0 12px;
  min-height: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.result-content {
  text-align: right;
}

.output-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--font-color-primary);
  margin-bottom: 2px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  word-break: break-all;
  line-height: 1.4;
  cursor: pointer;
  transition: all 0.2s ease;
  background-color: var(--background-color-3);
  padding: 6px 12px;
  border-radius: 20px;
}

.webshell-row.success .output-text {
  background-color: rgba(76, 175, 80, 0.15);
  color: #4CAF50;
}

.webshell-row.error .output-text {
  background-color: rgba(244, 67, 54, 0.15);
  color: #F44336;
}

.output-text:hover {
  background-color: var(--background-color-2);
  transform: scale(1.02);
}

.status-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--font-color-secondary);
  margin-bottom: 4px;
  font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
  word-break: break-all;
  line-height: 1.4;
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  background-color: var(--background-color-3);
}

.webshell-row.executing .status-text {
  color: #FF9800;
  background-color: rgba(255, 152, 0, 0.15);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.8; }
  50% { opacity: 1; }
  100% { opacity: 0.8; }
}

.webshell-row.success .output-text {
  color: var(--green);
}

.webshell-row.error .output-text {
  color: var(--red);
}

.meta-section {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'SF Mono', monospace;
}

.return-code.success {
  color: #4CAF50 !important;
  background-color: rgba(76, 175, 80, 0.15) !important;
}

.return-code.error {
  color: #F44336 !important;
  background-color: rgba(244, 67, 54, 0.15) !important;
}

.timestamp {
  color: var(--font-color-secondary) !important;
  background-color: var(--background-color-3) !important;
}

.meta-icon {
  font-size: 10px;
  opacity: 0.9;
}

.meta-text {
  font-weight: 500;
  color: inherit;
}

.meta-separator {
  color: var(--font-color-secondary);
  opacity: 0.5;
}

.command-footer {
  background-color: var(--background-color-2);
  border-radius: 14px;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.command-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background-color: var(--background-color-3);
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

.command-input-wrapper:focus-within {
  border-color: var(--green);
  box-shadow: 0 0 0 4px rgba(76, 175, 80, 0.2);
  background-color: var(--background-color-2);
}

.input-icon {
  padding: 0 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--green);
  font-family: 'SF Mono', monospace;
  background-color: rgba(76, 175, 80, 0.1);
  height: 48px;
  display: flex;
  align-items: center;
  border-right: 1px solid var(--border-color);
}

.command-input {
  flex: 1;
  padding: 0 16px;
  height: 48px;
  border: none;
  background: transparent;
  color: var(--font-color-primary);
  font-size: 15px;
  font-family: 'SF Mono', monospace;
  outline: none;
}

.command-input::placeholder {
  color: var(--font-color-secondary);
  opacity: 0.6;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-button {
  height: 40px;
  padding: 0 16px;
  border-radius: 20px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.execute-button {
  background-color: var(--green);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.execute-button:hover:not(:disabled) {
  background-color: #66BB6A;
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
  transform: translateY(-2px);
}

.execute-button:active:not(:disabled) {
  transform: translateY(0);
}

.export-button {
  background-color: transparent;
  color: var(--green);
  border: 1px solid var(--green);
}

.export-button:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.1);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.reset-button {
  background-color: transparent;
  color: var(--font-color-secondary);
  border: 1px solid var(--border-color);
}

.reset-button:hover:not(:disabled) {
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--red);
  border-color: var(--red);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.2);
}

.button-icon {
  width: 20px;
  height: 20px;
  stroke: currentColor;
}

.execute-button .button-icon {
  stroke: white;
}

.reset-icon {
  font-size: 16px;
  font-weight: 300;
}

.button-text {
  letter-spacing: 0.3px;
}


.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
  color: var(--font-color-secondary);
}

.empty-message {
  font-size: 16px;
  margin-bottom: 20px;
  opacity: 0.8;
}

.empty-button {
  background-color: var(--green);
  color: white;
  border: none;
  border-radius: 20px;
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

.empty-button:hover {
  background-color: #66BB6A;
  box-shadow: 0 6px 16px rgba(76, 175, 80, 0.4);
  transform: translateY(-2px);
}

.empty-button:active {
  transform: translateY(0);
}
</style>