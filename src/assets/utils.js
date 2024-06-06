import axios from "axios"


export function hello() {
  console.log("Hello, World!")
}

export function getCurrentApiUrl() {
  return "http://127.0.0.1:8000" // TODO: rewrite me
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

export function getDataOrPopupError(resp, popupsRef) {
  if (resp.data.code != 0) {
    let title = `未知错误：${resp.data.code}`
    if (resp.data.code == -400) {
      title = "客户端错误"
    } else if (resp.data.code == -500) {
      title = "服务端错误"
    }
    popupsRef.value.addPopup("red", title, resp.data.msg)
    doAssert(false, `${title}: ${resp.data.msg}`)
    return;
  }
  return resp.data.data
}


export async function requestDataOrPopupError(uri, popupsRef, config) {
  let url = `${getCurrentApiUrl()}${uri}`
  let resp
  try {
    resp = await axios.get(url, config)
  }catch(e){
    popupsRef.value.addPopup("red", "请求错误", `无法请求${uri}，服务端是否正在运行？`)
    throw e
  }
  return getDataOrPopupError(resp, popupsRef)
}

export async function postDataOrPopupError(uri, popupsRef, config) {
  let url = `${getCurrentApiUrl()}${uri}`
  let resp
  try {
    resp = await axios.post(url, config)
  }catch(e){
    popupsRef.value.addPopup("red", "请求错误", `无法请求${uri}，服务端是否正在运行？`)
    throw e
  }
  return getDataOrPopupError(resp, popupsRef)
}

