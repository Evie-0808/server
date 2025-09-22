<template>
  <div class="app">
    <h1>World Model Simulator</h1>
    <div class="chat-box">
      <!-- 输入框：宽度随 chat-box 适配 -->
      <input 
      v-model="message" 
        @keyup.enter="sendMessage"
        class="chat-input"  
        :disabled="isProcessing" 
        :placeholder="isProcessing ? '处理中，请稍候...' : 'Input scene description...e.g. The scene in an busy intersection with 32 cars'" 
      >
      <!-- 按钮：与输入框适配 -->
      <div class="btn-group">  <!-- 新增：用容器包裹按钮和提示，便于排版 -->
        <button 
          @click="sendMessage" 
          class="chat-btn"
          :disabled="isProcessing" 
        >
          {{ isProcessing ? '生成中...' : 'Generate' }}  <!-- 动态按钮文本 -->
        </button>
        <!-- 新增：加载中提示文本（颜色浅灰，突出状态） -->
        <span class="loading-text">{{ loadStatus }}</span>
      </div>
      


      <!-- 回复区域：随 chat-box 宽度适配 -->
      <div v-if="reply" class="reply-container">
        <div class="reply-text">{{ reply }}</div>
      </div>
    </div>

    <div v-if="imageUrls.length > 0" class="image-viewer">
      <img 
        :src="`http://10.253.15.87:10001${imageUrls[currentIndex]}?ts=${updateTime}`"
        class="seq-frame"
        :alt="`序列帧 ${currentIndex + 1}/${imageUrls.length}`"
      >
      
      <!-- 切换按钮 -->
      <div class="navigation-buttons">
        <button 
          @click="prevImage" 
          :disabled="currentIndex === 0"  
          class="nav-btn"
        >
          上一张
        </button>
        <span class="frame-info">
          {{ currentIndex + 1 }} / {{ imageUrls.length }}  
        </span>
        <button 
          @click="nextImage" 
          :disabled="currentIndex === imageUrls.length - 1" 
          class="nav-btn"
        >
          下一张
        </button>
      </div>
    </div> <!-- 闭合 image-viewer -->
  </div> <!-- 补充：闭合最外层的 app 容器 -->
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const message = ref('');
const reply = ref('');
// 注意：原代码中 imageUrls 初始值是 ''（字符串），但后端返回的是数组，需改为数组！
const imageUrls = ref([]);  // 修正：初始化为空数组，避免 length 判断错误
const loadStatus = ref('');  // 加载状态文本提示
const updateTime = ref(Date.now());
const currentIndex = ref(0);
// 新增：加载中锁（true = 正在处理，禁用输入/按钮）
const isProcessing = ref(false);

// 上一张
const prevImage = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

// 下一张
const nextImage = () => {
  if (currentIndex.value < imageUrls.value.length - 1) {
    currentIndex.value++;
  }
};


// 关键：使用相对路径调用 API（无需指定域名和端口）
const sendMessage = async () => {
   // 1. 空输入拦截
  if (!message.value.trim()) return;
  
  // 2. 加载中拦截（防止重复点击）
  if (isProcessing.value) return;

  try {
    // 3. 开始处理：开启加载中状态
    isProcessing.value = true;  // 禁用输入/按钮
    loadStatus.value = "正在生成新场景图...";  // 显示提示文本
    
    // 4. 发起请求（原有逻辑不变）
    const response = await axios.post('/api/chat', { content: message.value });
    reply.value = response.data.reply;
    imageUrls.value = response.data.image_urls;  // 后端返回数组，对应修正后的 imageUrls
    currentIndex.value = 0;  // 重置图片索引到第一张
    updateTime.value = Date.now();
    message.value = '';

  } catch (error) {
    // （原有错误处理逻辑不变）
    let errorMsg = '更新图片失败';
    if (error.response) {
      errorMsg = error.response.data.detail || `服务器错误：${error.response.status}`;
    } else if (error.request) {
      errorMsg = `网络错误：${error.message}`;
    } else {
      errorMsg = `未知错误：${error.message}`;
    }
    reply.value = errorMsg;
    imageUrls.value = [];  // 错误时清空图片数组

  } finally {
    // 5. 无论成功/失败，结束加载中状态
    isProcessing.value = false;  // 恢复输入/按钮可用
    loadStatus.value = '';  // 清除提示文本
  }
};

// // 可选：图片加载完成提示
// const handleImageLoad = () => {
//   loadStatus.value = "图片更新完成！";
//   setTimeout(() => loadStatus.value = '', 1500);  // 1.5秒后清除提示
// };

// const handleImageError = (e) => {
//   e.target.src = "https://via.placeholder.com/400x200?text=图片更新失败";
// };

</script>

<style scoped>
/* 1. 扩大 chat-box 容器 */
.chat-box {
  /* 宽度：占父容器 90%（适配不同屏幕），最大宽度限制为 800px（避免过宽） */
  width: 90%;
  max-width: 800px;
  /* 最小高度：300px（确保有足够空间，内容多了会自动撑开） */
  min-height: 300px;
  /* 内边距：增加内部空间，避免元素贴边 */
  padding: 20px;
  /* 边框和背景：可选，让 chatbox 更明显 */
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
  /* 布局：让输入框和按钮横向排列，回复区域纵向在下 */
  display: flex;
  flex-direction: column;
  gap: 15px; /* 元素之间的间距 */
  /* 居中：让 chatbox 在页面中居中（可选） */
  margin: 0 auto;
}

/* 2. 优化输入框样式（随 chat-box 宽度适配） */
.chat-input {
  /* 宽度：占满 chat-box 横向空间 */
  width: 100%;
  /* 高度：50px（比默认更高，输入更舒适） */
  height: 50px;
  /* 内边距：左右 15px，避免文字贴边 */
  padding: 0 15px;
  /* 字体大小：16px（更清晰） */
  font-size: 16px;
  /* 边框：优化样式 */
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box; /* 确保 padding 不撑大宽度 */
}

/* 3. 优化按钮样式（与输入框适配） */
.chat-btn {
  /* 宽度：不占满，适中即可 */
  width: 120px;
  /* 高度：与输入框一致（50px），视觉统一 */
  height: 50px;
  /* 字体大小：16px */
  font-size: 16px;
  /* 颜色：突出按钮 */
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-group {
  display: flex;
  align-items: center;
  gap: 12px;  /* 按钮和提示的间距 */
}

/* 新增：加载中提示文本样式（浅灰色，小字体） */
.loading-text {
  color: #666;  /* 浅灰色，不刺眼 */
  font-size: 14px;
  height: 50px;  /* 与按钮高度一致，垂直居中 */
  line-height: 50px;  /* 垂直居中 */
}

/* 优化：禁用状态的输入框和按钮样式（更明显的不可用状态） */
.chat-input:disabled {
  background-color: #f5f5f5;  /* 浅灰背景 */
  color: #999;  /* 灰色文本 */
  cursor: not-allowed;  /* 禁止光标 */
  border-color: #ddd;
}

.chat-btn:disabled {
  background-color: #ccc;  /* 灰色按钮 */
  cursor: not-allowed;
}
/* 4. 优化回复区域（随 chat-box 宽度适配） */
.reply-container {
  /* 宽度：占满 chat-box */
  width: 100%;
  box-sizing: border-box;
  /* 最小高度：100px（确保回复内容有足够空间） */
  min-height: 100px;
  /* 内边距：15px */
  padding: 15px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #eee;
}

.seq-frame {
  max-width: 500px;  /* 限制图片最大宽度 */
  border: 1px solid #eee;
  margin: 10px 0;
}

.navigation-buttons {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 15px;  /* 按钮和文字之间的间距 */
}

.nav-btn {
  padding: 6px 12px;
  cursor: pointer;
  background: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
}

.nav-btn:disabled {
  background: #ccc;
  cursor: not-allowed;  /* 禁用状态的鼠标样式 */
}

.frame-info {
  color: #666;
}
</style>