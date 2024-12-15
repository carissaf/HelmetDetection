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
  <div class="flex flex-col items-center space-y-4 border border-gray-800 w-2/3 p-10 rounded-3xl">
    <div v-if="!submitted" class="flex flex-row justify-between w-full items-center">
      <img src="/upload-img-banner.png" alt="Upload Image" class="w-[55%] rounded-lg" />

      <form @submit.prevent="uploadImage" class="flex flex-col w-[40%] justify-between">
        <div class="w-full mb-16">
          <h1 class="font-bold text-2xl mb-5">Upload Your Image Here</h1>
          <input type="file" @change="onFileChange" accept="image/*" class="border border-gray-400 p-3 rounded-xl w-full" />
        </div>
        <button
            type="submit"
            class="py-2 px-4 rounded-full bg-gray-800 text-white self-end"
            :disabled="!selectedFile"
        >
          Detect Helmet
        </button>
      </form>
    </div>

    <div v-else class="flex flex-row justify-between w-full items-center">
      <img :src="returnedImage" alt="Processed" class="rounded w-[55%]" />

      <div class="w-[40%] flex flex-col justify-between">
        <div class="mb-16">
          <h1 class="font-bold text-2xl mb-5">Results</h1>
          <p class="text-green-600 font-bold">Class: {{ predictedClass }}</p>
          <p>Confidence: {{ (confidence * 100).toFixed(2) }}%</p>
        </div>
        <button
            class="py-2 px-4 rounded-full bg-gray-800 text-white self-end"
            @click="resetForm"
        >
          Try Helmet Detector Again
        </button>
      </div>

    </div>
  </div>
</template>

<style scoped>

</style>