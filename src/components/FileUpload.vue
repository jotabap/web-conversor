<template>
  <div class="w-full p-6 bg-gray-700 rounded-xl shadow-inner text-center">
    <h2 class="text-lg font-semibold mb-4 text-white">Sube tu archivo</h2>

    <div
      class="border-2 border-dashed border-gray-500 rounded-lg p-8 cursor-pointer hover:border-blue-400 transition"
      @dragover.prevent
      @drop.prevent="handleDrop"
    >
      <p class="text-gray-300 mb-2">Arrastra tu archivo aquí</p>
      <button
        class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white"
        @click="$refs.fileInput.click()"
      >
        Seleccionar archivo
      </button>
      <input type="file" class="hidden" ref="fileInput" @change="handleFileChange" />
    </div>

    <div v-if="file" class="mt-4">
      <p class="text-sm text-gray-200">
        Archivo cargado: <strong>{{ file.name }}</strong>
      </p>
      <button
        class="mt-3 bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-white"
        @click="$emit('file-uploaded', file)"
      >
        Procesar archivo
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: ["option"],
  data() {
    return { file: null }
  },
  methods: {
    handleFileChange(e) {
      this.file = e.target.files[0]
    },
    handleDrop(e) {
      this.file = e.dataTransfer.files[0]
    }
  }
}
</script>
