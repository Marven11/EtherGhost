<script setup>
import { ref } from 'vue';
import IconRun from '../icons/iconRun.vue';
import IconSetting from '../icons/iconSetting.vue';
import LoadingButton from '../LoadingButton.vue';


const connectors = [
    {
        "connector_type": "",
        "connector_id": "",
        "name": "反弹Shell",
        "note": "《原神》是由米哈游自主研发的一款全新开放世界冒险游戏。游戏发生在一个被称作「提瓦特」的幻想世界，在这里，被神选中的人将被授予「神之眼」，导引元素之力。你将扮演一位名为「旅行者」的神秘角色，在自由的旅行中邂逅性格各异、能力独特的同伴们，和他们一起击败强敌，找回失散的亲人——同时，逐步发掘「原神」的真相。",
        "connection": {},
        "autostart": false,
    },

];
const allStatus = ['off', 'loading', 'on'];
const status = ref("off"); // "on" "loading"

</script>

<template>
    <div class="connectors">
        <div class="connector shadow-box" v-for="connector in connectors">
            <h1 class="connector-name">{{ connector.name }}</h1>
            <p class="connector-note">{{ connector.note }}</p>
            <div class="delimiter"></div>
            <div class="connector-button" @click="() => {
                console.log(status)
                status = allStatus[(allStatus.indexOf(status) + 1) % 3];
            }">
                <LoadingButton :status="status">
                </LoadingButton>
            </div>
            <div class="connector-button setting-button">
                <IconSetting></IconSetting>
            </div>
        </div>
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
</style>