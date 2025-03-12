<template>
  <div class="under-construction">
    <img src="@/assets/icons/under-construction.svg" alt="建设中" class="construction-icon">
    <h1>功能建设中</h1>
    <p>该功能正在开发中，敬请期待...</p>
  </div>
</template>

<style scoped>
.under-construction {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  color: var(--gray-600);
}

.construction-icon {
  width: 120px;
  height: 120px;
  margin-bottom: 24px;
}

h1 {
  font-size: 24px;
  margin-bottom: 16px;
  color: var(--gray-900);
}

.dark h1 {
  color: var(--gray-100);
}

p {
  font-size: 16px;
}
</style>
