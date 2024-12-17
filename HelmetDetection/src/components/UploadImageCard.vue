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

    const onDrop = (event: DragEvent) => {
      event.preventDefault();
      if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
        selectedFile.value = event.dataTransfer.files[0];
      }
    }

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

    const preventDefault = (event: DragEvent) => {
      event.preventDefault();
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
      onDrop,
      preventDefault
    };
  },
});
</script>

<template>
    <div v-if="!submitted" class="flex flex-row justify-between w-full items-center">
      <img src="/upload-img-banner.png" alt="Upload Image" class="w-[55%] rounded-lg" />

      <form @submit.prevent="uploadImage" class="flex flex-col w-[40%] justify-between">

          <div class="w-full mb-16" @dragover.prevent="preventDefault" @drop="onDrop">
            <label for="cover-photo" class="block font-bold text-2xl text-gray-800">Upload Your Image Here</label>
            <div class="mt-2 flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10">
              <div class="text-center">
                <svg class="mx-auto size-12 text-gray-300" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" data-slot="icon">
                  <path fill-rule="evenodd" d="M1.5 6a2.25 2.25 0 0 1 2.25-2.25h16.5A2.25 2.25 0 0 1 22.5 6v12a2.25 2.25 0 0 1-2.25 2.25H3.75A2.25 2.25 0 0 1 1.5 18V6ZM3 16.06V18c0 .414.336.75.75.75h16.5A.75.75 0 0 0 21 18v-1.94l-2.69-2.689a1.5 1.5 0 0 0-2.12 0l-.88.879.97.97a.75.75 0 1 1-1.06 1.06l-5.16-5.159a1.5 1.5 0 0 0-2.12 0L3 16.061Zm10.125-7.81a1.125 1.125 0 1 1 2.25 0 1.125 1.125 0 0 1-2.25 0Z" clip-rule="evenodd" />
                </svg>
                <div class="mt-4 flex text-sm/6 text-gray-600">
                  <label for="file-upload" class="relative cursor-pointer rounded-md bg-white font-semibold focus-within:outline-none focus-within:ring-2 focus-within:ring-gray-800 focus-within:ring-offset-2 hover:text-gray-800 hover:underline">
                    <span>Upload a file</span>
                    <input @change="onFileChange" accept="image/*" id="file-upload" name="file-upload" type="file" class="sr-only">
                  </label>
                  <p class="pl-1">or drag and drop</p>
                </div>
                <p class="text-xs/5 text-gray-600">PNG, JPG, JPEG</p>

                <p v-if="selectedFile" class="mt-4 text-gray-600 font-semibold w-full">Selected File: {{ selectedFile.name }}</p>
              </div>
            </div>
<!--              <h1 class="font-bold text-2xl mb-5">Upload Your Image Here</h1>-->
<!--          <input type="file" @change="onFileChange" accept="image/*" class="border border-gray-400 p-3 rounded-xl w-full" />-->
        </div>
        <button
            type="submit"
            class="py-2 px-4 rounded-full bg-gray-800 text-white self-end flex cursor-pointer hover:scale-105 transition-all hover:drop-shadow-xl"
            :disabled="!selectedFile"
        >
          Detect Helmet
          <svg class="flex self-center ml-2" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 48 48"><path fill="currentColor" d="M17.457 31.51a2.67 2.67 0 0 0 3.08.008c.404-.288.722-.682.916-1.139l1.236-3.769a6.16 6.16 0 0 1 3.9-3.9l3.631-1.183a2.67 2.67 0 0 0 0-5.036l-3.7-1.193a6.18 6.18 0 0 1-3.895-3.888l-1.179-3.629a2.66 2.66 0 0 0-.976-1.291a2.71 2.71 0 0 0-3.085 0a2.68 2.68 0 0 0-.987 1.32l-1.193 3.667a6.17 6.17 0 0 1-3.796 3.818l-3.627 1.178a2.67 2.67 0 0 0 .03 5.047l3.587 1.165a6.19 6.19 0 0 1 3.902 3.91l1.18 3.623c.183.521.524.973.975 1.292m15.418 9.132a1.95 1.95 0 0 0 1.124.359l.005.003a1.95 1.95 0 0 0 1.844-1.328l.569-1.75a2.38 2.38 0 0 1 1.499-1.502l1.79-.582a1.946 1.946 0 0 0 .94-2.958a1.96 1.96 0 0 0-1.005-.73l-1.757-.569a2.38 2.38 0 0 1-1.5-1.5l-.582-1.789a1.944 1.944 0 0 0-3.679.03l-.572 1.757a2.38 2.38 0 0 1-1.46 1.495l-1.79.582a1.943 1.943 0 0 0 .029 3.677l1.752.57a2.37 2.37 0 0 1 1.5 1.506l.582 1.788c.134.38.382.709.71.941"/></svg>
        </button>
      </form>
    </div>

    <div v-else class="flex flex-row justify-between w-full items-center">
      <img :src="returnedImage" alt="Processed" class="rounded w-[55%]" />

      <div class="w-[40%] flex flex-col justify-between">
        <div class="mb-16">
          <h1 class="font-bold text-2xl mb-5">Results</h1>
          <p class="text-green-600 font-bold capitalize">Class: {{ predictedClass }}</p>
          <p>Confidence: {{ (confidence * 100).toFixed(2) }}%</p>
        </div>
        <button
            class="py-2 px-4 rounded-full bg-gray-800 text-white self-end flex gap-2 hover:scale-105 transition-all hover:drop-shadow-xl"
            @click="resetForm"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" class="bi bi-arrow-clockwise flex self-center" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2z"/>
            <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466"/>
          </svg>
          Try Again
        </button>
      </div>
    </div>
</template>

<style scoped>

</style>