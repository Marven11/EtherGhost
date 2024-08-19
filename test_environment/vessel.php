<?php
ignore_user_abort(true);
set_time_limit(0);

$PREFIX = "vessel";
$folder = "/tmp/vessel";

mkdir($folder, 0777, true);

$endpoints = array();

function hello($args)
{
    return "hi";
}
$endpoints["hello"] = "hello";

function version($args)
{
    return "0.0.1";
}
$endpoints["version"] = "version";

function checkdir($args)
{
    return is_dir($args[0]) . "";
}
$endpoints["checkdir"] = "checkdir";





while (is_dir($folder . "/")) {
    foreach (scandir($folder) as $filename) {
        if ($filename == "." || $filename == "..") {
            continue;
        }
        $filepath = "$folder/$filename";
        $matches = null;
        if (preg_match("/^vessel_([a-z0-9]+)_req/", $filename, $matches)) {
            $reqid = $matches[1];
            $content = file_get_contents($filepath);
            @unlink($filepath);
            try {
                $data = json_decode($content);
                $resp = $endpoints[$data->fn]($data->args);
                file_put_contents("$folder/{$PREFIX}_{$reqid}_resp", json_encode([
                    "reqid" => $reqid,
                    "code" => 0,
                    "resp" => $resp,
                ]));
            } catch (Exception $e) {
                echo $e;
            }
        }
    }
    usleep(5000);
    // php would cache is_dir, clear it
    clearstatcache();
}
