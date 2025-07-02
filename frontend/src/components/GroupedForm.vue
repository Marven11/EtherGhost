<script setup>
import { defineProps, defineEmits } from 'vue'
import IconCheck from '@/components/icons/iconCheck.vue'
import IconCross from '@/components/icons/iconCross.vue'

const props = defineProps({
    groups: {
        type: Array,
        required: true,
        validator: (value) => {
            return value.every(group => {
                return typeof group.name === 'string' &&
                    Array.isArray(group.options) &&
                    group.options.every(option => {
                        return typeof option.id === 'string' &&
                            typeof option.name === 'string' &&
                            typeof option.type === 'string' &&
                            ['text', 'select', 'checkbox'].includes(option.type)
                    })
            })
        }
    },
    modelValue: {
        type: Object,
        required: true
    },
    buttons: {
        type: Array,
        default: () => []
    }
})

const emit = defineEmits(['update:modelValue', 'button-click'])

function updateValue(optionId, value) {
    emit('update:modelValue', 
        optionId,
        value
    )
}

function changeClickboxOption(optionId) {
    updateValue(optionId, !props.modelValue[optionId])
}

function onButtonClick(button) {
    emit('button-click', button)
}
</script>

<template>
    <div class="option-group" v-for="group in groups">
        <p class="group-title shadow-box">
            {{ group.name }}
        </p>
        <div class="options">
            <div class="option" v-for="option in group.options">
                <div class="option-name">
                    {{ option.name }}
                </div>
                <input v-if="option.type == 'text'" :type="option.type" :name="option.id" :value="modelValue[option.id]"
                    @input="updateValue(option.id, $event.target.value)" :placeholder="option.placeholder"
                    :id="'option-' + option.id">
                <select v-else-if="option.type == 'select'" :name="option.id" :id="'option-' + option.id"
                    :value="modelValue[option.id]" @change="updateValue(option.id, $event.target.value)">
                    <option disabled value="">选择一个</option>
                    <option v-for="alternative in option.alternatives" :value="alternative.value">
                        {{ alternative.name }}
                    </option>
                </select>
                <div v-else-if="option.type == 'checkbox'" class="input-checkbox" :id="'option-' + option.id"
                    :checked="modelValue[option.id]" @click="changeClickboxOption(option.id)">
                    <input type="hidden" :name="option.id" :id="'option-' + option.id" :value="modelValue[option.id]">
                    <IconCheck v-if="modelValue[option.id]" />
                    <IconCross v-else />
                </div>
            </div>
        </div>
    </div>
    <div v-if="buttons.length > 0" class="submit-buttons shadow-box">
        <div v-for="button in buttons" class="submit-button" @click="onButtonClick(button)">
            {{ button.label }}
        </div>
    </div>
</template>

<style scoped>
.option-group {
    display: flex;
    flex-direction: column;
    margin-bottom: 30px;
    width: 60%;
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
    font-size: 1.5rem;
    margin: 0;
    padding-top: 0.75rem;
    padding-bottom: 0.75rem;
    border-radius: 0.75rem;
    margin-bottom: 10px;
}

.options {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

body[data-theme="glass"] .options {
    border-radius: 20px;
    background-color: #00000015;
    backdrop-filter: blur(20px);
    padding: 10px 20px;
    margin-top: 5px;
}

.option {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: start;
    color: var(--font-color-primary);
    height: 2.2rem;
    font-size: 1rem;
    margin-top: 0.5rem;
}

.option-name {
    margin-right: 20px;
}

.option input[type="text"] {
    height: 100%;
    min-width: 200px;
    border-radius: 8px;
    flex-grow: 1;
    font-size: 1rem;
    text-indent: 10px;
}

.option select {
    height: 100%;
    background-color: #00000015;
    outline: none;
    border: none;
    border-radius: 8px;
    color: var(--font-color-primary);
    min-width: 100px;
    font-size: 1rem;
    padding-left: 10px;
}

input {
    background-color: #00000015;
    border: none;
    outline: none;
    color: var(--font-color-primary);
}

.input-checkbox {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background-color: #00000015;
    outline: 2px dashed var(--font-color-secondary);
    stroke: var(--font-color-secondary);
    display: flex;
    justify-content: center;
    align-items: center;
    transition: all 0.3s ease;
}

.input-checkbox:hover {
    background-color: #ffffff15;
}

.input-checkbox[checked=true] {
    background-color: var(--font-color-primary);
    stroke: var(--font-color-secondary);
}

.input-checkbox svg {
    width: 20px;
    height: 20px;
}

.submit-buttons {
    min-height: 6rem;
    width: 60%;
    border-radius: 20px;
    margin-left: 20%;
    margin-right: 20%;
    background-color: var(--background-color-2);
    display: flex;
    align-items: center;
    justify-content: space-around;
    user-select: none;
}

.submit-button {
    height: 60%;
    width: 20%;
    margin-left: 20px;
    margin-right: 20px;
    border-radius: 12px;
    background-color: var(--background-color-3);
    color: var(--font-color-primary);
    outline: 2px dashed var(--font-color-secondary);
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s ease;
}

.submit-button:hover {
    background-color: color-mix(in lch, rgb(255, 255, 255) 10%, var(--background-color-3));
}
</style>
