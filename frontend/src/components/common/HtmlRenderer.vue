<template>
  <div class="html-renderer">
    <div class="html-container" ref="htmlContainer">
      <IframeResizer
        class="html-iframe"
        :src="iframeSrc"
        :options="iframeOptions"
        @load="handleIframeLoad"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount, onMounted } from 'vue'
import IframeResizer from '@iframe-resizer/vue/sfc'
import DOMPurify from 'dompurify'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  language: {
    type: String,
    required: true
  }
})

const htmlContainer = ref(null)
const iframeSrc = ref('')
const iframeOptions = {
  scrolling: false,
  checkOrigin: false,
  sizeWidth: true,
  heightCalculationMethod: 'lowestElement',
  warningTimeout: 0,
  log: false,
  license: 'GPLv3', 
  sandbox: 'allow-scripts allow-same-origin allow-modals allow-forms allow-popups allow-presentation allow-downloads allow-pointer-lock'
}

// 处理iframe加载完成事件
const handleIframeLoad = (iframe) => {
  console.log('Iframe loaded successfully')
  
  // 可以在这里添加额外的iframe加载后处理逻辑
  try {
    // 确保iframe内容已完全加载
    if (iframe && iframe.contentWindow) {
      // 可以在这里访问iframe内容
      console.log('Iframe content loaded')
    }
  } catch (error) {
    console.error('Error accessing iframe content:', error)
  }
}

// 创建一个blob URL用于iframe的src
const createHtmlDoc = (content) => {
  // 使用字符串变量来构建HTML文档，通过字符串拼接避免Vue编译器解析错误
  const doctype = '<!DOCTYPE html>';
  const htmlOpen = '<' + 'html' + '>';
  const htmlClose = '</' + 'html' + '>';
  const headOpen = '<' + 'head' + '>';
  const headClose = '</' + 'head' + '>';
  const bodyOpen = '<' + 'body' + '>';
  const bodyClose = '</' + 'body' + '>';
  const metaCharset = '<' + 'meta charset="UTF-8"' + '>';
  const metaViewport = '<' + 'meta name="viewport" content="width=device-width, initial-scale=1.0"' + '>';
  const title = '<' + 'title' + '>HTML Preview</' + 'title' + '>';
  
  // iframe-resizer脚本
  const scriptOpen = '<' + 'script' + '>';
  const scriptClose = '</' + 'script' + '>';
  const iframeResizerScript = `
    // iframe-resizer contentWindow代码
    (function() {
      if (window.parentIFrame) return;
      window.parentIFrame = {
        // 添加GPLv3许可证密钥
        license: 'GPLv3',
        size: function(customHeight, customWidth) {
          var height = customHeight || document.documentElement.offsetHeight || document.body.offsetHeight;
          var width = customWidth || document.documentElement.offsetWidth || document.body.offsetWidth;
          window.parent.postMessage({
            iframe: window.name,
            type: "resize",
            height: height,
            width: width
          }, "*");
        }
      };
      window.addEventListener("resize", function() { window.parentIFrame.size(); });
      document.addEventListener("DOMContentLoaded", function() {
        setTimeout(function() { window.parentIFrame.size(); }, 50);
      });
    })();
  `;
  
  // 默认样式
  const styleOpen = '<' + 'style' + '>';
  const styleClose = '</' + 'style' + '>';
  const defaultStyles = `
    html, body { margin: 0; padding: 0; width: 100%; height: auto; overflow-x: hidden; }
    body { padding: 8px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #333; line-height: 1.5; }
    h1, h2, h3, h4, h5, h6 { margin-top: 1em; margin-bottom: 0.5em; font-weight: 600; line-height: 1.25; }
    p { margin-top: 0; margin-bottom: 1em; }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    img, svg { max-width: 100%; height: auto; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f6f8fa; }
    code, pre { font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; background-color: #f6f8fa; border-radius: 3px; }
    code { padding: 0.2em 0.4em; font-size: 85%; }
    pre { padding: 16px; overflow: auto; line-height: 1.45; }
    pre code { background-color: transparent; padding: 0; }
    canvas { max-width: 100%; display: block; }
  `;
  
  // 脚本处理
  const canvasScript = `
    // 创建一个全局对象来存储canvas引用
    window.canvasElements = {};
    document.addEventListener("DOMContentLoaded", function() {
      // 处理canvas元素
      const canvasElements = document.querySelectorAll("canvas");
      canvasElements.forEach((canvas, index) => {
        if (canvas.id) {
          canvas.setAttribute("data-original-id", canvas.id);
          window.canvasElements[canvas.id] = canvas;
        } else {
          const generatedId = "canvas-" + index;
          canvas.id = generatedId;
          window.canvasElements[generatedId] = canvas;
        }
      });
      
      // 添加辅助函数
      window.getCanvas = function(id) {
        return window.canvasElements[id] || document.getElementById(id);
      };
      
      // 执行脚本
      const scripts = document.querySelectorAll("script:not([src]):not([data-executed=\\"true\\"])");
      scripts.forEach(script => {
        try {
          script.setAttribute("data-executed", "true");
          let scriptContent = script.textContent;
          const scriptFunction = new Function(scriptContent);
          scriptFunction.call(window);
        } catch (error) {
          console.error("执行脚本时出错:", error);
        }
      });
      
      // 通知父窗口内容已加载完成
      if (window.parentIFrame) {
        window.parentIFrame.size();
      }
    });
  `;
  
  // 构建HTML文档
  let html = doctype + '\n' + htmlOpen + '\n' + headOpen + '\n';
  html += metaCharset + '\n' + metaViewport + '\n' + title + '\n';
  html += scriptOpen + iframeResizerScript + scriptClose + '\n';
  
  // 添加默认样式
  html += styleOpen + defaultStyles + styleClose + '\n';
  
  // 添加body内容
  html += headClose + '\n' + bodyOpen + '\n';
  html += content + '\n';
  html += scriptOpen + canvasScript + scriptClose + '\n';
  html += bodyClose + '\n' + htmlClose;
  
  return html;
};

const createBlobUrl = (htmlContent) => {
  // 如果是SVG，添加SVG标签
  if (props.language === 'svg' && !htmlContent.includes('<svg')) {
    // 使用变量拼接SVG标签，避免Vue编译器解析错误
    const svgOpen = '<' + 'svg xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" viewBox="0 0 800 600"' + '>';
    const svgClose = '</' + 'svg' + '>';
    htmlContent = svgOpen + htmlContent + svgClose;
  }
  
  // 清理HTML内容
  const cleanHtml = DOMPurify.sanitize(htmlContent, {
    ADD_TAGS: ['iframe', 'canvas', 'script'],
    ADD_ATTR: [
      'allow', 'allowfullscreen', 'frameborder', 'scrolling', 'width', 'height',
      'onclick', 'ondblclick', 'onmousedown', 'onmousemove', 'onmouseout',
      'onmouseover', 'onmouseup', 'onkeydown', 'onkeypress', 'onkeyup',
      'onload', 'onunload', 'sandbox'
    ],
    FORCE_BODY: true,
    SANITIZE_DOM: true
  });
  
  // 创建完整的HTML文档
  const htmlDoc = createHtmlDoc(cleanHtml);
  
  // 创建Blob对象
  const blob = new Blob([htmlDoc], { type: 'text/html' });
  
  // 创建URL
  return URL.createObjectURL(blob);
};

// 监听内容变化，更新iframe
watch(() => props.content, (newContent) => {
  if (newContent) {
    // 释放旧的Blob URL
    if (iframeSrc.value && iframeSrc.value.startsWith('blob:')) {
      URL.revokeObjectURL(iframeSrc.value)
    }
    
    // 创建新的Blob URL
    iframeSrc.value = createBlobUrl(newContent)
  }
}, { immediate: true })

onMounted(() => {
  console.log('HtmlRenderer component mounted')
})

// 组件卸载前清理资源
onBeforeUnmount(() => {
  // 释放Blob URL
  if (iframeSrc.value && iframeSrc.value.startsWith('blob:')) {
    URL.revokeObjectURL(iframeSrc.value)
  }
})
</script>

<style scoped>
.html-renderer {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.html-container {
  flex: 1;
  overflow: hidden;
  border-radius: 6px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.html-iframe {
  width: 100%;
  height: 100%;
  min-height: 200px;
  border: none;
  display: block;
}

:global(.dark) .html-container {
  background-color: #1e1e2e;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}
</style>