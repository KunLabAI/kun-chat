<template>
  <div class="starry-background-container">
    <canvas ref="canvas" class="starry-canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let animationId = null
let resizeObserver = null

// 处理窗口大小变化
const handleResize = () => {
  if (canvas.value) {
    // 停止当前动画
    if (animationId) {
      cancelAnimationFrame(animationId)
      animationId = null
    }
    
    // 重新设置画布尺寸
    canvas.value.width = canvas.value.offsetWidth
    canvas.value.height = canvas.value.offsetHeight
    
    // 重新初始化星空
    initStarryBackground()
  }
}

// 星空背景动画逻辑
const initStarryBackground = () => {
  if (!canvas.value) return

  const ctx = canvas.value.getContext('2d')
  const width = canvas.value.width
  const height = canvas.value.height
  
  // 星星
  const stars = []
  for (let i = 0; i < 300; i++) {
    stars.push({
      x: Math.random() * width,
      y: Math.random() * height,
      radius: Math.random() * 1.5,
      opacity: Math.random(),
      speed: 0.05 + Math.random() * 0.1
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, width, height)
    
    // 绘制星星
    ctx.fillStyle = 'white'
    for (const star of stars) {
      // 添加星星闪烁效果
      star.opacity = Math.max(0.1, Math.min(1, star.opacity + (Math.random() - 0.5) * 0.05))
      
      ctx.globalAlpha = star.opacity
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
      ctx.fill()
      
      // 让星星缓慢移动
      star.y += star.speed
      
      // 如果星星移出画布底部，则重新放置到顶部
      if (star.y > height) {
        star.y = 0
        star.x = Math.random() * width
      }
    }
    ctx.globalAlpha = 1
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

onMounted(() => {
  initStarryBackground()
  
  window.addEventListener('resize', handleResize)
  
  // 添加一个ResizeObserver来监视容器尺寸变化
  if (canvas.value && canvas.value.parentElement) {
    resizeObserver = new ResizeObserver(() => {
      handleResize()
    })
    resizeObserver.observe(canvas.value.parentElement)
  }
})

// 组件卸载时清理资源
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
})
</script>

<style scoped>
.starry-background-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #000000;
  overflow: hidden;
}

.starry-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
