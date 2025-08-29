import { nextTick } from 'vue'

// 动画工具类
export class AnimationUtils {
  /**
   * 为元素添加CSS类名并在指定时间后移除
   */
  static async addClass(
    element: HTMLElement | string, 
    className: string, 
    duration?: number
  ): Promise<void> {
    const el = typeof element === 'string' ? document.querySelector(element) as HTMLElement : element
    if (!el) return

    el.classList.add(className)
    
    if (duration) {
      setTimeout(() => {
        el.classList.remove(className)
      }, duration)
    }
  }

  /**
   * 页面进入动画
   */
  static async pageEnterAnimation(container: HTMLElement | string): Promise<void> {
    const el = typeof container === 'string' ? document.querySelector(container) as HTMLElement : container
    if (!el) return

    el.style.opacity = '0'
    el.style.transform = 'translateY(20px)'
    
    await nextTick()
    
    el.style.transition = 'all 0.6s ease-out'
    el.style.opacity = '1'
    el.style.transform = 'translateY(0)'
  }

  /**
   * 卡片入场动画（批量）
   */
  static async staggerCards(
    cards: HTMLElement[] | NodeListOf<HTMLElement>, 
    delay = 100
  ): Promise<void> {
    const cardArray = Array.from(cards)
    
    cardArray.forEach((card, index) => {
      card.style.opacity = '0'
      card.style.transform = 'translateY(30px) scale(0.9)'
      
      setTimeout(() => {
        card.style.transition = 'all 0.5s ease-out'
        card.style.opacity = '1'
        card.style.transform = 'translateY(0) scale(1)'
      }, index * delay)
    })
  }

  /**
   * 数字递增动画
   */
  static animateNumber(
    element: HTMLElement,
    from: number,
    to: number,
    duration = 2000,
    formatter?: (value: number) => string
  ): void {
    const startTime = Date.now()
    const difference = to - from

    const step = () => {
      const currentTime = Date.now()
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 使用easeOutQuart缓动函数
      const easedProgress = 1 - Math.pow(1 - progress, 4)
      const currentValue = from + (difference * easedProgress)
      
      const displayValue = formatter ? formatter(currentValue) : Math.round(currentValue).toString()
      element.textContent = displayValue
      
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }
    
    requestAnimationFrame(step)
  }

  /**
   * 粒子效果（点击反馈）
   */
  static createRipple(event: MouseEvent, element: HTMLElement): void {
    const ripple = document.createElement('div')
    const rect = element.getBoundingClientRect()
    const size = Math.max(rect.width, rect.height)
    const x = event.clientX - rect.left - size / 2
    const y = event.clientY - rect.top - size / 2

    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%);
      border-radius: 50%;
      pointer-events: none;
      transform: scale(0);
      animation: ripple 0.6s ease-out;
    `

    element.style.position = 'relative'
    element.style.overflow = 'hidden'
    element.appendChild(ripple)

    setTimeout(() => {
      ripple.remove()
    }, 600)
  }

  /**
   * 打字机效果
   */
  static typewriter(
    element: HTMLElement, 
    text: string, 
    speed = 100,
    cursor = true
  ): Promise<void> {
    return new Promise((resolve) => {
      element.textContent = ''
      
      if (cursor) {
        element.style.borderRight = '2px solid #2196f3'
        element.style.paddingRight = '2px'
      }

      let i = 0
      const timer = setInterval(() => {
        element.textContent += text[i]
        i++
        
        if (i >= text.length) {
          clearInterval(timer)
          
          if (cursor) {
            // 闪烁光标效果
            setTimeout(() => {
              element.style.borderRight = 'none'
              resolve()
            }, 1000)
          } else {
            resolve()
          }
        }
      }, speed)
    })
  }

  /**
   * 滚动到元素位置的平滑动画
   */
  static scrollToElement(
    element: HTMLElement | string, 
    offset = 0, 
    duration = 800
  ): void {
    const el = typeof element === 'string' ? document.querySelector(element) as HTMLElement : element
    if (!el) return

    const targetPosition = el.offsetTop + offset
    const startPosition = window.pageYOffset
    const distance = targetPosition - startPosition
    const startTime = Date.now()

    const step = () => {
      const currentTime = Date.now()
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // 使用easeInOutQuart缓动
      const easedProgress = progress < 0.5 
        ? 8 * progress * progress * progress * progress
        : 1 - Math.pow(-2 * progress + 2, 4) / 2

      window.scrollTo(0, startPosition + distance * easedProgress)
      
      if (progress < 1) {
        requestAnimationFrame(step)
      }
    }
    
    requestAnimationFrame(step)
  }

  /**
   * 元素淡入淡出
   */
  static fadeToggle(element: HTMLElement, show: boolean, duration = 300): Promise<void> {
    return new Promise((resolve) => {
      element.style.transition = `opacity ${duration}ms ease-in-out`
      
      if (show) {
        element.style.display = 'block'
        element.style.opacity = '0'
        
        requestAnimationFrame(() => {
          element.style.opacity = '1'
        })
        
        setTimeout(resolve, duration)
      } else {
        element.style.opacity = '0'
        
        setTimeout(() => {
          element.style.display = 'none'
          resolve()
        }, duration)
      }
    })
  }

  /**
   * 脉冲效果
   */
  static pulse(element: HTMLElement, scale = 1.05, duration = 600): void {
    element.style.transition = `transform ${duration / 2}ms ease-out`
    element.style.transform = `scale(${scale})`
    
    setTimeout(() => {
      element.style.transform = 'scale(1)'
    }, duration / 2)
  }

  /**
   * 晃动效果
   */
  static shake(element: HTMLElement, intensity = 10, duration = 600): void {
    const keyframes = [
      { transform: 'translateX(0)' },
      { transform: `translateX(-${intensity}px)` },
      { transform: `translateX(${intensity}px)` },
      { transform: `translateX(-${intensity / 2}px)` },
      { transform: `translateX(${intensity / 2}px)` },
      { transform: 'translateX(0)' }
    ]

    element.animate(keyframes, {
      duration,
      easing: 'ease-in-out'
    })
  }

  /**
   * 弹跳效果
   */
  static bounce(element: HTMLElement, height = 10, duration = 600): void {
    const keyframes = [
      { transform: 'translateY(0)' },
      { transform: `translateY(-${height}px)` },
      { transform: 'translateY(0)' },
      { transform: `translateY(-${height / 2}px)` },
      { transform: 'translateY(0)' }
    ]

    element.animate(keyframes, {
      duration,
      easing: 'ease-out'
    })
  }
}

// Vue 3 组合式API钩子
export const useAnimations = () => {
  const animateOnMount = async (refs: { [key: string]: any }) => {
    await nextTick()
    
    Object.entries(refs).forEach(([key, ref], index) => {
      if (ref.value) {
        setTimeout(() => {
          AnimationUtils.addClass(ref.value, 'fade-in slide-in-up')
        }, index * 100)
      }
    })
  }

  const staggerAnimation = async (containerRef: any, itemClass: string) => {
    await nextTick()
    
    if (containerRef.value) {
      const items = containerRef.value.querySelectorAll(itemClass)
      AnimationUtils.staggerCards(items)
    }
  }

  return {
    AnimationUtils,
    animateOnMount,
    staggerAnimation
  }
}

// CSS动画类名常量
export const ANIMATION_CLASSES = {
  FADE_IN: 'fade-in',
  SLIDE_IN_UP: 'slide-in-up',
  SLIDE_IN_DOWN: 'slide-in-down',
  BOUNCE_IN: 'bounce-in',
  SCALE_IN: 'scale-in',
  ROTATE_IN: 'rotate-in',
  HOVER_LIFT: 'hover-lift',
  HOVER_GLOW: 'hover-glow',
  HOVER_SCALE: 'hover-scale',
  CARD_ENTRANCE: 'card-entrance',
  LOADING_PULSE: 'loading-pulse',
  LOADING_SPIN: 'loading-spin',
  TEXT_GRADIENT: 'text-gradient'
}