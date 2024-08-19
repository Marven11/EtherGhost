<?php

$PREFIX = "vessel";
$folder = "/tmp/vessel";
$sleep_interval = 5000;

function random_string($length)
{
    $characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
    $randomString = '';
    for ($i = 0; $i < $length; $i++) {
        $randomString .= $characters[rand(0, strlen($characters) - 1)];
    }
    return $randomString;
}

function call_raw($fn, $args, $check_times)
{
    global $PREFIX, $folder, $sleep_interval;
    $reqid = random_string(12);
    if (!is_dir($folder)) {
        return json_encode(["code" => -100, "msg" => "vessel not started"]);
    }
    file_put_contents("$folder/{$PREFIX}_{$reqid}_req", json_encode([
        "fn" => $fn,
        "args" => $args
    ]));
    for ($i = 0; $i < $check_times; $i++) {
        if (is_file("$folder/{$PREFIX}_{$reqid}_resp")) {
            $resp = file_get_contents("$folder/{$PREFIX}_{$reqid}_resp");
            @unlink("$folder/{$PREFIX}_{$reqid}_resp");
            return $resp;
        }
        usleep($sleep_interval);
    }
    return json_encode(["code" => -100, "msg" => "vessel down"]);
}

function call($fn, $args, $timeout)
{
    global $sleep_interval;
    $hello_resp = json_decode(call_raw("hello", [], 10));
    if ($hello_resp->code != 0) {
        return json_encode($hello_resp);
    }
    return call_raw($fn, $args, intval(1000 * 1000 * $timeout / $sleep_interval));
}

echo call($_POST["fn"], json_decode($_POST["args"]), intval($_POST["timeout"]));
