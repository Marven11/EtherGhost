let elementActionList = null;
let elementClicked = null;
let siteUrl = `${window.location.protocol}//${window.location.host}`
let currentPage = null;
let currentSession = null;
let lastPopupTime = Date.now() - 10000;

let actionListConfig = {
    home: {
        clickClass: ["session",],
        buttons: [
            "terminal",
            "files",
            // TODO: add support
            // "proxy",
            // "machine-info",
            "edit-webshell"
        ]
    },
    files: {
        clickClass: ["files-pwd-item",],
        buttons: {
            file: [
                "open-file",
                "rename",
                "delete"
            ],
            dir: [
                "open-folder",
                "rename",
                "delete"
            ],
            "link-file": [
                "open-file",
                "rename",
                "delete"
            ],
            "link-dir": [
                "open-folder",
                "rename",
                "delete"
            ],
        }
    }
}

// action list functions

function actionListGetConfig() {
    let config = actionListConfig[currentPage];
    if (config == undefined) {
        throw new Error(`找不到页面${currentPage}点击菜单需要的按钮`);
    }
    return config;
}

let actionList = {
    top: 0,
    left: 0,
    hide: function () {

        if (!elementActionList) {
            return;
        }
        // We need to make this action list invisible to others
        // so that before we delete it, others will create a new one when
        // they need to show somethings.
        let element = elementActionList;
        elementActionList = null;

        element.style = `
            opacity: 0;
            position: absolute;
            top: ${this.top}px;
            left: ${this.left}px;`
        setTimeout(function () {
            element.remove();
        }, 300);
    },
    show: function (top, left) {
        let template = document.getElementById("template-action-list");
        let style = `
            opacity: 1; 
            position: absolute;
            top: ${top}px; 
            left: ${left}px;`;
        // create one when we don't have it, otherwise use the existed one.
        if (!elementActionList) {
            let clone = template.content.cloneNode(true);
            const mainElement = document.querySelector('main');
            mainElement.appendChild(clone);
            let elementActionLists = document.querySelectorAll(".menu-action-list")
            elementActionList = elementActionLists[elementActionLists.length - 1]
        }
        while (elementActionList.firstChild) {
            elementActionList.firstChild.remove();
        }
        if (!this.fillButtons[currentPage]) {
            throw new Error(`Page ${currentPage} doesn't support action list`)
        }
        this.fillButtons[currentPage]();

        this.top = top;
        this.left = left;
        setTimeout(() => {
            elementActionList.style = style;
        }, 0)
    },
    fillButtons: {
        home: function () {
            let config = actionListGetConfig();
            for (let button of config.buttons) {
                let template = document.getElementById(`template-action-list-item-${button}`);
                let clone = template.content.cloneNode(true);
                elementActionList.appendChild(clone);
            }
        },
        files: function () {
            let config = actionListGetConfig();
            let fileType = elementClicked.dataset.fileType;
            if (!config.buttons[fileType]) {
                showPopup("yellow", "不支持的文件类型", "现在仍不支持操作当前的文件类型");
                return;
            }
            for (let button of config.buttons[fileType]) {
                let template = document.getElementById(`template-action-list-item-${button}`);
                let clone = template.content.cloneNode(true);
                elementActionList.appendChild(clone);
            }
        }
    },
    clicked: {
        home: function (clickedAction) {
            let targetActions = {
                "menu-action-terminal": "terminal",
                "menu-action-files": "files",
                "menu-action-proxy": "proxy",
                "menu-action-machine-info": "machine-info",
                "menu-action-edit-webshell": "edit-webshell",
            }[clickedAction.id];
            if (!elementActionList || !elementClicked) {
                return
            }
            let clickedSessionId = elementClicked.getAttribute("session-id")
            window.location = `/#session=${clickedSessionId}&action=${targetActions}`
        },
        files: function (clickedAction) {
            let targetActions = {
                "menu-action-open-folder": "open-folder",
                "menu-action-open-file": "open-file",
            }[clickedAction.id];
            if (!elementActionList || !elementClicked) {
                return
            }
            let fileType = elementClicked.dataset.fileType;
            let isDirlike = (fileType == "dir" || fileType == "link-dir");
            let isFilelike = (fileType == "file" || fileType == "link-file");
            let pwd = document.querySelector(".action-input").value;
            if (targetActions == "open-folder" && isDirlike) {
                let folderName = elementClicked.querySelector(".files-pwd-item-name").textContent
                filesFetchNewDir(pwd, folderName)
            } else if (targetActions == "open-file" && isFilelike) {
                let fileName = elementClicked.querySelector(".files-pwd-item-name").textContent
                filesOpenFile(pwd, fileName)

            } else {
                throw new Error(`Unknown action ${clickedAction.id}(${targetActions}) for ${fileType}`)
            }
        }
    },
}


// event functions

let eventFuncs = {
    triggerActionList: function (event) {
        let config = actionListGetConfig();
        let element = traverseParents(event.target)
            .filter(it => {
                let classFound = config.clickClass
                    .filter(clazz => it.classList.contains(clazz))
                return classFound.length > 0;
            })[0];
        if (element != undefined) {
            elementClicked = element
            actionList.show(event.clientY, event.clientX);
        }
        else {
            elementClicked = null;
            actionList.hide();
        }
    },
    actionList: function (event) {

        let clickedAction = traverseParents(event.target).filter(
            element => element.classList.contains("menu-action-item")
        )[0];
        if (!clickedAction) {
            throw new Error("找不到点击的菜单项");
        }
        actionList.clicked[currentPage](clickedAction);

    },
    terminalExecute: function (event) {
        terminalExecuteCommand();
    },
    navbarButton: function (event) {
        let icon = traverseParents(event.target).filter(it => it.classList.contains("navbar-icon"))[0]
        if (icon == undefined) {
            throw new Error(`No button was clicked for target ${event.target}.`);
        }
        if (icon.id == "navbar-icon-home") {
            window.location = "/"
        } else if (icon.id == "navbar-icon-terminal") {
            alert("请点击对应webshell打开终端")
        }
    },
    homeAddWebshell: function (event) {
        window.location = "/#action=add-webshell"

    },
    webshellEditorDiscard: function (event) {
        window.history.back();
    },
    webshellEditorTest: function (event) {
        const form = document.querySelector(".main-form");
        let sessionInfo = getEditorInput(form);
        fetchJson("/test_webshell", "POST", params = {}, data = sessionInfo).then(success => {
            if (success) {
                showPopup("green", "测试成功", "这个webshell可以正常使用")
            } else {
                showPopup("yellow", "测试失败", "这个webshell不可以正常使用")
            }
        });
    },
    webshellEditorDelete: function (event) {
        let sessionId = document.querySelector("[name='session_id']").value
        if (!sessionId) {
            alert("No session id!");
        }
        fetchJson(`/session/${sessionId}`, "DELETE").then(success => {
            if (success) {
                window.location = "/"
            }
        })
    },
    webshellEditorSubmit: function (event) {
        event.preventDefault();
        const form = event.target;
        let sessionInfo = getEditorInput(form);
        fetchJson("/update_webshell", "POST", params = {}, data = sessionInfo).then(_ => {
            showPopup("green", "保存成功", "webshell已成功保存到本地数据库中");
            setTimeout(() => {
                window.history.back();
            }, 800);
        });
    },
    terminalKeydown: function (event) {
        if (event.key === "Enter") {
            terminalExecuteCommand();
        }
    },
    filesKeydown: function (event) {
    },
}


// template functions

function useTemplateHome(templateId) {
    let mainElement = document.querySelector('main');
    while (mainElement.firstChild) {
        mainElement.firstChild.remove();
    }
    let template = document.getElementById(templateId);
    let clone = template.content.cloneNode(true);
    mainElement.appendChild(clone);
}

// session files functions

function filesAddPwdItem(fileType, fileName, filePermission) {
    let pwdListElement = document.querySelector('.files-pwd-list');
    let template = document.getElementById("template-files-pwd-item");
    let clone = template.content.cloneNode(true);
    let icons = Array.from(clone.querySelectorAll(".files-pwd-item-icon"));
    icons.forEach(element => {
        if (!element.classList.contains(`icon-${fileType}`)) {
            element.remove();
        }
    })
    clone.querySelector(".files-pwd-item").dataset.fileType = fileType
    clone.querySelector(".files-pwd-item-name").textContent = fileName
    clone.querySelector(".files-pwd-item-permission").textContent = parseFilePermission(filePermission)
    pwdListElement.appendChild(clone);
}

async function filesFetchDir(dir) {
    let entries = await fetchJson(`/session/${currentSession}/list_dir`, "GET", {
        current_dir: dir
    })
    let pwdListElement = document.querySelector('.files-pwd-list');
    document.querySelector(".action-input").value = dir;
    while (pwdListElement.firstChild) {
        pwdListElement.firstChild.remove();
    }
    entries.forEach(entry => {
        filesAddPwdItem(entry.entry_type, entry.name, entry.permission);
    })
}

async function filesFetchNewDir(pwd, folderName) {
    let newPwd = await fetchJson("/utils/changedir", "GET", {
        "folder": pwd,
        "entry": folderName
    });
    filesFetchDir(newPwd)
}

async function filesOpenFile(pwd, fileName) {
    let data = await fetchJson(`/session/${currentSession}/get_file_contents`, "GET", {
        current_dir: pwd,
        filename: fileName
    })
    document.querySelector("#files-property-encoding").value = data.encoding
    document.querySelector("#files-content-editor").value = data.text
    document.querySelector("#files-title-filename").value = fileName
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
    fetchJson(`/session/${currentSession}/execute_cmd`, "GET", params = {
        "cmd": cmd,
    }).then(result => terminalAddCommand(cmd, result))
}

function terminalInit() {
    terminalPaint()
}


// webshell editor functions

function getEditorInput(form) {
    const formData = new FormData(form);
    let data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    data.http_params_obfs = data.http_params_obfs == "on"
    let sessionInfo = {
        session_type: data.session_type,
        name: data.name,
        connection: {
            url: data.url,
            password: data.password,
            method: data.method,
            http_params_obfs: data.http_params_obfs,
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

function fillEditorInput(sessionInfo) {
    let setOptionByIndex = (element, option) => {
        element.selectedIndex = Array.from(element.getElementsByTagName("option"))
            .map(it => it.value)
            .indexOf(option)
    }
    setOptionByIndex(document.querySelector("[name='session_type']"), sessionInfo["session_type"])
    document.querySelector("[name='name']").value = sessionInfo["name"]
    document.querySelector("[name='note']").value = sessionInfo["note"]
    document.querySelector("[name='session_id']").value = sessionInfo["session_id"]
    if (sessionInfo["session_type"] == "ONELINE_PHP") {
        document.querySelector("[name='url']").value = sessionInfo["connection"]["url"]
        document.querySelector("[name='password']").value = sessionInfo["connection"]["password"]
        document.querySelector("[name='method']").value = sessionInfo["connection"]["method"]
        document.querySelector("[name='http_params_obfs']").checked = sessionInfo["connection"]["http_params_obfs"]
        setOptionByIndex(document.querySelector("[name='method']"), sessionInfo["connection"]["method"])
        setOptionByIndex(document.querySelector("[name='encoder']"), sessionInfo["connection"]["encoder"])
    }
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

function parseFilePermission(filePermission) {
    return Array.from(filePermission).map(dig => {
        let n = Number(dig)
        result = ["-", "-", "-"];
        if (n & 4) {
            result[0] = "r";
        }
        if (n & 2) {
            result[1] = "w";
        }
        if (n & 1) {
            result[2] = "x";
        }
        return result.join("")
    }).join("")
}


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
    const paramObj = new URLSearchParams();
    if (param) {
        for (k of Object.keys(param)) {
            paramObj.append(k, param[k]);
        }
        url.search = paramObj;
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
    let response;
    try {
        response = await fetch(url, fetchOptions); 
    } catch(error) {
        if(error instanceof TypeError) {
            showPopup("red", "连接后台失败", `无法连接到后台，后台是否仍在运行？`);
        }
        throw error;
    }
    if (response.status != 200) {
        showPopup("red", "HTTP请求失败", `HTTP：${response.status}`);
        throw new Error(`HTTP请求失败：${response.status}`)
    }
    let responseData = await response.json();
    if (responseData.code != 0) {
        showPopup("red", "请求失败", `${responseData.code}: ${responseData.msg}`);
        throw new Error(`请求失败：${responseData.code}: ${responseData.msg}`)
    }
    return responseData.data;
}

// entry functions

function sessionMain(hashParams) {
    let action = "terminal"
    if (!currentSession) {
        throw new Error("Session should be provided");
    }
    if (hashParams.action) {
        action = hashParams.action;
    }
    if (action == "terminal") {
        useTemplateHome("template-terminal");
        terminalInit();
        currentPage = "terminal";
        return;
    }
    if (action == "files") {
        useTemplateHome("template-files");

        fetchJson(`/session/${currentSession}/get_pwd`, "GET").then(filesFetchDir)
        currentPage = "files";
    }
}

function editWebshellMain(hashParams) {
    useTemplateHome("template-webshell-editor");
    fetchJson("/session", "GET", {
        "session_id": currentSession
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
    currentSession = hashParams.session
    if (hashParams.action == "add-webshell") {
        addWebshellMain(hashParams);
    } else if (hashParams.action == "edit-webshell" && currentSession) {
        editWebshellMain(hashParams);
    } else if (currentSession) {
        sessionMain(hashParams);
    }
    else {
        homeMain(hashParams);
    }
}

main();


