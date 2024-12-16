<script setup lang="ts">

</script>

<template>
  <section class="flex flex-col items-center justify-center min-h-screen">
    <img src="/banner-aboutus.png" alt="About Us" class="mt-32 mb-12"/>
    <div class="w-full md:px-80 mb-10">
      <h1 class="font-bold text-2xl mb-3">Our Background</h1>
      <p class="text-sm leading-6">
        Motorcycles dominate vehicle ownership in Indonesia, making up 83.6% of the 164.1 million vehicles as of August 2024. Unfortunately, motorcycles also pose a high risk, with 73% of 103,672 accidents in 2018 involving motorcycles and a fatality rate of 25.38 passengers per 160 million kilometers. Helmets play a crucial role in reducing head injuries and fatalities, with studies showing that riders without helmets face significantly higher risks of severe injuries and death. Despite laws mandating helmet use, such as Indonesia’s UU No. 22/2009, compliance remains an issue, as evidenced by over 54,000 violations for non-SNI helmets during the 2024 Operasi Zebra.
        <br> <br>
        To promote helmet compliance and improve road safety, we have developed a website integrated with an AI-powered model to detect helmet usage. Users can upload an image to the platform, and our system will automatically analyze it to determine if a helmet is present. By leveraging computer vision technology, our solution offers an efficient and accurate way to identify non-compliance, helping raise awareness and supporting enforcement efforts. This tool aims to encourage responsible riding behavior while contributing to a safer environment for motorcycle users.
      </p>
    </div>

    <div class="w-full md:px-80 mb-10">
      <h1 class="font-bold text-2xl mb-3">How does it work?</h1>
      <p class="text-sm leading-6">
        The object detection process begins by loading a dataset containing images and bounding box coordinates. The images are pre-processed using methods such as grayscale conversion, Gaussian blur, and histogram equalization to enhance quality. Key features in the images are then detected using ORB and Akaze methods, producing keypoints that are clustered using the DBSCAN algorithm. Based on these clusters, initial bounding boxes are generated, and the average bounding box size is calculated. This size is used as a reference for the Sliding Window technique, where windows systematically move across the image to create smaller image sections for further analysis.
        <br><br>
        The sliding window outputs are passed through a Random Forest Classifier Model, which predicts whether an object is present in each section. The predicted bounding boxes are then evaluated using the Intersection over Union (IoU) metric to identify the most accurate bounding box compared to the ground truth. The final output is an image displaying the best bounding box with its prediction. This systematic process ensures accurate and efficient object detection, providing clear identification of objects in the uploaded images.
      </p>
    </div>

    <div class="md:px-80 mt-20 mb-10">
      Created by Karen, Verren, Carissa, Marvella, Hans @ 2024.
    </div>
  </section>
</template>

<style scoped>

</style>