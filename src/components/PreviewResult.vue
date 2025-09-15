<template>
  <div class="w-full mt-6 bg-gray-900 rounded-xl shadow p-6">
    <h2 class="text-lg font-semibold text-white mb-4">Resultado</h2>

    <pre class="bg-black text-green-400 p-4 rounded-lg max-h-72 overflow-y-auto text-sm">
{{ formattedResult }}
    </pre>

    <button
      class="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white"
      @click="downloadFile"
    >
      Descargar resultado
    </button>
  </div>
</template>

<script>
export default {
  props: ["result"],
  computed: {
    formattedResult() {
      if (typeof this.result === "object") {
        return JSON.stringify(this.result, null, 2)
      }
      return this.result
    }
  },
  methods: {
    downloadFile() {
      const blob = new Blob(
        [typeof this.result === "object" ? JSON.stringify(this.result, null, 2) : this.result],
        { type: "application/octet-stream" }
      )
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = "resultado.txt"
      a.click()
      URL.revokeObjectURL(url)
    }
  }
}
</script>
