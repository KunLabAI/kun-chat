<template>
  <div class="solar-system-container">
    <canvas id="solarSystem" ref="canvas"></canvas>
    <div class="overlay-text" v-if="showOverlay">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  showOverlay: {
    type: Boolean,
    default: true
  }
})

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
    
    // 重新初始化太阳系
    initSolarSystem()
  }
}

// 太阳系动画逻辑
const initSolarSystem = () => {
  if (!canvas.value) return

  const ctx = canvas.value.getContext('2d')
  const width = canvas.value.width
  const height = canvas.value.height
  
  // 缩放因子 - 根据屏幕大小调整，减小除数可以增大太阳系
  const scaleFactor = Math.min(width, height) / 800
  
  // 辅助函数：调整颜色深浅
  const shadeColor = (color, percent) => {
    let R = parseInt(color.substring(1, 3), 16);
    let G = parseInt(color.substring(3, 5), 16);
    let B = parseInt(color.substring(5, 7), 16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R < 255) ? R : 255;
    G = (G < 255) ? G : 255;
    B = (B < 255) ? B : 255;

    R = Math.max(0, R).toString(16);
    G = Math.max(0, G).toString(16);
    B = Math.max(0, B).toString(16);

    const RR = (R.length === 1) ? "0" + R : R;
    const GG = (G.length === 1) ? "0" + G : G;
    const BB = (B.length === 1) ? "0" + B : B;

    return "#" + RR + GG + BB;
  };
  
  // 星星
  const stars = []
  for (let i = 0; i < 200; i++) {
    stars.push({
      x: Math.random() * width,
      y: Math.random() * height,
      radius: Math.random() * 1.5 * scaleFactor, // 星星也放大
      opacity: Math.random()
    })
  }
  
  // 行星数据 - 所有半径和距离都乘以缩放因子
  const planets = [
    { radius: 30 * scaleFactor, distance: 0, speed: 0.002, color: '#FDB813', angle: 0, moons: [] }, // 太阳，减慢自转速度
    { radius: 3 * scaleFactor, distance: 50 * scaleFactor, speed: 0.002, color: '#97979F', angle: Math.random() * Math.PI * 2, moons: [] }, // 水星
    { radius: 5 * scaleFactor, distance: 80 * scaleFactor, speed: 0.0015, color: '#E7CDCD', angle: Math.random() * Math.PI * 2, moons: [] }, // 金星
    { radius: 6 * scaleFactor, distance: 120 * scaleFactor, speed: 0.001, color: '#6B93D6', angle: Math.random() * Math.PI * 2, moons: [
      { radius: 1.5 * scaleFactor, distance: 15 * scaleFactor, speed: 0.005, color: '#CCCCCC', angle: Math.random() * Math.PI * 2 }
    ] }, // 地球和月球
    { radius: 4 * scaleFactor, distance: 160 * scaleFactor, speed: 0.0008, color: '#C1440E', angle: Math.random() * Math.PI * 2, moons: [
      { radius: 1 * scaleFactor, distance: 12 * scaleFactor, speed: 0.004, color: '#BBBBBB', angle: Math.random() * Math.PI * 2 },
      { radius: 1 * scaleFactor, distance: 18 * scaleFactor, speed: 0.003, color: '#AAAAAA', angle: Math.random() * Math.PI * 2 }
    ] }, // 火星和卫星
    { radius: 12 * scaleFactor, distance: 220 * scaleFactor, speed: 0.0005, color: '#E3DCCB', angle: Math.random() * Math.PI * 2, moons: [
      { radius: 2 * scaleFactor, distance: 25 * scaleFactor, speed: 0.003, color: '#DDDDDD', angle: Math.random() * Math.PI * 2 },
      { radius: 1.5 * scaleFactor, distance: 35 * scaleFactor, speed: 0.002, color: '#CCCCCC', angle: Math.random() * Math.PI * 2 }
    ] }, // 木星和卫星
    { radius: 10 * scaleFactor, distance: 280 * scaleFactor, speed: 0.0004, color: '#E0BA7C', angle: Math.random() * Math.PI * 2, 
      rings: { innerRadius: 12 * scaleFactor, outerRadius: 20 * scaleFactor, color: 'rgba(224, 186, 124, 0.4)' },
      moons: [
        { radius: 1.8 * scaleFactor, distance: 22 * scaleFactor, speed: 0.0025, color: '#DDDDDD', angle: Math.random() * Math.PI * 2 },
        { radius: 1.5 * scaleFactor, distance: 30 * scaleFactor, speed: 0.002, color: '#CCCCCC', angle: Math.random() * Math.PI * 2 }
      ] 
    }, // 土星和光环及卫星
    { radius: 8 * scaleFactor, distance: 340 * scaleFactor, speed: 0.0003, color: '#82B3D1', angle: Math.random() * Math.PI * 2, moons: [
      { radius: 1.5 * scaleFactor, distance: 20 * scaleFactor, speed: 0.002, color: '#CCCCCC', angle: Math.random() * Math.PI * 2 }
    ] }, // 天王星和卫星
    { radius: 7.5 * scaleFactor, distance: 390 * scaleFactor, speed: 0.0002, color: '#3E66F9', angle: Math.random() * Math.PI * 2, moons: [
      { radius: 1.2 * scaleFactor, distance: 18 * scaleFactor, speed: 0.0015, color: '#AAAAAA', angle: Math.random() * Math.PI * 2 }
    ] } // 海王星和卫星
  ]
  
  // 小行星带
  const asteroidBelt = {
    innerRadius: 180 * scaleFactor,
    outerRadius: 200 * scaleFactor,
    count: 200,
    asteroids: []
  }
  
  // 生成小行星
  for (let i = 0; i < asteroidBelt.count; i++) {
    const angle = Math.random() * Math.PI * 2
    const distance = asteroidBelt.innerRadius + Math.random() * (asteroidBelt.outerRadius - asteroidBelt.innerRadius)
    asteroidBelt.asteroids.push({
      angle,
      distance,
      radius: 0.5 * scaleFactor + Math.random() * 1 * scaleFactor,
      speed: 0.0001 + Math.random() * 0.0003,
      color: `rgba(${150 + Math.random() * 50}, ${150 + Math.random() * 50}, ${150 + Math.random() * 50}, ${0.6 + Math.random() * 0.4})`
    })
  }
  
  const animate = () => {
    ctx.clearRect(0, 0, width, height)
    
    const centerX = width / 2
    const centerY = height / 2
    
    // 绘制星星
    ctx.fillStyle = 'white'
    for (const star of stars) {
      // 添加星星闪烁效果
      star.opacity = Math.max(0.1, Math.min(1, star.opacity + (Math.random() - 0.5) * 0.05))
      
      ctx.globalAlpha = star.opacity
      ctx.beginPath()
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2)
      ctx.fill()
    }
    ctx.globalAlpha = 1
    
    // 绘制小行星带
    for (const asteroid of asteroidBelt.asteroids) {
      // 更新小行星角度
      asteroid.angle += asteroid.speed
      
      const asteroidX = centerX + Math.cos(asteroid.angle) * asteroid.distance
      const asteroidY = centerY + Math.sin(asteroid.angle) * asteroid.distance
      
      ctx.fillStyle = asteroid.color
      ctx.beginPath()
      ctx.arc(asteroidX, asteroidY, asteroid.radius, 0, Math.PI * 2)
      ctx.fill()
    }
    
    // 绘制太阳 - 增强版本
    const sunRadius = planets[0].radius;
    // 更新太阳角度 - 但不用于纹理旋转
    planets[0].angle += planets[0].speed;
    
    // 1. 创建太阳基础渐变
    const sunGradient = ctx.createRadialGradient(
      centerX, centerY, 0,
      centerX, centerY, sunRadius
    );
    sunGradient.addColorStop(0, '#FFF7D6');  // 内部颜色更亮
    sunGradient.addColorStop(0.5, '#FDB813'); // 中间是标准的太阳黄色
    sunGradient.addColorStop(1, '#F07F13');   // 外部偏红色
    
    ctx.fillStyle = sunGradient;
    ctx.beginPath();
    ctx.arc(centerX, centerY, sunRadius, 0, Math.PI * 2);
    ctx.fill();
    
    // 2. 添加太阳表面纹理 - 固定的随机斑点
    ctx.globalAlpha = 0.3;
    ctx.fillStyle = 'rgba(255, 100, 0, 0.5)';
    
    // 使用固定的随机种子生成太阳黑子，这样它们不会每帧都变化
    // 但会缓慢旋转，给人一种太阳在自转的感觉
    const rotationOffset = planets[0].angle * 0.2; // 减慢纹理旋转速度
    
    // 添加15个固定位置的斑点模拟太阳黑子
    for (let i = 0; i < 15; i++) {
      // 使用固定角度 + 缓慢旋转
      const angle = (i / 15) * Math.PI * 2 + rotationOffset;
      // 使用固定的距离模式，但分布在不同半径上
      const distanceFactor = 0.2 + (i % 5) * 0.15;
      const distance = sunRadius * distanceFactor;
      const spotX = centerX + Math.cos(angle) * distance;
      const spotY = centerY + Math.sin(angle) * distance;
      // 大小也基于索引，使不同位置有不同大小
      const spotRadius = 1 + (i % 4) * (sunRadius / 20);
      
      ctx.beginPath();
      ctx.arc(spotX, spotY, spotRadius, 0, Math.PI * 2);
      ctx.fill();
    }
    
    // 3. 添加太阳耀斑 - 也使用固定位置但缓慢旋转
    ctx.globalAlpha = 0.6;
    ctx.fillStyle = '#FFFF00';
    
    // 4. 添加太阳光晕效果 - 光晕不旋转
    const sunGlow = ctx.createRadialGradient(
      centerX, centerY, sunRadius,
      centerX, centerY, sunRadius * 2
    );
    sunGlow.addColorStop(0, 'rgba(253, 184, 19, 0.5)');
    sunGlow.addColorStop(1, 'rgba(253, 184, 19, 0)');
    
    ctx.fillStyle = sunGlow;
    ctx.beginPath();
    ctx.arc(centerX, centerY, sunRadius * 2, 0, Math.PI * 2);
    ctx.fill();
    
    // 确保绘制行星时全局透明度为1
    ctx.globalAlpha = 1;
    
    // 绘制行星
    for (let i = 1; i < planets.length; i++) {
      const planet = planets[i]
      
      // 更新行星角度
      planet.angle += planet.speed
      
      const planetX = centerX + Math.cos(planet.angle) * planet.distance
      const planetY = centerY + Math.sin(planet.angle) * planet.distance
      
      // 绘制行星轨道
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)'
      ctx.beginPath()
      ctx.arc(centerX, centerY, planet.distance, 0, Math.PI * 2)
      ctx.stroke()
      
      // 确保绘制行星本体时完全不透明
      ctx.globalAlpha = 1;
      
      // 绘制行星 - 添加简单纹理
      // 1. 创建行星基础渐变
      const planetGradient = ctx.createRadialGradient(
        planetX, planetY, 0,
        planetX, planetY, planet.radius
      );
      
      // 根据不同行星设置不同的颜色渐变
      switch(i) {
        case 1: // 水星 - 灰色岩石纹理
          planetGradient.addColorStop(0, '#B7B8CE');
          planetGradient.addColorStop(0.5, '#97979F');
          planetGradient.addColorStop(1, '#7A7A85');
          break;
        case 2: // 金星 - 黄褐色云层
          planetGradient.addColorStop(0, '#FFFDE7');
          planetGradient.addColorStop(0.5, '#E7CDCD');
          planetGradient.addColorStop(1, '#D2B48C');
          break;
        case 3: // 地球 - 蓝绿色海洋和陆地
          planetGradient.addColorStop(0, '#A7C7E7');
          planetGradient.addColorStop(0.5, '#6B93D6');
          planetGradient.addColorStop(1, '#3A6B35');
          break;
        case 4: // 火星 - 红色岩石
          planetGradient.addColorStop(0, '#F5CCA0');
          planetGradient.addColorStop(0.5, '#E27B58');
          planetGradient.addColorStop(1, '#C1440E');
          break;
        case 5: // 木星 - 条纹云层
          planetGradient.addColorStop(0, '#F8E9A1');
          planetGradient.addColorStop(0.5, '#F6C555');
          planetGradient.addColorStop(1, '#B76E79');
          break;
        case 6: // 土星 - 淡黄色
          planetGradient.addColorStop(0, '#FFF8E7');
          planetGradient.addColorStop(0.5, '#F4D03F');
          planetGradient.addColorStop(1, '#D4AC0D');
          break;
        case 7: // 天王星 - 淡蓝色
          planetGradient.addColorStop(0, '#D6EAF8');
          planetGradient.addColorStop(0.5, '#85C1E9');
          planetGradient.addColorStop(1, '#3498DB');
          break;
        case 8: // 海王星 - 深蓝色
          planetGradient.addColorStop(0, '#AED6F1');
          planetGradient.addColorStop(0.5, '#5499C7');
          planetGradient.addColorStop(1, '#2E86C1');
          break;
        default:
          planetGradient.addColorStop(0, planet.color);
          planetGradient.addColorStop(1, shadeColor(planet.color, -20));
      }
      
      ctx.fillStyle = planetGradient;
      ctx.beginPath();
      ctx.arc(planetX, planetY, planet.radius, 0, Math.PI * 2);
      ctx.fill();
      
      // 为部分行星添加简单纹理特征 - 使用较低的透明度
      ctx.globalAlpha = 0.2; // 降低纹理透明度，使行星看起来更不透明
      
      // 添加行星表面特征
      const planetRotationOffset = planet.angle * 0.5; // 行星纹理旋转速度
      
      // 根据行星类型添加不同的表面特征
      if (i === 3) { // 地球 - 添加云层
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        for (let j = 0; j < 5; j++) {
          const cloudAngle = (j / 5) * Math.PI * 2 + planetRotationOffset;
          const cloudX = planetX + Math.cos(cloudAngle) * (planet.radius * 0.8);
          const cloudY = planetY + Math.sin(cloudAngle) * (planet.radius * 0.8);
          const cloudSize = planet.radius / 3;
          
          ctx.beginPath();
          ctx.arc(cloudX, cloudY, cloudSize, 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (i === 5) { // 木星 - 添加条纹
        ctx.fillStyle = 'rgba(180, 110, 100, 0.4)';
        for (let j = 0; j < 3; j++) {
          const stripY = planetY - planet.radius/2 + j * planet.radius/1.5;
          
          ctx.beginPath();
          ctx.ellipse(planetX, stripY, planet.radius * 0.9, planet.radius/5, 0, 0, Math.PI * 2);
          ctx.fill();
        }
      } else if (i === 6) { // 土星 - 添加光环
        // 保存当前上下文状态，以便进行变换
        ctx.save();
        
        // 移动到土星中心
        ctx.translate(planetX, planetY);
        
        // 添加倾斜角度，模拟土星环的倾斜
        const tiltAngle = Math.PI / 7; // 约26度倾角
        ctx.rotate(planetRotationOffset); // 随行星旋转
        ctx.transform(1, 0, 0, Math.cos(tiltAngle), 0, 0); // 应用倾斜变换
        
        // 绘制多层光环，增加真实感
        const ringLayers = 5;
        const innerRadius = planet.radius * 1.2;
        const outerRadius = planet.radius * 2.2;
        const ringStep = (outerRadius - innerRadius) / ringLayers;
        
        // 卡西尼分隔带 - 土星环中的暗色间隙
        const cassiniDivision = innerRadius + ringStep * 3.2;
        
        // 绘制多层光环
        for (let j = 0; j < ringLayers; j++) {
          const radius = innerRadius + j * ringStep;
          let alpha = 0.5 + (j / ringLayers) * 0.3; // 基础透明度
          
          // 卡西尼分隔带处透明度更高（更暗）
          if (Math.abs(radius - cassiniDivision) < ringStep * 0.3) {
            alpha = 0.1; // 分隔带更暗
          }
          
          // 根据环的位置设置不同颜色
          let ringColor;
          if (radius < cassiniDivision - ringStep * 0.3) {
            // B环 - 内环，更亮
            ringColor = `rgba(244, 208, 63, ${alpha})`;
          } else if (radius > cassiniDivision + ringStep * 0.3) {
            // A环 - 外环，略暗
            ringColor = `rgba(212, 172, 13, ${alpha})`;
          } else {
            // 卡西尼分隔带
            ringColor = `rgba(50, 50, 50, 0.1)`;
          }
          
          // 设置环的样式
          ctx.strokeStyle = ringColor;
          ctx.lineWidth = ringStep * 0.8;
          
          // 绘制环
          ctx.beginPath();
          ctx.arc(0, 0, radius, 0, Math.PI * 2);
          ctx.stroke();
        }
        
        // 恢复上下文状态
        ctx.restore();
        
        // 重置透明度
        ctx.globalAlpha = 1;
      }
      
      // 重置透明度，确保后续绘制不受影响
      ctx.globalAlpha = 1;
      
      // 绘制卫星
      for (const moon of planet.moons) {
        // 更新卫星角度
        moon.angle += moon.speed
        
        const moonX = planetX + Math.cos(moon.angle) * moon.distance
        const moonY = planetY + Math.sin(moon.angle) * moon.distance
        
        // 绘制卫星轨道
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)'
        ctx.beginPath()
        ctx.arc(planetX, planetY, moon.distance, 0, Math.PI * 2)
        ctx.stroke()
        
        // 绘制卫星
        ctx.fillStyle = moon.color
        ctx.beginPath()
        ctx.arc(moonX, moonY, moon.radius, 0, Math.PI * 2)
        ctx.fill()
      }
    }
    
    animationId = requestAnimationFrame(animate)
  }
  
  animate()
}

onMounted(() => {
  initSolarSystem()
  
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
/* 太阳系容器 */
.solar-system-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: transparent; /* 移除背景色，让星空背景透过 */
}

/* 画布样式 */
canvas {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover; /* 修改为cover，确保画布覆盖整个容器 */
}

/* 覆盖文本样式 */
.overlay-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 10;
  color: white;
  animation: fadeIn 1.5s ease-in-out;
  width: 80%;
  max-width: 500px;
}

/* 文本淡入动画 */
@keyframes fadeIn {
  from { 
    opacity: 0; 
    transform: translate(-50%, -60%); 
  }
  to { 
    opacity: 1; 
    transform: translate(-50%, -50%); 
  }
}

/* 为左侧面板添加样式 */
:deep(.auth-left-panel) {
  position: relative;
  width: 66.67%; /* 改为2/3的屏幕宽度 */
  height: 100%;
  overflow: hidden;
  flex-shrink: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  :deep(.auth-left-panel) {
    display: none; /* 在小屏幕上隐藏太阳系 */
  }
}
</style>