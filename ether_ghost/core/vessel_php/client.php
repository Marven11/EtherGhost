<?php
session_start();
if (version_compare(PHP_VERSION, '5.4.0', '>=')) @http_response_code(200);

class VesselClient
{
    public $sleep_interval = 50000;
    public $session_key = "";
    function __construct($session_key)
    {
        $this->session_key = $session_key;
    }
    function random_string($length)
    {
        $characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
        $randomString = '';
        for ($i = 0; $i < $length; $i++) {
            $randomString .= $characters[rand(0, strlen($characters) - 1)];
        }
        return $randomString;
    }
    function call_over_file($fn, $args, $check_times)
    {
        $PREFIX = "vessel";
        $folder = "/tmp/vessel";
        $reqid = $this->random_string(12);

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
            usleep($this->sleep_interval);
        }
        return json_encode(["code" => -100, "msg" => "vessel down"]);
    }

    function call_over_session($fn, $args, $check_times)
    {
        $reqid = $this->random_string(12);
        $session_key = $this->session_key;
        if (!isset($_SESSION[$session_key])) {
            return json_encode(["code" => -100, "msg" => "vessel not found"]);
        }
        $_SESSION[$session_key]["req"][$reqid] = json_encode([
            "fn" => $fn,
            "args" => $args,
        ]);
        session_write_close();
        for ($i = 0; $i < $check_times; $i++) {
            $result = null;
            session_start();
            if (isset($_SESSION[$session_key]["resp"][$reqid])) {
                $result = $_SESSION[$session_key]["resp"][$reqid];
                unset($_SESSION[$session_key]["resp"][$reqid]);
                return $result;
            }
            session_write_close();
            usleep($this->sleep_interval);
        }
        return json_encode(["code" => -100, "msg" => "vessel down for key: " . $session_key]);
    }

    function call($call_raw, $fn, $args, $timeout)
    {
        $hello_resp = json_decode($this->$call_raw("hello", [], 10));
        if ($hello_resp->code != 0) {
            return json_encode($hello_resp);
        }
        $result = call_user_func([$this, $call_raw], $fn, $args, intval(1000 * 1000 * $timeout / $this->sleep_interval));
        return $result;
    }
}
