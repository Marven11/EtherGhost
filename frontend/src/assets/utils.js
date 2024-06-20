import axios from "axios"
import { popupsRef } from "./store"

export function hello() {
  console.log("Hello, World!")
}

export async function joinPath(folder, entry) {
  return await getDataOrPopupError("/utils/join_path", {
    params: {
      folder: folder,
      entry: entry
    }
  })
}

export function getCurrentApiUrl() {
  return window.location.origin.includes("5173") ? "http://127.0.0.1:8022" : window.location.origin
}

export function doAssert(result, msg) {
  if (result) {
    return
  }
  if (msg) {
    throw Error(msg)
  } else {
    throw Error("Assertion failed, message is not provided")
  }
}

export function addPopup(color, title, msg) {
  popupsRef.value.addPopup(color, title, msg)
}

export function parseDataOrPopupError(resp) {
  if (resp.data.code != 0) {
    let title = `未知错误：${resp.data.code}`
    if (resp.data.code == -400) {
      title = "客户端错误"
    } else if (resp.data.code == -500) {
      title = "服务端错误"
    }else if (resp.data.code == -600) {
      title = "受控端错误"
    }
    addPopup("red", title, resp.data.msg)
    doAssert(false, `${title}: ${resp.data.msg}`)
    return;
  }
  return resp.data.data
}


export async function getDataOrPopupError(uri, config) {
  let url = `${getCurrentApiUrl()}${uri}`
  let resp
  try {
    resp = await axios.get(url, config)
  } catch (e) {
    addPopup("red", "请求服务端失败", `无法请求${uri}，服务端是否正在运行？`)
    throw e
  }
  return parseDataOrPopupError(resp, popupsRef)
}

export async function postDataOrPopupError(uri, data, config = undefined) {
  let url = `${getCurrentApiUrl()}${uri}`
  let resp
  try {
    resp = await axios.post(url, data, config)
  } catch (e) {
    addPopup("red", "请求服务端失败", `无法请求${uri}，服务端是否正在运行？`)
    throw e
  }
  return parseDataOrPopupError(resp, popupsRef)
}

