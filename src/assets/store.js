import { reactive, ref, watch } from 'vue'
import { getDataOrPopupError } from './utils'

export const popupsRef = ref(null)

export const store = reactive({
  session: "",
  sessionName: ""
})

watch(
  () => store.session,
  async newSession => {
    let sessionInfo = await getDataOrPopupError(`/session/${newSession}/`)
    store.sessionName = sessionInfo.name
  }
)