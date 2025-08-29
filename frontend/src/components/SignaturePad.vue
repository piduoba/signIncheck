<template>
  <div class="signature-pad-container">
    <div class="signature-header" v-if="showHeader">
      <span class="signature-title">{{ title }}</span>
      <div class="signature-tools">
        <el-button-group size="small">
          <el-button @click="undo" :disabled="!canUndo">
            <el-icon><Back /></el-icon>
            撤销
          </el-button>
          <el-button @click="clear">
            <el-icon><RefreshLeft /></el-icon>
            清除
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <div class="signature-canvas-wrapper" :style="canvasWrapperStyle">
      <canvas
        ref="canvasRef"
        class="signature-canvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="handleStart"
        @mousemove="handleMove"
        @mouseup="handleEnd"
        @mouseleave="handleEnd"
        @touchstart.prevent="handleStart"
        @touchmove.prevent="handleMove"
        @touchend.prevent="handleEnd"
      />
      
      <!-- 占位符文字 -->
      <div v-if="!hasSignature && showPlaceholder" class="signature-placeholder">
        {{ placeholder }}
      </div>
      
      <!-- 签名指导线 -->
      <div v-if="showGuidelines" class="signature-guidelines">
        <div class="guideline baseline"></div>
        <div class="guideline topline"></div>
        <div class="guideline bottomline"></div>
      </div>
    </div>
    
    <!-- 签名信息 -->
    <div class="signature-info" v-if="showInfo">
      <div class="info-item">
        <span class="label">笔触颜色：</span>
        <el-color-picker
          v-model="strokeColor"
          size="small"
          @change="updateStrokeColor"
        />
      </div>
      <div class="info-item">
        <span class="label">笔触粗细：</span>
        <el-slider
          v-model="strokeWidth"
          :min="1"
          :max="10"
          :step="0.5"
          style="width: 100px;"
          @change="updateStrokeWidth"
        />
      </div>
      <div class="info-item">
        <span class="label">签名质量：</span>
        <el-rate
          v-model="signatureQuality"
          disabled
          show-score
          text-color="#ff9900"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'

interface Point {
  x: number
  y: number
  pressure?: number
  timestamp: number
}

interface Stroke {
  points: Point[]
  color: string
  width: number
}

interface SignaturePadProps {
  width?: number
  height?: number
  title?: string
  placeholder?: string
  showHeader?: boolean
  showPlaceholder?: boolean
  showGuidelines?: boolean
  showInfo?: boolean
  strokeColor?: string
  strokeWidth?: number
  backgroundColor?: string
  penColor?: string
}

interface SignaturePadEmits {
  (e: 'change', signature: string): void
  (e: 'start'): void
  (e: 'end'): void
  (e: 'clear'): void
}

const props = withDefaults(defineProps<SignaturePadProps>(), {
  width: 600,
  height: 200,
  title: '请在下方签名',
  placeholder: '请在此区域内签名',
  showHeader: true,
  showPlaceholder: true,
  showGuidelines: false,
  showInfo: false,
  strokeColor: '#000000',
  strokeWidth: 2,
  backgroundColor: '#ffffff',
  penColor: '#000000'
})

const emit = defineEmits<SignaturePadEmits>()

// 响应式数据
const canvasRef = ref<HTMLCanvasElement>()
const isDrawing = ref(false)
const hasSignature = ref(false)
const strokes = ref<Stroke[]>([])
const currentStroke = ref<Stroke | null>(null)
const lastPoint = ref<Point | null>(null)
const strokeColor = ref(props.strokeColor)
const strokeWidth = ref(props.strokeWidth)

// 计算属性
const canvasWidth = computed(() => props.width)
const canvasHeight = computed(() => props.height)
const canvasWrapperStyle = computed(() => ({
  width: `${props.width}px`,
  height: `${props.height}px`
}))

const canUndo = computed(() => strokes.value.length > 0)

const signatureQuality = computed(() => {
  if (!hasSignature.value) return 0
  
  // 基于笔画数量、长度等计算签名质量
  const strokeCount = strokes.value.length
  const totalPoints = strokes.value.reduce((sum, stroke) => sum + stroke.points.length, 0)
  
  if (strokeCount === 0) return 0
  if (strokeCount < 2) return 1
  if (strokeCount < 5 && totalPoints > 10) return 2
  if (strokeCount < 8 && totalPoints > 20) return 3
  if (strokeCount >= 5 && totalPoints > 30) return 4
  if (strokeCount >= 8 && totalPoints > 50) return 5
  
  return 3 // 默认中等质量
})

// 获取画布上下文
const getContext = (): CanvasRenderingContext2D | null => {
  const canvas = canvasRef.value
  if (!canvas) return null
  return canvas.getContext('2d')
}

// 初始化画布
const initCanvas = () => {
  const canvas = canvasRef.value
  const ctx = getContext()
  if (!canvas || !ctx) return

  // 设置画布样式
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  ctx.strokeStyle = strokeColor.value
  ctx.lineWidth = strokeWidth.value

  // 填充背景色
  ctx.fillStyle = props.backgroundColor
  ctx.fillRect(0, 0, canvas.width, canvas.height)
}

// 获取事件坐标
const getEventPos = (event: MouseEvent | TouchEvent): Point => {
  const canvas = canvasRef.value
  if (!canvas) return { x: 0, y: 0, timestamp: Date.now() }

  const rect = canvas.getBoundingClientRect()
  const scaleX = canvas.width / rect.width
  const scaleY = canvas.height / rect.height

  let clientX: number, clientY: number

  if ('touches' in event && event.touches.length > 0) {
    clientX = event.touches[0].clientX
    clientY = event.touches[0].clientY
  } else if ('clientX' in event) {
    clientX = event.clientX
    clientY = event.clientY
  } else {
    return { x: 0, y: 0, timestamp: Date.now() }
  }

  return {
    x: (clientX - rect.left) * scaleX,
    y: (clientY - rect.top) * scaleY,
    pressure: 'pressure' in event ? (event as any).pressure : 0.5,
    timestamp: Date.now()
  }
}

// 开始绘制
const handleStart = (event: MouseEvent | TouchEvent) => {
  const point = getEventPos(event)
  
  isDrawing.value = true
  lastPoint.value = point
  hasSignature.value = true

  // 创建新笔画
  currentStroke.value = {
    points: [point],
    color: strokeColor.value,
    width: strokeWidth.value
  }

  const ctx = getContext()
  if (ctx) {
    ctx.strokeStyle = strokeColor.value
    ctx.lineWidth = strokeWidth.value
    ctx.beginPath()
    ctx.moveTo(point.x, point.y)
  }

  emit('start')
}

// 绘制移动
const handleMove = (event: MouseEvent | TouchEvent) => {
  if (!isDrawing.value || !lastPoint.value || !currentStroke.value) return

  const point = getEventPos(event)
  currentStroke.value.points.push(point)

  const ctx = getContext()
  if (ctx) {
    // 使用二次贝塞尔曲线进行平滑绘制
    const midPoint = {
      x: (lastPoint.value.x + point.x) / 2,
      y: (lastPoint.value.y + point.y) / 2,
      timestamp: Date.now()
    }

    ctx.quadraticCurveTo(lastPoint.value.x, lastPoint.value.y, midPoint.x, midPoint.y)
    ctx.stroke()
  }

  lastPoint.value = point
}

// 结束绘制
const handleEnd = () => {
  if (!isDrawing.value || !currentStroke.value) return

  isDrawing.value = false
  
  // 保存当前笔画
  strokes.value.push({ ...currentStroke.value })
  currentStroke.value = null
  lastPoint.value = null

  // 触发变化事件
  emitChange()
  emit('end')
}

// 清除签名
const clear = () => {
  const ctx = getContext()
  if (!ctx) return

  strokes.value = []
  hasSignature.value = false
  isDrawing.value = false
  currentStroke.value = null
  lastPoint.value = null

  // 清除画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 重新填充背景
  ctx.fillStyle = props.backgroundColor
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)

  emitChange()
  emit('clear')
}

// 撤销最后一笔
const undo = () => {
  if (strokes.value.length === 0) return

  strokes.value.pop()
  redraw()
  
  if (strokes.value.length === 0) {
    hasSignature.value = false
  }
  
  emitChange()
}

// 重新绘制所有笔画
const redraw = () => {
  const ctx = getContext()
  if (!ctx) return

  // 清除画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 填充背景
  ctx.fillStyle = props.backgroundColor
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)

  // 重新绘制所有笔画
  strokes.value.forEach(stroke => {
    if (stroke.points.length === 0) return

    ctx.strokeStyle = stroke.color
    ctx.lineWidth = stroke.width
    ctx.beginPath()
    
    const firstPoint = stroke.points[0]
    ctx.moveTo(firstPoint.x, firstPoint.y)

    for (let i = 1; i < stroke.points.length; i++) {
      const point = stroke.points[i]
      const prevPoint = stroke.points[i - 1]
      
      const midPoint = {
        x: (prevPoint.x + point.x) / 2,
        y: (prevPoint.y + point.y) / 2
      }
      
      ctx.quadraticCurveTo(prevPoint.x, prevPoint.y, midPoint.x, midPoint.y)
    }
    
    ctx.stroke()
  })
}

// 更新笔触颜色
const updateStrokeColor = (color: string) => {
  strokeColor.value = color
}

// 更新笔触粗细
const updateStrokeWidth = (width: number) => {
  strokeWidth.value = width
}

// 获取签名数据URL
const getDataURL = (type = 'image/png', quality = 1): string => {
  const canvas = canvasRef.value
  if (!canvas) return ''
  return canvas.toDataURL(type, quality)
}

// 获取签名数据
const getSignatureData = () => {
  return {
    strokes: strokes.value,
    dataURL: getDataURL(),
    isEmpty: !hasSignature.value,
    quality: signatureQuality.value
  }
}

// 触发变化事件
const emitChange = () => {
  const dataURL = getDataURL()
  emit('change', dataURL)
}

// 加载签名数据
const loadSignature = (dataURL: string) => {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = getContext()
  if (!ctx) return

  const img = new Image()
  img.onload = () => {
    clear()
    ctx.drawImage(img, 0, 0, canvasWidth.value, canvasHeight.value)
    hasSignature.value = true
    emitChange()
  }
  img.src = dataURL
}

// 暴露方法给父组件
defineExpose({
  clear,
  undo,
  getDataURL,
  getSignatureData,
  loadSignature,
  isEmpty: computed(() => !hasSignature.value)
})

onMounted(() => {
  nextTick(() => {
    initCanvas()
  })
})

// 监听props变化
watch([() => props.strokeColor, () => props.strokeWidth], () => {
  strokeColor.value = props.strokeColor
  strokeWidth.value = props.strokeWidth
})
</script>

<style scoped>
.signature-pad-container {
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  overflow: hidden;
  background-color: #ffffff;
}

.signature-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.signature-title {
  font-weight: 500;
  color: #333;
}

.signature-canvas-wrapper {
  position: relative;
  background-color: #ffffff;
  overflow: hidden;
}

.signature-canvas {
  display: block;
  cursor: crosshair;
  width: 100%;
  height: 100%;
}

.signature-placeholder {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #999;
  font-size: 16px;
  pointer-events: none;
  user-select: none;
}

.signature-guidelines {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.guideline {
  position: absolute;
  left: 20px;
  right: 20px;
  height: 1px;
  background-color: #e8eaec;
}

.baseline {
  bottom: 30%;
}

.topline {
  top: 30%;
}

.bottomline {
  bottom: 20%;
}

.signature-info {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 16px;
  background-color: #f8f9fa;
  border-top: 1px solid #eee;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .signature-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }

  .signature-info {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .info-item {
    justify-content: space-between;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  .signature-canvas {
    cursor: default;
  }
}
</style>