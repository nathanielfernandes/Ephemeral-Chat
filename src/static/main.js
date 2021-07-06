const COLORCLASSES = ["purple", "pink", "red", "yellow", "green", "blue", "indigo"];

var colorButton = document.getElementById("colorButton");
var startChatting = document.getElementById("startChatting");
var color = 0;

var formColor = document.getElementById("color");
formColor.value = COLORCLASSES[color];


function cycleColor() {
    colorButton.classList.remove(`bg-${COLORCLASSES[color]}-400`);
    colorButton.classList.remove(`hover:bg-${COLORCLASSES[color]}-500`);
    startChatting.classList.remove(`bg-${COLORCLASSES[color]}-400`);
    startChatting.classList.remove(`hover:bg-${COLORCLASSES[color]}-500`);

    if (color == 6) {
        color = 0;
    } else {
        color += 1;
    }

    colorButton.classList.add(`bg-${COLORCLASSES[color]}-400`);
    colorButton.classList.add(`hover:bg-${COLORCLASSES[color]}-500`);
    startChatting.classList.add(`bg-${COLORCLASSES[color]}-400`);
    startChatting.classList.add(`hover:bg-${COLORCLASSES[color]}-500`);
    formColor.value = COLORCLASSES[color];
}