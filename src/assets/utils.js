

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


export function mustGetData(resp_data, popupsRef) {
  if (resp_data.code != 0) {
    let title = "未知错误"
    if (resp_data.code == -400) {
      title = "客户端错误"
    } else if (resp_data.code == -500) {
      title = "服务端错误"
    }
    popupsRef.value.addPopup("red", title, resp_data.msg)
    doAssert(false, `${title}: ${resp_data.msg}`)
    return;
  }
  return resp_data.data
}

