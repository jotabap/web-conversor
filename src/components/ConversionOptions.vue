<template>
  <div class="grid sm:grid-cols-2 gap-4">
    <button
      v-for="(opt, index) in options"
      :key="index"
      @click="$emit('option-selected', opt.value)"
      class="bg-blue-600 hover:bg-blue-700 transition-colors px-6 py-4 rounded-xl shadow text-left text-lg font-semibold"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      options: [
        { value: 1, label: "Excel → JSON" },
        { value: 2, label: "JSON → Excel" },
        { value: 3, label: "Excel → SQL" },
        { value: 4, label: "Ver Formatos Soportados" }
      ]
    }
  }
}
</script>
