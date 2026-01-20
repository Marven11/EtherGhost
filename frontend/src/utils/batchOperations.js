import { addPopup, parseDataOrPopupError, getCurrentApiUrl } from "@/assets/utils";
import axios from "axios";

/**
 * 初始化批量操作状态
 * @param {Array} sessionIds - 会话ID数组
 * @param {Object} batchOperationStatus - 批量操作状态对象
 */
export function initBatchOperationStatus(sessionIds, batchOperationStatus) {
  for (const sessionId of sessionIds) {
    batchOperationStatus[sessionId] = 'pending'
  }
}

/**
 * 清理批量操作状态
 * @param {Object} batchOperationStatus - 批量操作状态对象
 * @param {Object} isBatchOperating - 是否正在批量操作的ref
 * @param {Function} exitMultiSelectMode - 退出多选模式函数
 * @param {Set} selectedSessionIds - 选中的会话ID集合
 */
export function cleanupBatchOperation(batchOperationStatus, isBatchOperating, exitMultiSelectMode, selectedSessionIds) {
  Object.keys(batchOperationStatus).forEach(key => {
    delete batchOperationStatus[key]
  })
  isBatchOperating.value = false
  
  if (selectedSessionIds.size === 0) {
    exitMultiSelectMode()
  }
}

/**
 * 批量打印到console（演示功能）
 * @param {Array} sessionIds - 会话ID数组
 * @param {Array} sessions - 会话数组
 * @param {Object} batchOperationStatus - 批量操作状态对象
 * @param {Object} isBatchOperating - 是否正在批量操作的ref
 * @param {Function} exitMultiSelectMode - 退出多选模式函数
 * @param {Set} selectedSessionIds - 选中的会话ID集合
 */
export async function batchPrintToConsole(sessionIds, sessions, batchOperationStatus, isBatchOperating, exitMultiSelectMode, selectedSessionIds) {
  if (sessionIds.length === 0) {
    addPopup("red", "错误", "没有选中任何webshell")
    return
  }

  isBatchOperating.value = true
  
  initBatchOperationStatus(sessionIds, batchOperationStatus)

  for (const sessionId of sessionIds) {
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const isSuccess = Math.random() > 0.3
    batchOperationStatus[sessionId] = isSuccess ? 'success' : 'error'
    
    const session = sessions.find(s => s.id === sessionId)
    console.log(`批量操作: ${session?.name || sessionId}`)
  }

  setTimeout(() => {
    cleanupBatchOperation(batchOperationStatus, isBatchOperating, exitMultiSelectMode, selectedSessionIds)
  }, 3000)
}

/**
 * 批量测试webshell
 * @param {Array} sessionIds - 会话ID数组
 * @param {Array} sessions - 会话数组
 * @param {Object} batchOperationStatus - 批量操作状态对象
 * @param {Object} isBatchOperating - 是否正在批量操作的ref
 * @param {Function} exitMultiSelectMode - 退出多选模式函数
 * @param {Set} selectedSessionIds - 选中的会话ID集合
 */
export async function batchTestWebshell(sessionIds, sessions, batchOperationStatus, isBatchOperating, exitMultiSelectMode, selectedSessionIds) {
  if (sessionIds.length === 0) {
    addPopup("red", "错误", "没有选中任何webshell")
    return
  }

  isBatchOperating.value = true
  
  // 初始化状态
  initBatchOperationStatus(sessionIds, batchOperationStatus)

  try {
    // 并发测试所有选中的webshell
    const promises = sessionIds.map(async (sessionId) => {
      const session = sessions.find(s => s.id === sessionId)
      if (!session) {
        batchOperationStatus[sessionId] = 'error'
        return
      }
      
      try {
        // 调用后端测试API - 需要发送完整的session_info结构
        const sessionInfo = {
          session_id: session.id,
          name: session.name,
          type: session.type,
          url: session.url,
          password: session.password,
          comment: session.comment,
          extra_data: session.extra_data || {},
        }
        
        const response = await axios.post(`${getCurrentApiUrl()}/test_webshell`, sessionInfo)
        const result = parseDataOrPopupError(response)
        
        if (result && result.success) {
          batchOperationStatus[sessionId] = 'success'
        } else {
          batchOperationStatus[sessionId] = 'error'
        }
      } catch (error) {
        console.error(`测试webshell ${sessionId} 失败:`, error)
        batchOperationStatus[sessionId] = 'error'
      }
    })
    
    // 等待所有测试完成
    await Promise.allSettled(promises)
  } finally {
    // 所有操作完成，等待三秒
    setTimeout(() => {
      cleanupBatchOperation(batchOperationStatus, isBatchOperating, exitMultiSelectMode, selectedSessionIds)
    }, 3000)
  }
}
