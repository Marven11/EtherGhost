

let elementActionListGuessWhat = document.querySelector(".webshell-action-list");
let elementActionListTop = 0;
let elementActionListLeft = 0;
let lastClickWebshell = null;
let siteUrl = `${window.location.protocol}//${window.location.host}`
// event functions

function onClickRoot(event) {
    let isWebshellClicked = traverseParents(event.target).map(it => it.classList.contains("webshell")).includes(true);
    if (isWebshellClicked) {
        showActionList(event.clientY, event.clientX)
        lastClickWebshell = event.target;
    } else {
        hideActionList()
    }
}

// template function

function useTemplateHome(template_id) {
    const mainElement = document.querySelector('main');
    while (mainElement.firstChild) {
        mainElement.firstChild.remove();
    }
    let template = document.getElementById(template_id);
    let clone = template.content.cloneNode(true);
    mainElement.appendChild(clone);
}

// terminal function

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
        terminalLines.push(element)
    });
    terminalLines.push("$ ")
    terminalPaint()
}

function terminalInit() {
    terminalPaint()
}

// helper function


function hideActionList() {
    elementActionListGuessWhat.style = `
        opacity: 0;
        position: absolute;
        top: ${elementActionListTop}px;
        left: ${elementActionListLeft}px;`
}

function showActionList(top, left) {
    elementActionListTop = top;
    elementActionListLeft = left;
    let style = `
        opacity: 1; 
        position: absolute;
        top: ${elementActionListTop}px; 
        left: ${elementActionListLeft}px;`
    elementActionListGuessWhat.style = style;
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
    for(let webshell of webshells) {
        let clone = template.content.cloneNode(true);
        clone.querySelector(".webshell-name").textContent = webshell.name
        clone.querySelector(".webshell-note").textContent = webshell.note
        clone.querySelector(".webshell-meta-type").textContent = webshell.type
        clone.querySelector(".webshell-meta-location").textContent = webshell.location
        webshellsElement.appendChild(clone);
    }
}

async function fetchJson(path) {
    const response = await fetch(siteUrl + path);
    const response_json = await response.json();
    if (response_json.code != 0) {
        throw new Error(`Wrong response code ${response_json.code} for path ${path}`);
    }
    return response_json.data;
}

// 各个入口函数

function webshellMain() {
    useTemplateHome("template-terminal");

}

function homeMain() {
    useTemplateHome("template-home");
    fetchJson("/list_webshell").then(
        homeFillWebshells
    );
}

function main() {
    let hashParams = getHashParameters();
    console.log(hashParams)
    if (!hashParams.webshell) {
        homeMain()
    } else {
        webshellMain()
    }
}
main();