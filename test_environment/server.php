<?php
// set_time_limit(0);
ignore_user_abort();

if (version_compare(PHP_VERSION, '5.4.0', '>=')) @http_response_code(200);

if ($_GET["cmd"] == "server") {
    $start_time = time();
    $result = "";
    session_start();
    $_SESSION["data"] = array(
        "data" => ""
    );
    session_write_close();
    while (time() - $start_time < 3) {
        session_start();
        if ($_SESSION["data"]["data"]) {
            $result .= $_SESSION["data"]["data"];
            unset($_SESSION["data"]["data"]);
        }
        session_write_close();
        usleep(10000);
    }
    var_dump($result);
    echo session_id();
} else {
    session_start();
    $_SESSION["data"]["data"] = $_GET["data"];
    echo session_id();
    var_dump($_SESSION["data"]["data"]);
    session_write_close();
}
