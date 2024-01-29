<?php
error_reporting(0);
$folderPath = "/var/www/html";
$files = scandir($folderPath);
$result = array();
foreach ($files as $file) {
    $filePath = $folderPath . $file;
    array_push($result, array(
        "name" => basename($file),
        "type" => filetype($filePath),
        "permission" => decoct(fileperms($filePath))
    ));
}
echo json_encode($result);