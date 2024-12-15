<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
  name: 'Navbar',
  setup() {
    interface NavLink {
      name: string;
      url: string;
    }

    const route = useRoute();
    const isActive = (path: string) => route?.path === path;

    const links = ref<NavLink[]>([
      { name: 'Home', url: '/' },
      { name: 'About', url: '/about' },
    ]);

    return {
      links,
      isActive,
    };
  },
});
</script>

<template>
  <nav class="fixed top-5 flex flex-row justify-center gap-3 -translate-x-1/2 left-1/2 py-2 px-3 border border-gray-800 rounded-full backdrop-blur bg-[rgba(255,255,255,0.7)]">
    <a
        v-for="link in links"
        :key="link.name"
        :href="link.url"
        :class="[
          'py-2 px-4 rounded-full',
          isActive(link.url) ? 'bg-gray-800 text-gray-100' : '',
        ]"
    >
      {{ link.name }}
    </a>
  </nav>
</template>

<style scoped>

</style>
