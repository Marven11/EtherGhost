

let elementActionListElement = null;
let elementActionListTop = 0;
let elementActionListLeft = 0;
let lastClickSession = null;
let siteUrl = `${window.location.protocol}//${window.location.host}`

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
    if (!elementActionListElement) {
        return
    }
    let clickedAction = traverseParents(event.target).filter(
        element => element.classList.contains("session-action-item")
    )
    if (clickedAction.length == 0) {
        console.log("Click Nothing!")
        return;
    }
    clickedAction = clickedAction[0]
    console.log(clickedAction.id)

}

function onClickTerminalExecute(event) {
    terminalExecuteCommand();
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
    fetchJson("/session_execute_cmd", {
        "cmd": cmd,
        "session_id": getHashParameters().session
    }).then(result => terminalAddCommand(cmd, result))
}

function terminalInit() {
    terminalPaint()
}

// action list functions

function hideActionList() {
    if (!elementActionListElement) {
        return;
    }
    elementActionListElement.style = `
        opacity: 0;
        position: absolute;
        top: ${elementActionListTop}px;
        left: ${elementActionListLeft}px;`
    setTimeout(function () {
        elementActionListElement.remove();
        elementActionListElement = null;
    }, 300);
}

function showActionList(top, left) {
    let template = document.getElementById("template-action-list");
    let style = `
        opacity: 1; 
        position: absolute;
        top: ${top}px; 
        left: ${left}px;`
    let clickedSession = traverseParents(lastClickSession).filter(it => it.classList.contains("session"))[0];
    let clickedSessionId = clickedSession.getAttribute("session-id")
    if (!elementActionListElement) {
        let clone = template.content.cloneNode(true);
        const mainElement = document.querySelector('main');
        mainElement.appendChild(clone);
        elementActionListElement = document.querySelector(".session-action-list")
    }

    elementActionListTop = top;
    elementActionListLeft = left;
    Array.from(elementActionListElement.getElementsByClassName("session-action-link")).forEach(element => {
        let itemId = element.querySelector(".session-action-item").id;
        let action = {
            "session-action-terminal": "terminal",
            "session-action-files": "files",
            "session-action-delete-session": "delete-session",
        }[itemId];
        element.href = `#session=${clickedSessionId}&action=${action}`
    })
    setTimeout(() => {
        elementActionListElement.style = style;
    }, 0)
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

async function fetchJson(path, param) {

    let url = new URL(siteUrl + path);
    const param_obj = new URLSearchParams();
    if (param) {
        for (k of Object.keys(param)) {
            param_obj.append(k, param[k]);
        }
        url.search = param_obj;
    }

    let response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
        body: param_obj.toString()
    });
    let response_json = await response.json();
    if (response_json.code != 0) {
        throw new Error(`Wrong response code ${response_json.code} for path ${path}, msg: ${response_json.msg}`);
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
    }

}

function homeMain(hashParams) {
    useTemplateHome("template-home");
    fetchJson("/list_session").then(
        homeFillSessions
    );
}

function main() {
    let hashParams = getHashParameters();
    console.log(hashParams)
    if (!hashParams.session) {
        homeMain(hashParams)
    } else {
        sessionMain(hashParams)
    }
}
main();