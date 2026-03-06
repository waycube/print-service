<template>
  <div>
    <nav class="p-4 bg-gray-800 text-white flex gap-4">
      <router-link to="/grocy">Grocy</router-link>
      <router-link to="/office">Office</router-link>
    </nav>

    <router-view />
  </div>
</template>