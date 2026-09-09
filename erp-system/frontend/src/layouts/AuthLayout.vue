<script setup>
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Left side - branding -->
    <div class="hidden lg:flex lg:w-1/2 bg-primary-600 p-12 flex-col justify-between relative overflow-hidden">
      <div>
        <div class="flex items-center gap-2 mb-12">
          <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
            <span class="text-white font-bold text-xl">ERP</span>
          </div>
          <span class="text-white text-2xl font-semibold">ERP System</span>
        </div>
      </div>
      
      <div class="text-white max-w-md">
        <h1 class="text-4xl lg:text-5xl font-bold mb-6 leading-tight">
          Professional Services Management
        </h1>
        <p class="text-lg text-primary-100 mb-8">
          Streamline your projects, track time, manage clients, and grow your business with our comprehensive ERP solution.
        </p>
        <div class="grid grid-cols-3 gap-4">
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <p class="text-2xl font-bold">50+</p>
            <p class="text-primary-200 text-sm">Projects Managed</p>
          </div>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <p class="text-2xl font-bold">500+</p>
            <p class="text-primary-200 text-sm">Active Users</p>
          </div>
          <div class="bg-white/10 backdrop-blur-sm rounded-xl p-4">
            <p class="text-2xl font-bold">99.9%</p>
            <p class="text-primary-200 text-sm">Uptime</p>
          </div>
        </div>
      </div>
      
      <div class="text-primary-200 text-sm">
        © 2024 ERP System. All rights reserved.
      </div>
      
      <!-- Decorative elements -->
      <div class="absolute top-20 right-10 w-72 h-72 bg-primary-400/20 rounded-full blur-3xl"></div>
      <div class="absolute bottom-20 left-10 w-96 h-96 bg-primary-300/20 rounded-full blur-3xl"></div>
    </div>

    <!-- Right side - form -->
    <div class="w-full lg:w-1/2 flex items-center justify-center p-8 bg-secondary-50">
      <div class="w-full max-w-md">
        <div class="lg:hidden mb-8 text-center">
          <div class="w-16 h-16 bg-primary-600 rounded-xl flex items-center justify-center mx-auto mb-4">
            <span class="text-white font-bold text-2xl">ERP</span>
          </div>
          <h1 class="text-2xl font-bold text-secondary-900">ERP System</h1>
        </div>
        
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Auth layout styles */
</style>