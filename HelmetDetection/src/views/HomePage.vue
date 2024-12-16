<script setup lang="ts">

import UploadImageCard from "@/components/UploadImageCard.vue";
</script>

<template>
  <section class="flex flex-col items-center justify-center min-h-screen">
    <div class="flex flex-row items-center gap-10 h-[80vh] self-center w-full md:px-80 mb-10">

      <div class="flex flex-col gap-5">
        <h1 class="font-bold text-4xl">Try Out Our Helmet Detector</h1>
        <p class="text-sm text-gray-500">
          Ensure safety compliance by identifying helmets in images. Whether you're managing a construction site or enforcing road safety, our system delivers accurate results quickly and reliably.
        </p>
      </div>
    </div>
    
    <UploadImageCard/>

    <div class="md:px-80 mt-20 mb-10">
      Created by Karen, Verren, Carissa, Marvella, Hans @ 2024.
    </div>
  </section>
</template>

<style scoped>

</style>