

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
