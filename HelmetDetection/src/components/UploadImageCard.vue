<script lang="ts">
import { defineComponent, ref } from "vue";
import axios from "axios";

export default defineComponent({
  name: "UploadForm",
  setup() {
    const selectedFile = ref<File | null>(null);
    const submitted = ref(false);
    const predictedClass = ref("");
    const confidence = ref<number | null>(null);
    const returnedImage = ref<string | null>(null);

    const onFileChange = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        selectedFile.value = target.files[0];
      }
    };

    const uploadImage = async () => {
      if (!selectedFile.value) {
        alert("Please select a file.");
        return;
      }

      const formData = new FormData();
      formData.append("image", selectedFile.value);

      try {
        const response = await axios.post("http://127.0.0.1:5000/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });

        const data = response.data;

        predictedClass.value = data.predicted_class;
        confidence.value = data.confidence;
        returnedImage.value = `data:image/jpeg;base64,${data.image}`;

        submitted.value = true;
      } catch (error) {
        console.error(error);
        alert("Failed to upload the image.");
      }
    };

    const resetForm = () => {
      selectedFile.value = null;
      submitted.value = false;
      predictedClass.value = "";
      confidence.value = null;
      returnedImage.value = null;
    };

    return {
      selectedFile,
      submitted,
      predictedClass,
      confidence,
      returnedImage,
      onFileChange,
      uploadImage,
      resetForm,
    };
  },
});
</script>

<template>
  <div class="flex flex-col items-center space-y-4">
    <div v-if="!submitted">
      <form @submit.prevent="uploadImage" class="flex flex-col items-center space-y-4">
        <input type="file" @change="onFileChange" accept="image/*" />
        <button
            type="submit"
            class="bg-blue-500 text-white px-4 py-2 rounded"
            :disabled="!selectedFile"
        >
          Upload
        </button>
      </form>
    </div>

    <div v-else>
      <h3 class="text-lg font-semibold">Results</h3>
      <p class="text-green-600 font-bold">Class: {{ predictedClass }}</p>
      <p>Confidence: {{ (confidence * 100).toFixed(2) }}%</p>
      <img :src="returnedImage" alt="Processed" class="border rounded shadow mt-4 w-[200px] h-[200px] object-cover" />

      <button
          class="bg-gray-500 text-white px-4 py-2 rounded mt-4"
          @click="resetForm"
      >
        Upload Another Image
      </button>
    </div>
  </div>
</template>

<style scoped>

</style>