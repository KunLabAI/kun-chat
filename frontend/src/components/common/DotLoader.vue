<template>
  <!-- From Uiverse.io by abrahamcalsin --> 
  <div class="dot-spinner-container">
    <div class="dot-spinner">
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
      <div class="dot-spinner__dot"></div>
    </div>
  </div>
</template>

<script setup>
// 无需props，这是一个简单的加载指示器组件
</script>

<style scoped>
.dot-spinner-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
  min-height: 200px;
}

/* From Uiverse.io by abrahamcalsin */ 
.dot-spinner {
  --uib-size: 3.5rem;
  --uib-speed: .9s;
  --uib-color: var(--primary-600);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height: var(--uib-size);
  width: var(--uib-size);
}

.dot-spinner__dot {
  position: absolute;
  top: 0;
  left: 0;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height: 100%;
  width: 100%;
}

.dot-spinner__dot::before {
  content: '';
  height: 20%;
  width: 20%;
  border-radius: 50%;
  background-color: var(--uib-color);
  transform: scale(0);
  opacity: 0.5;
  animation: pulse0112 calc(var(--uib-speed) * 1.111) ease-in-out infinite;
  box-shadow: 0 0 20px rgba(126, 34, 206, 0.3);
}

.dot-spinner__dot:nth-child(1)::before {
  background-color: var(--primary-500);
}

.dot-spinner__dot:nth-child(2) {
  transform: rotate(45deg);
}

.dot-spinner__dot:nth-child(2)::before {
  animation-delay: calc(var(--uib-speed) * -0.875);
  background-color: var(--primary-600);
}

.dot-spinner__dot:nth-child(3) {
  transform: rotate(90deg);
}

.dot-spinner__dot:nth-child(3)::before {
  animation-delay: calc(var(--uib-speed) * -0.75);
  background-color: var(--primary-700);
}

.dot-spinner__dot:nth-child(4) {
  transform: rotate(135deg);
}

.dot-spinner__dot:nth-child(4)::before {
  animation-delay: calc(var(--uib-speed) * -0.625);
  background-color: var(--primary-800);
}

.dot-spinner__dot:nth-child(5) {
  transform: rotate(180deg);
}

.dot-spinner__dot:nth-child(5)::before {
  animation-delay: calc(var(--uib-speed) * -0.5);
  background-color: var(--primary-700);
}

.dot-spinner__dot:nth-child(6) {
  transform: rotate(225deg);
}

.dot-spinner__dot:nth-child(6)::before {
  animation-delay: calc(var(--uib-speed) * -0.375);
  background-color: var(--primary-600);
}

.dot-spinner__dot:nth-child(7) {
  transform: rotate(270deg);
}

.dot-spinner__dot:nth-child(7)::before {
  animation-delay: calc(var(--uib-speed) * -0.25);
  background-color: var(--primary-500);
}

.dot-spinner__dot:nth-child(8) {
  transform: rotate(315deg);
}

.dot-spinner__dot:nth-child(8)::before {
  animation-delay: calc(var(--uib-speed) * -0.125);
  background-color: var(--primary-400);
}

@keyframes pulse0112 {
  0%,
  100% {
    transform: scale(0);
    opacity: 0.5;
  }

  50% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 暗色主题适配 */
:root.dark .dot-spinner__dot:nth-child(1)::before,
.dark .dot-spinner__dot:nth-child(1)::before {
  background-color: var(--primary-300);
}

:root.dark .dot-spinner__dot:nth-child(2)::before,
.dark .dot-spinner__dot:nth-child(2)::before {
  background-color: var(--primary-400);
}

:root.dark .dot-spinner__dot:nth-child(3)::before,
.dark .dot-spinner__dot:nth-child(3)::before {
  background-color: var(--primary-500);
}

:root.dark .dot-spinner__dot:nth-child(4)::before,
.dark .dot-spinner__dot:nth-child(4)::before {
  background-color: var(--primary-600);
}

:root.dark .dot-spinner__dot:nth-child(5)::before,
.dark .dot-spinner__dot:nth-child(5)::before {
  background-color: var(--primary-500);
}

:root.dark .dot-spinner__dot:nth-child(6)::before,
.dark .dot-spinner__dot:nth-child(6)::before {
  background-color: var(--primary-400);
}

:root.dark .dot-spinner__dot:nth-child(7)::before,
.dark .dot-spinner__dot:nth-child(7)::before {
  background-color: var(--primary-300);
}

:root.dark .dot-spinner__dot:nth-child(8)::before,
.dark .dot-spinner__dot:nth-child(8)::before {
  background-color: var(--primary-200);
}
</style>
