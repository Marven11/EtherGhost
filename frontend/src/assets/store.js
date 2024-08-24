import { reactive, ref, watch } from 'vue'
import { getDataOrPopupError } from './utils'

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