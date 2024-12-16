<script setup lang="ts">

import UploadImageCard from "@/components/UploadImageCard.vue";
import {type Ref, ref} from "vue";

const cardSection = ref<HTMLElement|null>(null);

function scrollTo(view: Ref<HTMLElement|null>){
  view?.scrollIntoView({ behavior: 'smooth' });
}

</script>

<template>
  <section class="flex flex-col items-center justify-center min-h-screen">

    <div class="flex flex-row items-center gap-10 h-[80vh] self-center w-full md:px-80 mb-10">
      <img class="w-2/6" src="/banner-home.png" alt="Banner Home" />

      <div class="flex flex-col gap-5">
        <h1 class="font-bold text-4xl text-gray-800">Try Out Our Helmet Detector</h1>
        <p class="text-sm text-gray-500">
          Ensure safety compliance by identifying helmets in images. Whether you're managing a construction site or enforcing road safety, our system delivers accurate results quickly and reliably.
        </p>

        <button class="w-fit bg-gray-800 py-2 px-4 rounded-full text-gray-200 flex flex-row items-center hover:scale-105 transition-all hover:drop-shadow-xl" @click="scrollTo(cardSection)">
          Try Now
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="currentColor" class="bi bi-arrow-down-short animate-bounce flex self-center" viewBox="0 0 16 16">
            <path fill-rule="evenodd" d="M8 4a.5.5 0 0 1 .5.5v5.793l2.146-2.147a.5.5 0 0 1 .708.708l-3 3a.5.5 0 0 1-.708 0l-3-3a.5.5 0 1 1 .708-.708L7.5 10.293V4.5A.5.5 0 0 1 8 4"/>
          </svg>
        </button>
      </div>
    </div>
    <div class="flex flex-col items-center space-y-4 border border-gray-800 w-2/3 p-10 rounded-3xl" ref="cardSection">
      <UploadImageCard/>
    </div>
    <div class="md:px-80 mt-20 mb-10">
      Created by Karen, Verren, Carissa, Marvella, Hans @ 2024.
    </div>
  </section>


</template>

<style scoped>

</style>