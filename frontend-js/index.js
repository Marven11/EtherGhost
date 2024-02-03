import { EditorView, basicSetup } from "codemirror"
import { javascript } from "@codemirror/lang-javascript"
import { php } from "@codemirror/lang-php"
import { oneDark } from '@codemirror/theme-one-dark';
import { StreamLanguage } from "@codemirror/language"
import { shell as codeMirrorModeShell } from "@codemirror/legacy-modes/mode/shell"
import { python as codeMirrorModePython } from "@codemirror/legacy-modes/mode/python"

const siteUrl = `${window.location.protocol}//${window.location.host}`
const doubleClickInterval = 200; // ms
let fileEntryClicked = null;
let fileEntryClickTime = Date.now() - 10000;
let elementClicked = null;
let currentPage = null;
let currentSession = null;
let fileEditor = null;
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
        clickClass: ["files-pwd-item-actionbutton",],
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
    element: null,
    hide: function () {

        if (!this.element) {
            return;
        }
        // We need to make this action list invisible to others
        // so that before we delete it, others will create a new one when
        // they need to show somethings.
        let element = this.element;
        this.element = null;

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
        if (!this.element) {
            let clone = template.content.cloneNode(true);
            const mainElement = document.querySelector('main');
            mainElement.appendChild(clone);
            let elementActionLists = document.querySelectorAll(".menu-action-list")
            this.element = elementActionLists[elementActionLists.length - 1]
        }
        while (this.element.firstChild) {
            this.element.firstChild.remove();
        }
        if (!this.fillButtons[currentPage]) {
            throw new Error(`Page ${currentPage} doesn't support action list`)
        }
        this.fillButtons[currentPage](this.element);

        this.top = top;
        this.left = left;
        let element = this.element
        setTimeout(() => {
            element.style = style;
        }, 0)
    },
    fillButtons: {
        home: function (element) {
            let config = actionListGetConfig();
            for (let button of config.buttons) {
                let template = document.getElementById(`template-action-list-item-${button}`);
                let clone = template.content.cloneNode(true);
                element.appendChild(clone);
            }
        },
        files: function (element) {
            let config = actionListGetConfig();
            let fileType = elementClicked.parentElement.dataset.fileType;
            if (!config.buttons[fileType]) {
                showPopup("yellow", "不支持的文件类型", "现在仍不支持操作当前的文件类型");
                return;
            }
            for (let button of config.buttons[fileType]) {
                let template = document.getElementById(`template-action-list-item-${button}`);
                let clone = template.content.cloneNode(true);
                element.appendChild(clone);
            }
        }
    },
    clicked_home: function (clickedAction) {
        let targetActions = {
            "menu-action-terminal": "terminal",
            "menu-action-files": "files",
            "menu-action-proxy": "proxy",
            "menu-action-machine-info": "machine-info",
            "menu-action-edit-webshell": "edit-webshell",
        }[clickedAction.id];
        if (!this.element || !elementClicked) {
            return
        }
        let clickedSessionId = elementClicked.getAttribute("session-id")
        window.location = `/#session=${clickedSessionId}&action=${targetActions}`
    },
    clicked_files: function (clickedAction) {
        let targetActions = {
            "menu-action-open-folder": "open-folder",
            "menu-action-open-file": "open-file",
        }[clickedAction.id];
        if (!this.element || !elementClicked) {
            return
        }
        let folderEntryElement = elementClicked.parentElement;
        let fileType = folderEntryElement.dataset.fileType;
        let isDirlike = (fileType == "dir" || fileType == "link-dir");
        let isFilelike = (fileType == "file" || fileType == "link-file");
        let pwd = document.querySelector(".action-input").value;
        let entryName = folderEntryElement.querySelector(".files-pwd-item-name").textContent
            if (targetActions == "open-folder" && isDirlike) {
            filesFetchNewDir(pwd, entryName)
            showPopup("blue", "Tips!", "你可以双击打开文件夹！")
        } else if (targetActions == "open-file" && isFilelike) {
            filesOpenFile(pwd, entryName)
            showPopup("blue", "Tips!", "你可以双击打开文件！")
        } else {
            throw new Error(`Unknown action ${clickedAction.id}(${targetActions}) for ${fileType}`)
        }
    },
}


// event functions

let eventFuncs = {
    triggerActionList: function (event) {
        if (!actionListConfig[currentPage]) {
            return;
        }
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
            return; // 点击边缘
        }
        actionList[`clicked_${currentPage}`](clickedAction);

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
        fetchJson("/test_webshell", "POST", {}, sessionInfo).then(success => {
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
    webshellEditorChangeSessionType: function (event) {
        changeEditorSessionType(event.target.value)
    },
    webshellEditorSubmit: function (event) {
        event.preventDefault();
        const form = event.target;
        let sessionInfo = getEditorInput(form);
        fetchJson("/update_webshell", "POST", {}, sessionInfo).then(_ => {
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
    filesClickEntry: function (event) {
        if (Date.now() - fileEntryClickTime > doubleClickInterval) {
            fileEntryClickTime = Date.now()
            fileEntryClicked = event.target
            return
        }
        let element = traverseParents(fileEntryClicked)
            .filter(it => it.classList.contains("files-pwd-item"))[0];
        let fileType = element.dataset.fileType;
        let pwd = document.querySelector(".action-input").value;
        let entryName = element.querySelector(".files-pwd-item-name").textContent

        if (fileType == "dir" || fileType == "link-dir") {
            filesFetchNewDir(pwd, entryName)
        } else if (fileType == "file" || fileType == "link-file") {
            filesOpenFile(pwd, entryName)
        }
        setTimeout(() => actionList.hide(), 0)
        
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

// files functions
function filesAddPwdItem(entry) {
    let pwdListElement = document.querySelector('.files-pwd-list');
    let template = document.getElementById("template-files-pwd-item");
    let clone = template.content.cloneNode(true);
    let icons = Array.from(clone.querySelectorAll(".files-pwd-item-icon"));
    icons.forEach(element => {
        if (!element.classList.contains(`icon-${entry.entry_type}`)) {
            element.remove();
        }
    })
    clone.querySelector(".files-pwd-item").dataset.fileType = entry.entry_type
    clone.querySelector(".files-pwd-item-name").textContent = entry.name
    clone.querySelector(".files-pwd-item-permission").textContent = parseFilePermission(entry.permission)
    clone.querySelector(".files-pwd-item-filesize").textContent = parseFilesizeHumanReadable(entry.filesize)
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
        filesAddPwdItem(entry);
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
    let fileContentDocument = document.querySelector(".files-content")
    let myTheme = EditorView.theme({
        ".cm-content": {
            fontFamily: "'Courier New', Courier, monospace",
            fontSize: "22px",
            backgroundColor: "var(--background-color-2)"
        },
        ".cm-gutters": {
            fontSize: "16px",
        }
    })
    let extensions = [oneDark, myTheme, basicSetup];
    if (fileEditor) {
        fileEditor.destroy();
    }
    while (fileContentDocument.firstChild) {
        fileContentDocument.firstChild.remove();
    }
    document.querySelector("#files-property-encoding").value = data.encoding
    document.querySelector("#files-title-filename").value = fileName
    if (/\.js$/.test(fileName)) {
        extensions.push(javascript())
    } else if (/\.(php|php5|php7|phar)$/.test(fileName)) {
        extensions.push(php())
    } else if (/\.(sh|zsh|bashrc|zshrc)$/.test(fileName)) {
        extensions.push(StreamLanguage.define(codeMirrorModeShell))
    } else if (/\.py$/.test(fileName)) {
        extensions.push(StreamLanguage.define(codeMirrorModePython))
    }

    fileEditor = new EditorView({
        extensions: extensions,
        parent: fileContentDocument,
        doc: data.text
    })
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
    fetchJson(`/session/${currentSession}/execute_cmd`, "GET", {
        "cmd": cmd,
    }).then(result => terminalAddCommand(cmd, result))
}

function terminalInit() {
    terminalPaint()
}


// webshell editor functions

function getEditorInput(form) {
    let data = {};
    for (let element of Array.from(form.getElementsByTagName("input"))) {
        if (traverseParents(element).filter(it => it.style.display == "none").length) {
            continue
        }
        if(element.type == "checkbox") {
            data[element.name] = element.checked
        }else{
            data[element.name] = element.value
        }
    }
    for (let element of Array.from(form.getElementsByTagName("select"))) {
        if (traverseParents(element).filter(it => it.style.display == "none").length) {
            continue
        }
        data[element.name] = element.value
    }
    let sessionInfo
    if (data.session_type == "ONELINE_PHP") {
        sessionInfo = {
            session_type: data.session_type,
            name: data.name,
            connection: {
                url: data.url,
                password: data.password,
                method: data.method,
                http_params_obfs: data.http_params_obfs,
                encoder: data.encoder,
                sessionize_payload: data.sessionize_payload
            },
            note: data.note,
            location: "",
            session_id: data.session_id
        }
    } else if (data.session_type == "BEHINDER_PHP_AES") {
        sessionInfo = {
            session_type: data.session_type,
            name: data.name,
            connection: {
                url: data.url,
                password: data.password,
                encoder: data.encoder,
                sessionize_payload: data.sessionize_payload
            },
            note: data.note,
            location: "",
            session_id: data.session_id
        }
    } else if (data.session_type == "BEHINDER_PHP_XOR") {
        sessionInfo = {
            session_type: data.session_type,
            name: data.name,
            connection: {
                url: data.url,
                password: data.password,
                encoder: data.encoder,
                sessionize_payload: data.sessionize_payload
            },
            note: data.note,
            location: "",
            session_id: data.session_id
        }
    } else {
        throw new Error(`There's a unsupported type ${data.session_type}`)
    }
    if (!sessionInfo.session_id) {
        // tell server to insert (not update) the webshell
        delete sessionInfo.session_id
    }
    return sessionInfo;
}

function changeEditorSessionType(sessionType) {
    document.querySelectorAll(".main-form-conn-options")
        .forEach(element => {
            if (element.dataset.sessionType != sessionType) {
                element.style.display = "none";
            } else {
                element.style.display = "";

            }
        })
    document.querySelectorAll(".main-form-extra-options")
        .forEach(element => {
            if (element.dataset.sessionType != sessionType) {
                element.style.display = "none";
            } else {
                element.style.display = "";
            }
        })
}

function fillEditorInput(sessionInfo) {
    let setOptionByIndex = (element, option) => {
        element.selectedIndex = Array.from(element.getElementsByTagName("option"))
            .map(it => it.value)
            .indexOf(option)
    }
    setOptionByIndex(document.querySelector("[name='session_type']"), sessionInfo["session_type"])
    document.querySelector("[name='session_type']").disabled = true;
    document.querySelector("[name='name']").value = sessionInfo["name"]
    document.querySelector("[name='note']").value = sessionInfo["note"]
    document.querySelector("[name='session_id']").value = sessionInfo["session_id"]
    Array.from(document.querySelectorAll(".main-form-conn-options"))
        .filter(element => element.dataset.sessionType != sessionInfo["session_type"])
        .forEach(element => element.remove())
    Array.from(document.querySelectorAll(".main-form-extra-options"))
        .filter(element => element.dataset.sessionType != sessionInfo["session_type"])
        .forEach(element => element.remove())
    if (sessionInfo["session_type"] == "ONELINE_PHP") {
        document.querySelector("[name='url']").value = sessionInfo["connection"]["url"]
        document.querySelector("[name='password']").value = sessionInfo["connection"]["password"]
        document.querySelector("[name='method']").value = sessionInfo["connection"]["method"]
        document.querySelector("[name='http_params_obfs']").checked = sessionInfo["connection"]["http_params_obfs"]
        setOptionByIndex(document.querySelector("[name='method']"), sessionInfo["connection"]["method"])
        setOptionByIndex(document.querySelector("[name='encoder']"), sessionInfo["connection"]["encoder"])
        setOptionByIndex(document.querySelector("[name='sessionize_payload']"), sessionInfo["connection"]["sessionize_payload"])
    } else if (sessionInfo["session_type"] == "BEHINDER_PHP_AES") {
        document.querySelector("[name='url']").value = sessionInfo["connection"]["url"]
        document.querySelector("[name='password']").value = sessionInfo["connection"]["password"]
        setOptionByIndex(document.querySelector("[name='encoder']"), sessionInfo["connection"]["encoder"])
        setOptionByIndex(document.querySelector("[name='sessionize_payload']"), sessionInfo["connection"]["sessionize_payload"])
    } else if (sessionInfo["session_type"] == "BEHINDER_PHP_XOR") {
        document.querySelector("[name='url']").value = sessionInfo["connection"]["url"]
        document.querySelector("[name='password']").value = sessionInfo["connection"]["password"]
        setOptionByIndex(document.querySelector("[name='encoder']"), sessionInfo["connection"]["encoder"])
        setOptionByIndex(document.querySelector("[name='sessionize_payload']"), sessionInfo["connection"]["sessionize_payload"])
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

function parseFilesizeHumanReadable(filesize) {
    let units = ["B", "KiB", "MiB", "GiB", "TiB"];
    if (filesize < 0) {
        return "?B";
    }
    for (let unit of units) {
        if (filesize <= 1024 || unit == units[units.length - 1]) {
            filesize = Math.round(filesize * 100) / 100;
            return `${filesize}${unit}`;
        }
        filesize = filesize / 1024;
    }
    throw new Error("This line should not be run");
}

function parseFilePermission(filePermission) {
    return Array.from(filePermission).map(dig => {
        let n = Number(dig)
        let result = ["-", "-", "-"];
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
        for (let k of Object.keys(param)) {
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
    } catch (error) {
        if (error instanceof TypeError) {
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
    changeEditorSessionType("ONELINE_PHP")
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
window.eventFuncs = eventFuncs;