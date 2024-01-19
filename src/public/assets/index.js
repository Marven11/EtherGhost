

let elementActionListGuessWhat = document.querySelector(".webshell-action-list");
let elementActionListTop = 0;
let elementActionListLeft = 0;
let lastClickWebshell = null;
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
    var template = document.getElementById(template_id);
    var clone = template.content.cloneNode(true);
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
    var parents = [element,];

    while (element.parentNode.tagName != "HTML") {
        element = element.parentNode;
        parents.push(element);
    }

    return parents;
}

useTemplateHome("template-terminal");
terminalInit()