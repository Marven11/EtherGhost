let elementActionList = null;
let elementActionListTop = 0;
let elementActionListLeft = 0;
let lastClickSession = null;
let siteUrl = `${window.location.protocol}//${window.location.host}`
let currentPage = null;
let lastPopupTime = Date.now() - 10000;

// event functions

function onClickRoot(event) {
    let isSessionClicked = traverseParents(event.target).map(it => it.classList.contains("session")).includes(true);
    if (isSessionClicked) {
        lastClickSession = event.target;
        showActionList(event.clientY, event.clientX)
    } else {
        hideActionList()
    }
}

function onClickActionList(event) {

    let clickedAction = traverseParents(event.target).filter(
        element => element.classList.contains("session-action-item")
    )[0]

    let targetActions = {
        "session-action-terminal": "terminal",
        "session-action-files": "files",
        "session-action-proxy": "proxy",
        "session-action-machine-info": "machine-info",
        "session-action-edit-webshell": "edit-webshell",
    }[clickedAction.id];
    if (!elementActionList || !lastClickSession) {
        return
    }
    if (!clickedAction) {
        console.log("Click Nothing!")
        return;
    } else if (!targetActions) {
        console.log("Action not found!");
        return
    } else {
        console.log(`Click on: ${clickedAction}`)
    }
    let clickedSession = traverseParents(lastClickSession).filter(it => it.classList.contains("session"))[0];
    let clickedSessionId = clickedSession.getAttribute("session-id")
    window.location = `/#session=${clickedSessionId}&action=${targetActions}`
}

function onClickTerminalExecute(event) {
    terminalExecuteCommand();
}

function onClickNavbarButton(event) {
    let icon = traverseParents(event.target).filter(it => it.classList.contains("navbar-icon"))[0]
    if (icon == undefined) {
        throw new Error(`No button was clicked for target ${event.target}.`);
    }
    if (icon.id == "navbar-icon-home") {
        window.location = "/"
    } else if (icon.id == "navbar-icon-terminal") {
        alert("请点击对应webshell打开终端")
    }
}

function onClickHomeAddWebshellButton(event) {
    window.location = "/#action=add-webshell"
}

function onClickEditorDiscardButton(event) {
    window.close();
}

function onClickEditorTestButton(event) {
    const form = document.querySelector(".main-form");
    let sessionInfo = getEditorInput(form);
    console.log(sessionInfo);
    fetchJson("/test_webshell", "POST", params = {}, data = sessionInfo).then(success => {
        if (success) {
            showPopup("green", "测试成功", "这个webshell可以正常使用")
        } else {
            showPopup("yellow", "测试失败", "这个webshell不可以正常使用")
        }
    });
}

function onClickEditorDeleteButton(event) {
    console.log(event)
    let session_id = document.querySelector("[name='session_id']").value
    if (!session_id) {
        alert("No session id!");
    }
    fetchJson(`/session/${session_id}`, "DELETE").then(success => {
        if (success) {
            window.location = "/"
        }
    })
}

function onKeydownTerminal(event) {
    if (event.key === "Enter") {
        terminalExecuteCommand();
    }
}

function onSubmitWebshellEditor(event) {
    event.preventDefault();
    const form = event.target;
    let sessionInfo = getEditorInput(form);
    fetchJson("/update_webshell", "POST", params = {}, data = sessionInfo).then(_ => {
        showPopup("green", "保存成功", "webshell已成功保存到本地数据库中");
        setTimeout(() => {
            window.history.back();
        }, 800);
    });
}

// template functions

function useTemplateHome(template_id) {
    let mainElement = document.querySelector('main');
    while (mainElement.firstChild) {
        mainElement.firstChild.remove();
    }
    let template = document.getElementById(template_id);
    let clone = template.content.cloneNode(true);
    mainElement.appendChild(clone);
}

// webshell editor functions

function getEditorInput(form) {
    const formData = new FormData(form);
    let data = {};

    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    let sessionInfo = {
        session_type: data.session_type,
        name: data.name,
        connection: {
            url: data.url,
            password: data.password,
            method: data.method,
            http_params_obfs: data.http_obfs,
            encoder: data.encoder
        },
        note: data.note,
        location: "",
        session_id: data.session_id
    }
    if (!sessionInfo.session_id) {
        // tell server to insert (not update) the webshell
        delete sessionInfo.session_id
    }
    return sessionInfo;
}

function fillEditorInput(session_info) {
    let setOptionByIndex = (element, option) => {
        element.selectedIndex = Array.from(element.getElementsByTagName("option"))
            .map(it => it.value)
            .indexOf(option)
    }
    setOptionByIndex(document.querySelector("[name='session_type']"), session_info["session_type"])
    document.querySelector("[name='name']").value = session_info["name"]
    document.querySelector("[name='note']").value = session_info["note"]
    document.querySelector("[name='session_id']").value = session_info["session_id"]
    if (session_info["session_type"] == "ONELINE_PHP") {
        document.querySelector("[name='url']").value = session_info["connection"]["url"]
        document.querySelector("[name='password']").value = session_info["connection"]["password"]
        document.querySelector("[name='method']").value = session_info["connection"]["method"]
        document.querySelector("[name='http_params_obfs']").value = session_info["connection"]["http_params_obfs"]
        setOptionByIndex(document.querySelector("[name='method']"), session_info["connection"]["method"])
        setOptionByIndex(document.querySelector("[name='encoder']"), session_info["connection"]["encoder"])
    }
}

// terminal functions

let terminalLines = ["$ "]

function terminalPaint() {
    let terminalElement = document.querySelector(".terminal")
    terminalElement.textContent = terminalLines.join("\n")
    terminalElement.scrollTop = terminalElement.scrollHeight;
}

function terminalAddCommand(command, result) {
    terminalLines.pop();
    terminalLines.push("$ " + command);
    result.split("\n").forEach(element => {
        terminalLines.push(element);
    });
    terminalLines.push("$ ");
    terminalPaint();
}

function terminalExecuteCommand() {
    let cmd = document.querySelector(".action-input").value;
    let sessionId = getHashParameters().session;
    fetchJson(`/session/${sessionId}/execute_cmd`, "POST", params = {
        "cmd": cmd,
    }).then(result => terminalAddCommand(cmd, result))
}

function terminalInit() {
    terminalPaint()
}

// action list functions

function hideActionList() {
    if (!elementActionList) {
        return;
    }
    elementActionList.style = `
        opacity: 0;
        position: absolute;
        top: ${elementActionListTop}px;
        left: ${elementActionListLeft}px;`
    setTimeout(function () {
        elementActionList.remove();
        elementActionList = null;
    }, 300);
}

function showActionList(top, left) {
    let template = document.getElementById("template-action-list");
    let style = `
        opacity: 1; 
        position: absolute;
        top: ${top}px; 
        left: ${left}px;`
    if (!elementActionList) {
        let clone = template.content.cloneNode(true);
        const mainElement = document.querySelector('main');
        mainElement.appendChild(clone);
        elementActionList = document.querySelector(".session-action-list")
    }

    elementActionListTop = top;
    elementActionListLeft = left;
    setTimeout(() => {
        elementActionList.style = style;
    }, 0)
}

// popup functions

function showPopup(color, title, text) {
    // color can be: red, yellow, green, blue
    let template = document.getElementById("template-popup");
    let clone = template.content.cloneNode(true);
    let popUpDelate = 0;
    let duration = Date.now() - lastPopupTime;
    let elementId = `popup-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
    let icons = Array.from(clone.querySelector(".popup-icon").children);
    if (duration < 200) {
        popUpDelate = 200 - duration;
    }
    clone.querySelector(".popup-title").textContent = title;
    clone.querySelector(".popup-text").textContent = text;
    clone.querySelector(".popup").classList.add(`popup-${color}`);

    icons
        .filter(icon => !icon.classList.contains(`pop-icon-${color}`))
        .forEach(icon => icon.remove())

    setTimeout(() => {
        document.querySelector(".popups").prepend(clone);
    }, popUpDelate);
    setTimeout(() => {
        document.querySelector(".popups>:first-child").id = elementId;
    }, popUpDelate + 10);
    setTimeout(() => {
        let element = document.getElementById(elementId)
        element.style.opacity = 0;
    }, popUpDelate + 5000);
    setTimeout(() => {
        document.getElementById(elementId).remove();
    }, popUpDelate + 7000);
    lastPopupTime = Date.now() + popUpDelate;
}

// helper functions


function traverseParents(element) {
    let parents = [element,];

    while (element.parentNode.tagName != "HTML") {
        element = element.parentNode;
        parents.push(element);
    }

    return parents;
}

function getHashParameters() {
    if (window.location.hash == "") {
        console.log(window.location)
        return {};
    }
    const hash = window.location.hash.slice(1); // 获取URL中的井号后面的部分
    const params = {};
    const paramPairs = hash.split("&");
    for (const pair of paramPairs) {
        const [key, value] = pair.split("=");
        if (!key.match(/[a-z0-9_]+/)) {
            continue;
        }
        if (key.search(/prototype|constructor|__/) != -1) {
            continue;
        }
        params[key] = decodeURIComponent(value); // 解码URL中的参数值
    }

    return params;
}

function homeFillSessions(sessions) {
    const sessionsElement = document.querySelector('.sessions');
    while (sessionsElement.firstChild) {
        sessionsElement.firstChild.remove();
    }
    let template = document.getElementById("template-home-session");
    for (let session of sessions) {
        let clone = template.content.cloneNode(true);
        clone.querySelector(".session-name").textContent = session.name
        clone.querySelector(".session-note").textContent = session.note
        clone.querySelector(".session-meta-type").textContent = session.type
        clone.querySelector(".session-meta-location").textContent = session.location
        clone.querySelector(".session").setAttribute("session-id", session.id)
        sessionsElement.appendChild(clone);
    }
}

async function fetchJson(path, method, param, data) {
    let fetchOptions;
    let url = new URL(siteUrl + path);
    const param_obj = new URLSearchParams();
    if (param) {
        for (k of Object.keys(param)) {
            param_obj.append(k, param[k]);
        }
        url.search = param_obj;
    }
    if (!data) {
        data = {};
    }
    if (["GET", "HEAD"].indexOf(method.toUpperCase()) != -1) {
        fetchOptions = {
            method: method.toUpperCase(),
        }
    } else {
        fetchOptions = {
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }
    }
    let response = await fetch(url, fetchOptions);
    let response_json = await response.json();
    if (response_json.code != 0) {
        showPopup("red", "请求失败", `${response_json.code}: ${response_json.msg}`);
    }
    return response_json.data;
}

// entry functions

function sessionMain(hashParams) {
    let session = hashParams.session
    let action = "terminal"
    if (!session) {
        throw new Error("Session should be provided");
    }
    if (hashParams.action) {
        action = hashParams.action;
    }
    if (action == "terminal") {
        useTemplateHome("template-terminal");
        terminalInit();
        currentPage = "edit-webshell";
    }
}

function editWebshellMain(hashParams) {
    useTemplateHome("template-webshell-editor");
    fetchJson("/session", "GET", {
        "session_id": hashParams.session
    }).then(fillEditorInput)
    currentPage = "edit-webshell";
}

function addWebshellMain(hashParams) {
    useTemplateHome("template-webshell-editor");
    currentPage = "add-webshell";

}

function homeMain(hashParams) {
    useTemplateHome("template-home");
    fetchJson("/session", "GET").then(homeFillSessions);
    currentPage = "home";
}

function main() {
    let hashParams = getHashParameters();
    if (hashParams.action == "add-webshell") {
        addWebshellMain(hashParams);
    } else if (hashParams.action == "edit-webshell") {
        editWebshellMain(hashParams);
    } else if (hashParams.session) {
        sessionMain(hashParams);
    }
    else {
        homeMain(hashParams);
    }
}

main();


