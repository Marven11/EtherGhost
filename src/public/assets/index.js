

let elementActionListElement = null;
let elementActionListTop = 0;
let elementActionListLeft = 0;
let lastClickWebshell = null;
let siteUrl = `${window.location.protocol}//${window.location.host}`

// event functions

function onClickRoot(event) {
    let isWebshellClicked = traverseParents(event.target).map(it => it.classList.contains("webshell")).includes(true);
    if (isWebshellClicked) {
        lastClickWebshell = event.target;
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
        element => element.classList.contains("webshell-action-item")
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
    fetchJson("/webshell_execute_cmd", {
        "cmd": cmd,
        "webshell_id": getHashParameters().webshell
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
    let clickedWebshell = traverseParents(lastClickWebshell).filter(it => it.classList.contains("webshell"))[0];
    let clickedWebshellId = clickedWebshell.getAttribute("webshell-id")
    if (!elementActionListElement) {
        let clone = template.content.cloneNode(true);
        const mainElement = document.querySelector('main');
        mainElement.appendChild(clone);
        elementActionListElement = document.querySelector(".webshell-action-list")
    }

    elementActionListTop = top;
    elementActionListLeft = left;
    Array.from(elementActionListElement.getElementsByClassName("webshell-action-link")).forEach(element => {
        let itemId = element.querySelector(".webshell-action-item").id;
        let action = {
            "webshell-action-terminal": "terminal",
            "webshell-action-files": "files",
            "webshell-action-delete-webshell": "delete-webshell",
        }[itemId];
        element.href = `#webshell=${clickedWebshellId}&action=${action}`
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

function homeFillWebshells(webshells) {
    const webshellsElement = document.querySelector('.webshells');
    while (webshellsElement.firstChild) {
        webshellsElement.firstChild.remove();
    }
    let template = document.getElementById("template-home-webshell");
    for (let webshell of webshells) {
        let clone = template.content.cloneNode(true);
        clone.querySelector(".webshell-name").textContent = webshell.name
        clone.querySelector(".webshell-note").textContent = webshell.note
        clone.querySelector(".webshell-meta-type").textContent = webshell.type
        clone.querySelector(".webshell-meta-location").textContent = webshell.location
        clone.querySelector(".webshell").setAttribute("webshell-id", webshell.id)
        webshellsElement.appendChild(clone);
    }
}

async function fetchJson(path, param) {

    let url = new URL(siteUrl + path);
    if (param) {
        const params_obj = new URLSearchParams();
        for (k of Object.keys(param)) {
            params_obj.append(k, param[k]);
        }
        url.search = params_obj;
    }

    let response = await fetch(url);
    let response_json = await response.json();
    if (response_json.code != 0) {
        throw new Error(`Wrong response code ${response_json.code} for path ${path}, msg: ${response_json.msg}`);
    }
    return response_json.data;
}

// entry functions

function webshellMain(hashParams) {
    let webshell = hashParams.webshell
    let action = "terminal"
    if (!webshell) {
        throw new Error("Webshell should be provided");
    }
    if (hashParams.action) {
        action = hashParams.action;
    }
    if (action == "terminal") {
        useTemplateHome("template-terminal");
    }

}

function homeMain(hashParams) {
    useTemplateHome("template-home");
    fetchJson("/list_webshell").then(
        homeFillWebshells
    );
}

function main() {
    let hashParams = getHashParameters();
    console.log(hashParams)
    if (!hashParams.webshell) {
        homeMain(hashParams)
    } else {
        webshellMain(hashParams)
    }
}
main();