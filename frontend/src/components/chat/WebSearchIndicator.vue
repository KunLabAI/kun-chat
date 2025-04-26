<template>
  <div class="web-search-indicator">
    <div class="search-animation-container">
      <div class="top-section">
        <div class="rotating-globe-icon">
          <div class="globe-sphere"></div>
          <div class="globe-lines"></div>
        </div>
        <span class="search-text">网页搜索中...</span>
      </div>
      <div class="bottom-section"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 暴露方法给父组件 - 简化版本不需要步骤管理
defineExpose({})

// 简化版本不需要监听props变化和启动动画</script>

<style scoped>
.web-search-indicator {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
}

.search-animation-container {
  min-width: 348px; /* 使用100%宽度以适应父容器 */
  width: 100%;
  height: 48px; /* 容器高度 */
  display: flex;
  flex-direction: column; /* 垂直布局 */
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden; /* 隐藏超出范围的内容 */
}

.top-section {
  flex-grow: 3; /* 调整 flex-grow 以适应新的底部高度 */
  display: flex;
  align-items: center;
  justify-content: center; /* 水平居中 */
  gap: 8px; /* 图标和文字之间的间隔 */
  font-size: 14px;
}

.search-text {
  /* 文字样式，保持原有的字体粗细 */
  font-weight: 500;
  color: var(--text-color-light);
}

/* 旋转地球图标容器 */
.rotating-globe-icon {
  width: 16px; /* 图标大小 */
  height: 16px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--primary-color, #a200ff);
  animation: rotate-globe 4s linear infinite; /* 应用旋转动画 */
  flex-shrink: 0; /* 防止图标被挤压 */
}

/* 地球球体 */
.rotating-globe-icon .globe-sphere {
  width: 100%;
  height: 100%;
  border: 1.5px solid currentColor; /* 球体颜色继承 */
  border-radius: 50%;
  box-sizing: border-box;
  background-color: #f4bdff; /* 浅蓝色背景模拟海洋 */
}

/* 地球上的线条 (模拟经纬线或大陆) */
.rotating-globe-icon .globe-lines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  box-sizing: border-box;
  /* 使用径向渐变和线性渐变模拟线条 */
  background:
    radial-gradient(circle at center, transparent 50%, currentColor 50.5%, currentColor 51%, transparent 51.5%), /* 中心圆点或环 */
    linear-gradient(to right, transparent 40%, currentColor 40.5%, currentColor 41.5%, transparent 42%), /* 垂直线条 */
    linear-gradient(to bottom, transparent 40%, currentColor 40.5%, currentColor 41.5%, transparent 42%); /* 水平线条 */
  background-size: 100% 100%;
  background-repeat: no-repeat;
  opacity: 1; /* 让线条稍微透明 */
}

.bottom-section {
  height: 4px; /* 设置底部区域固定高度为4px */
  flex-grow: 0; /* flex-grow 设为 0，高度由 height 属性决定 */
  width: 100%; /* 宽度充满容器 */
  /* RGB色彩变化动画 */
  /* 增加更多颜色，使变化更丰富和平缓 */
  background: linear-gradient(to right,
    #ff0000, #ff4000, #ff8000, #ffbf00, #ffff00, #bfff00, #80ff00, #40ff00, #00ff00, /* 绿色系 */
    #00ff40, #00ff80, #00ffbf, #00ffff, #00bfff, #0080ff, #0040ff, #0000ff, /* 蓝色系 */
    #4000ff, #8000ff, #bf00ff, #ff00ff, #ff00bf, #ff0080, #ff0040, #ff0000 /* 紫色和红色系，并重复开始颜色 */
  );
  background-size: 1000% 200%; /* 显著增加渐变宽度，使变化更平缓 */
  animation: rgb-sweep 2s infinite linear; /* 增加动画时长，使移动更慢 */
}

/* 动画关键帧定义 */

/* 地球旋转动画 */
@keyframes rotate-globe {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* RGB色彩变化动画 */
@keyframes rgb-sweep {
  0% {
    background-position: 0% 0; /* 从左侧开始 */
  }
  100% {
    background-position: 100% 0; /* 移动到右侧 */
  }
}
</style>