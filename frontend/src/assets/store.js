import { reactive, ref, watch } from 'vue'
import { getDataOrPopupError } from './utils'

// 这里的popupsRef是一个指向Popups compoment的ref
// Popups全局唯一，只有App.vue里有一个
// 为了添加popup，其他模块需要取到这里的Popups ref然后调用里面的函数

export const popupsRef = ref(null)

export const store = reactive({
  session: "",
  sessionName: "",
  theme: "",
  theme_background_transition: false,
})

export const currentSettings = reactive({
  theme: "",
  filesizeUnit: 1024
})

watch(
  () => store.session,
  async newSession => {
    if (!newSession) {
      store.sessionName = ""
      return;
    }
    let sessionInfo = await getDataOrPopupError(`/session/${newSession}/`)
    store.sessionName = sessionInfo.name
  }
)

watch(
  () => currentSettings.theme,
  (newValue, oldValue) => {
    store.theme = newValue
    document.querySelector("body").dataset["theme"] = store.theme
  }
)