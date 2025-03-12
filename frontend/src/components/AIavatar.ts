import { h } from 'vue'
import type { Component } from 'vue'

interface BubbleAvatarProps {
  width?: number
  height?: number
}

export const BubbleAvatar: Component<BubbleAvatarProps> = (props = { width: 40, height: 40 }) => {
  return h('svg', {
    width: props.width,
    height: props.height,
    viewBox: '0 0 100 100'
  }, [
    h('defs', {}, [
      h('radialGradient', {
        id: 'pinkGradient',
        cx: '50%',
        cy: '50%',
        r: '50%',
        fx: '50%',
        fy: '50%'
      }, [
        h('stop', { offset: '0%', 'stop-color': '#FF0059', 'stop-opacity': '0.8' }),
        h('stop', { offset: '100%', 'stop-color': '#FF0059', 'stop-opacity': '0' })
      ]),
      h('radialGradient', {
        id: 'blueGradient',
        cx: '50%',
        cy: '50%',
        r: '50%',
        fx: '50%',
        fy: '50%'
      }, [
        h('stop', { offset: '0%', 'stop-color': '#00A5FD', 'stop-opacity': '0.8' }),
        h('stop', { offset: '100%', 'stop-color': '#00A5FD', 'stop-opacity': '0' })
      ]),
      h('radialGradient', {
        id: 'violetGradient',
        cx: '50%',
        cy: '50%',
        r: '50%',
        fx: '50%',
        fy: '50%'
      }, [
        h('stop', { offset: '0%', 'stop-color': '#BA00FD', 'stop-opacity': '0.8' }),
        h('stop', { offset: '100%', 'stop-color': '#BA00FD', 'stop-opacity': '0' })
      ]),
      h('radialGradient', {
        id: 'yellowGradient',
        cx: '50%',
        cy: '50%',
        r: '50%',
        fx: '50%',
        fy: '50%'
      }, [
        h('stop', { offset: '0%', 'stop-color': '#FFC800', 'stop-opacity': '0.8' }),
        h('stop', { offset: '100%', 'stop-color': '#FFC800', 'stop-opacity': '0' })
      ])
    ]),
    // 整个组添加上下浮动动画
    h('g', {
      transform: 'translate(0, 0)'
    }, [
      // 背景圆
      h('circle', { 
        cx: '50', 
        cy: '50', 
        r: '48', 
        fill: '#000000' 
      }),
      // 渐变圆形
      h('circle', { 
        cx: '50', 
        cy: '50', 
        r: '45', 
        fill: 'url(#pinkGradient)',
      }),
      h('circle', { 
        cx: '40', 
        cy: '40', 
        r: '45', 
        fill: 'url(#blueGradient)',
      }),
      h('circle', { 
        cx: '60', 
        cy: '40', 
        r: '40', 
        fill: 'url(#violetGradient)',
      }),
      h('circle', { 
        cx: '50', 
        cy: '60', 
        r: '35', 
        fill: 'url(#yellowGradient)',
      }),
      // 中心光晕
      h('circle', { 
        cx: '50', 
        cy: '50', 
        r: '20', 
        fill: '#FFFFFF', 
        'fill-opacity': '0.2',
      }),
      // 高光点
      h('circle', { 
        cx: '35', 
        cy: '35', 
        r: '8', 
        fill: '#FFFFFF', 
        'fill-opacity': '0.6',
      }),
      // 添加上下浮动动画
      h('animateTransform', {
        attributeName: 'transform',
        type: 'translate',
        values: '0 0; 0 -2; 0 1',
        dur: '2',
        repeatCount: 'indefinite',
        additive: 'sum'
      })
    ])
  ])
}
