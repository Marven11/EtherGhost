<script setup>
import { ref, shallowRef, watch } from "vue";
import { Codemirror } from 'vue-codemirror'
import { php } from '@codemirror/lang-php'
import { oneDark } from '@codemirror/theme-one-dark'
import { EditorView } from "@codemirror/view"
import { addPopup, postDataOrPopupError } from "@/assets/utils";

const props = defineProps({
  session: String,
})

// ##############
// --- Editor ---
// ##############

const phpPlain = ref(true)
const codeMirrorView = shallowRef()
const codeMirrorContent = ref("")
const codeMirrorTheme = EditorView.theme({
  "&": {
    "background-color": "var(--background-color-2)",
    "font-size": "24px",
  },
}, { dark: true })

const codeMirrorExtensions = shallowRef([])

function updateCodeMirrorExtension() {
  codeMirrorExtensions.value = [codeMirrorTheme, oneDark, codeMirrorTheme, php({ plain: phpPlain.value })]
}

function codeMirrorReady(payload) {
  codeMirrorView.value = payload.view
  updateCodeMirrorExtension()
}

watch(phpPlain, () => {
  updateCodeMirrorExtension()
})

watch(codeMirrorContent, (newValue, _) => {
  const isPlain = s => s.indexOf("<?") == -1 && s.indexOf("<html>") == -1
  if (isPlain(newValue) != phpPlain.value) {
    phpPlain.value = isPlain(newValue)
  }
})


// ###############
// --- Execute ---
// ###############

const terminalOutput = ref("")

async function onExecute() {
  if(phpPlain.value) {
    await onPhpEval();
  }else{
    await onPhpInclude();
  }
}

async function onPhpEval() {
  if (!phpPlain.value) {
    addPopup("yellow", "代码可能无法执行", "代码中含有<?, 可能导致代码无法被正常解析，请使用include功能执行")
  }
  const url = `/session/${props.session}/php_eval`
  const code = codeMirrorContent.value;
  const data = await postDataOrPopupError(url, {
    code: code
  })
  terminalOutput.value = data
}

async function onPhpInclude() {
  if (phpPlain.value) {
    addPopup("yellow", "代码可能无法执行", "代码中不含有<?, 可能导致代码无法被正常解析，请使用eval功能执行")
  }
  const url = `/session/${props.session}/php_eval`
  const rawCode = codeMirrorContent.value;
  const code = `
$temp_file = tempnam(sys_get_temp_dir(), "");
$content = ${JSON.stringify(rawCode)};
file_put_contents($temp_file, $content);
include $temp_file;
@unlink($temp_file);
  `
  const data = await postDataOrPopupError(url, {
    code: code
  })
  terminalOutput.value = data
}

</script>

<template>
  <div class="panels">
    <div class="left-panel">
      <div class="php-code">
        <codemirror v-model="codeMirrorContent" placeholder="var_dump('exploit!');" :autofocus="true"
          :indent-with-tab="true" :tab-size="4" :extensions="codeMirrorExtensions" @ready="codeMirrorReady" />
      </div>
      <div class="actions">
        <button @click="onExecute">自动选择模式执行</button>
        <button @click="onPhpEval">使用eval执行</button>
        <button @click="onPhpInclude">使用include执行</button>
      </div>
    </div>
    <div class="right-panel">
      <div class="php-output">
        <textarea name="php-output" id="php-output" readonly :value="terminalOutput"></textarea>
      </div>
      <!-- <transition>
        <InputBox v-if="showInputBox" title="测试标题" note="测试测试，这是一个测试" :requireInput="true"
          @result="(_) => showInputBox = false" />
      </transition> -->
    </div>
  </div>



</template>

<style scoped>
.panels {
  display: flex;
  width: 100%;
  height: 100%;
  justify-content: space-between;
}

.left-panel {
  width: 48%;
  height: 95%;
  display: flex;
  flex-direction: column;
}

.actions {
  display: flex;
  justify-content: left;
  width: 100%;
  height: 60px;
  margin-top: 20px;
  background-color: var(--background-color-2);
  border-radius: 20px;
  align-items: center;
  padding-left: 20px;
  padding-right: 20px;
}

.actions button {
  height: 40px;
  border: none;
  outline: none;
  border-radius: 12px;
  justify-content: center;
  margin-right: 10px;
  font-size: 16px;
  align-items: center;
  background-color: var(--background-color-3);
  color: var(--font-color-white);
  padding-left: 10px;
  padding-right: 10px;
}

.actions button:hover {
  background-color: #ffffff15;

}

.php-code {
  flex-grow: 1;
  border-radius: 20px;
  padding-top: 20px;
  padding-bottom: 20px;
  background-color: var(--background-color-2);
  overflow: auto;
}

.right-panel {
  width: 50%;
  height: 95%;
}

.php-output {
  height: 100%;
}

.php-output textarea {
  width: 100%;
  height: 100%;
  background-color: var(--background-color-2);
  color: var(--font-color-white);
  border-radius: 20px;
  font-size: 24px;
  padding: 20px;
  outline: none;
  border: none;
  resize: none;
}

svg {
  width: 35px;
  stroke: var(--font-color-white);
}
</style>
