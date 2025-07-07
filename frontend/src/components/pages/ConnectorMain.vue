<script setup>
import { reactive, ref, shallowRef } from 'vue';
import IconRun from '../icons/iconRun.vue';
import IconSetting from '../icons/iconSetting.vue';
import IconPlug from '../icons/iconPlug.vue';
import IconPlus from '../icons/iconPlus.vue';
import LoadingButton from '../LoadingButton.vue';
import { getDataOrPopupError } from '@/assets/utils';
import { useRouter } from 'vue-router';

const router = useRouter()

const connectors = ref([
    // {
    //     "connector_type": "",
    //     "connector_id": "",
    //     "name": "反弹Shell",
    //     "note": "《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。",
    //     "connection": {},
    //     "autostart": false,
    // },
]);

const connectorStatus = reactive({

})

async function fetchConnectors() {
    let allConnectors = await getDataOrPopupError("/connector/all")
    console.log(allConnectors)
    connectors.value = allConnectors
    let startedConnectors = await getDataOrPopupError("/connector/started")
    for (let connector of allConnectors) {
        connectorStatus[connector.connector_id] = "off"
    }
    console.log(startedConnectors)
    for (let connectorId of startedConnectors) {
        connectorStatus[connectorId] = "on"
    }
}

setTimeout(fetchConnectors, 0)

async function connectorSwitch(connectorId) {
    console.log(connectorId)
    let lastStatus = connectorStatus[connectorId];
    connectorStatus[connectorId] = "loading"
    try {
        if (lastStatus == "off") {
            await getDataOrPopupError(`/connector/${connectorId}/start`)
            connectorStatus[connectorId] = "on"
        } else {
            await getDataOrPopupError(`/connector/${connectorId}/stop`)
            connectorStatus[connectorId] = "off"
        }
    } finally {
        await fetchConnectors()
    }
}

function editConnector(connectorId) {
    router.push(`/connector-editor/${connectorId}`)
}

</script>

<template>
    <div class="connectors">
        <div class="connector shadow-box" v-for="connector in connectors">
            <h1 class="connector-name">{{ connector.name }}</h1>
            <p class="connector-note">{{ connector.note }}</p>
            <div class="delimiter"></div>
            <div class="connector-button" @click="connectorSwitch(connector.connector_id)">
                <LoadingButton :status="connectorStatus[connector.connector_id]">
                </LoadingButton>
            </div>
            <div class="connector-button setting-button" @click="editConnector(connector.connector_id)">
                <IconSetting></IconSetting>
            </div>
        </div>
        <div class="no-connector-panel" v-if="connectors.length == 0">
            <IconPlug></IconPlug>
            <p>现在就添加一个连接器吧</p>
        </div>
    </div>
    <div class="add-connector-button shadow-box" @click="router.push('/connector-editor/')">
        <IconPlus />
    </div>
</template>

<style scoped>
.connectors {
    width: 60%;
    margin: auto;
    margin-top: 0;
    margin-bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.connector {
    width: 100%;
    min-height: 6rem;
    background-color: var(--background-color-2);
    border-radius: 20px;
    margin-bottom: 2rem;

    display: flex;
    padding: 1rem 2rem;
    align-items: center;
    flex-direction: row;
}

.connector-name {
    font-size: 2rem;
    margin-right: 2rem;
    color: var(--font-color-primary);

}

.connector-note {
    color: var(--font-color-secondary);
    width: 60%;
    overflow: hidden;
    text-overflow: ellipsis;
}

.delimiter {
    flex-grow: 1;
}

.enable-button svg {
    width: 40px;
    stroke: #000000;
}

.connector-button {
    width: 3rem;
    height: 3rem;

    border-radius: 20px;
    margin-left: 1rem;

    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.setting-button {
    background-color: var(--primary-color);
}

.connector-button svg {
    width: 70%;
    stroke: #000000;
}

.no-connector-panel {
    width: 100%;
    height: 60vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.no-connector-panel svg {
    width: 24%;
    height: 24%;
    stroke: var(--font-color-secondary);
}

.no-connector-panel p {
    font-size: 1.5rem;
    color: var(--font-color-secondary);
    margin-top: 1rem;
}

.add-connector-button {
    width: 3.5rem;
    height: 3.5rem;
    background-color: #00000030;
    border-radius: 1000px;
    position: fixed;
    top: 90vh;
    transition: background 0.3s ease;
}

.add-connector-button svg {
    width: 80%;
    stroke: var(--font-color-primary);
    margin: 10%;
}

.add-connector-button:hover {
    background-color: #00000015;
}
</style>
