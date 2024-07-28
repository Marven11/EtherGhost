import { reactive, ref, watch } from 'vue'
import { getDataOrPopupError } from './utils'

export const popupsRef = ref(null)

export const store = reactive({
  session: "",
  sessionName: "",
  theme: "white",
  header_background_transition: false,
})

export const currentSettings = reactive({
  theme: "white"
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
  }
)