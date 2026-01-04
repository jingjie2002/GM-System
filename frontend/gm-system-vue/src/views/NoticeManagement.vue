<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import request from '@/utils/request'

// --- 1. 数据定义 ---
const loading = ref(false)
const showModal = ref(false)   // 编辑/新建弹窗
const isEditMode = ref(false)  // true=编辑, false=新建
const submitting = ref(false)

const noticeList = ref([])
const currentId = ref(null)

// 统计卡片
const statsCards = ref([
  { label: '公告总数', value: '0', sub: '累计发布', icon: 'ph-article', color: 'text-blue-400', bg: 'bg-blue-500/10' },
  { label: '正在生效', value: '0', sub: '玩家可见', icon: 'ph-broadcast', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  { label: '草稿箱', value: '0', sub: '待发布', icon: 'ph-file-dashed', color: 'text-orange-400', bg: 'bg-orange-500/10' },
])

// 表单数据
const form = reactive({
  title: '',
  content: '',
  notice_type: 'login',
  priority: 0,
  status: 'draft',
  start_time: '',
  end_time: ''
})

// --- 2. 辅助函数：状态判断 ---
const getNoticeStatus = (notice) => {
  const now = new Date()
  const start = new Date(notice.start_time)
  const end = new Date(notice.end_time)

  if (notice.status === 'draft') return { text: '草稿', class: 'text-orange-400 bg-orange-500/10 border-orange-500/20' }
  if (now < start) return { text: '未开始', class: 'text-blue-400 bg-blue-500/10 border-blue-500/20' }
  if (now > end) return { text: '已过期', class: 'text-white/40 bg-white/5 border-white/10' }
  return { text: '生效中', class: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20 animate-pulse' }
}

// 格式化 datetime-local 需要的字符串 (YYYY-MM-DDTHH:mm)
const formatForInput = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  // 处理时区偏移，转为本地时间格式字符串
  const offset = date.getTimezoneOffset() * 60000
  const localIso = new Date(date.getTime() - offset).toISOString().slice(0, 16)
  return localIso
}

// --- 3. 核心逻辑 ---
const fetchData = async () => {
  loading.value = true
  try {
    const res = await request.get('/notices/')
    const rawList = Array.isArray(res.data) ? res.data : (res.data?.results || [])

    // 客户端排序：优先级高在前 -> 创建时间晚在前
    noticeList.value = rawList.sort((a, b) => {
      if (b.priority !== a.priority) return b.priority - a.priority
      return new Date(b.created_at) - new Date(a.created_at)
    })

    // 更新统计
    const now = new Date()
    statsCards.value[0].value = rawList.length.toLocaleString()
    statsCards.value[1].value = rawList.filter(n =>
      n.status === 'published' && new Date(n.start_time) <= now && new Date(n.end_time) >= now
    ).length.toLocaleString()
    statsCards.value[2].value = rawList.filter(n => n.status === 'draft').length.toLocaleString()

  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

// 打开新建
const openCreate = () => {
  isEditMode.value = false
  currentId.value = null
  // 设置默认值
  const now = new Date()
  const nextMonth = new Date()
  nextMonth.setDate(now.getDate() + 30)

  form.title = ''
  form.content = ''
  form.notice_type = 'login'
  form.priority = 0
  form.status = 'published' // 默认选中已发布方便操作
  form.start_time = formatForInput(now)      // 默认现在开始
  form.end_time = formatForInput(nextMonth)  // 默认一个月后结束

  showModal.value = true
}

// 打开编辑
const openEdit = (notice) => {
  isEditMode.value = true
  currentId.value = notice.id

  form.title = notice.title
  form.content = notice.content
  form.notice_type = notice.notice_type
  form.priority = notice.priority
  form.status = notice.status
  form.start_time = formatForInput(notice.start_time)
  form.end_time = formatForInput(notice.end_time)

  showModal.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!form.title || !form.content || !form.start_time || !form.end_time) {
    alert('请补全必填信息')
    return
  }

  submitting.value = true
  try {
    const payload = { ...form }
    // 注意：datetime-local 的值包含 'T'，DRF 能够识别，直接传即可

    if (isEditMode.value) {
      await request.put(`/notices/${currentId.value}/`, payload)
      alert('修改成功')
    } else {
      await request.post('/notices/', payload)
      alert('发布成功')
    }
    showModal.value = false
    fetchData()
  } catch (error) {
    console.error('提交失败', error)
    alert('操作失败，请检查输入')
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = async (id) => {
  if (!confirm('确定要删除这条公告吗？此操作不可恢复。')) return
  try {
    await request.delete(`/notices/${id}/`)
    alert('删除成功')
    fetchData()
  } catch (error) {
    alert('删除失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="flex flex-col gap-6 h-full pb-4 relative overflow-y-auto custom-scrollbar pr-2">

    <div class="grid grid-cols-3 gap-6 shrink-0 h-[120px]">
      <div v-for="(item, index) in statsCards" :key="index"
           class="relative rounded-[24px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-5 flex flex-col justify-center overflow-hidden group hover:bg-white/[0.05] transition-all duration-500">
        <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full blur-[40px] opacity-20 transition-all duration-500 group-hover:scale-150"
             :class="item.color.replace('text-', 'bg-')"></div>
        <div class="flex justify-between items-center relative z-10">
          <div>
            <p class="text-blue-200/50 text-xs font-bold mb-1 tracking-wider uppercase">{{ item.label }}</p>
            <div class="flex items-end gap-3">
              <h3 class="text-3xl font-bold text-white tracking-tight">{{ item.value }}</h3>
              <span class="text-[10px] text-white/40 mb-1.5 font-medium border border-white/10 px-1.5 rounded bg-white/5">{{ item.sub }}</span>
            </div>
          </div>
          <div class="w-12 h-12 rounded-[18px] flex items-center justify-center shadow-inner border border-white/5" :class="item.bg">
            <i class="ph-fill text-2xl" :class="[item.color, item.icon]"></i>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-[30px] border border-white/8 bg-white/2 backdrop-blur-2xl shadow-xl overflow-hidden relative shrink-0">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent blur-sm"></div>

      <div class="px-6 py-5 border-b border-white/5 flex justify-between items-center shrink-0">
        <div>
          <h6 class="text-base font-bold text-white tracking-wide flex items-center gap-2">
            <i class="ph-duotone ph-megaphone text-blue-400"></i> 公告管理列表
            <span class="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/40 font-mono">共 {{ noticeList.length }} 条记录</span>
          </h6>
          <p class="text-[10px] text-blue-200/40 mt-0.5">管理游戏内的登录弹窗、跑马灯与系统通知</p>
        </div>
        <div class="flex gap-3">
          <button @click="fetchData" class="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-bold text-white/60 hover:bg-white/10 hover:text-white transition-all flex items-center gap-2">
            <i class="ph-bold ph-arrows-clockwise"></i> 刷新
          </button>
          <button @click="openCreate" class="px-4 py-2 rounded-xl bg-blue-600 border border-blue-400/30 text-xs font-bold text-white shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:bg-blue-500 hover:scale-105 transition-all flex items-center gap-2">
            <i class="ph-bold ph-plus"></i> 发布公告
          </button>
        </div>
      </div>

      <div class="p-3">
        <div v-if="loading" class="flex items-center justify-center py-20 text-white/20 text-sm">
          <i class="ph-bold ph-spinner animate-spin mr-2"></i> 加载数据中...
        </div>
        <div v-else-if="noticeList.length === 0" class="flex flex-col items-center justify-center py-20 text-white/20">
          <i class="ph-duotone ph-article text-4xl mb-2"></i>
          <span class="text-xs">暂无公告数据</span>
        </div>
        <table v-else class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-[#131b35]/90 backdrop-blur-md z-10 rounded-xl">
            <tr class="text-blue-200/40 text-[10px] uppercase tracking-wider">
              <th class="py-3 pl-4 font-semibold rounded-l-xl">公告标题</th>
              <th class="py-3 font-semibold">类型</th>
              <th class="py-3 font-semibold">优先级</th>
              <th class="py-3 font-semibold">状态 / 有效期</th>
              <th class="py-3 text-right pr-4 font-semibold rounded-r-xl">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="notice in noticeList" :key="notice.id"
                class="group hover:bg-white/3 border-white/2 last:border-0 rounded-xl">

              <td class="py-4 pl-4 max-w-[200px]">
                <div class="font-bold text-white text-xs truncate">{{ notice.title }}</div>
                <div class="text-[10px] text-white/30 truncate mt-0.5">{{ notice.content }}</div>
              </td>

              <td class="py-4">
                <span class="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-bold border border-white/5 bg-white/5 text-blue-200">
                  <i v-if="notice.notice_type === 'login'" class="ph-fill ph-sign-in text-blue-400"></i>
                  <i v-else-if="notice.notice_type === 'marquee'" class="ph-fill ph-text-aa text-orange-400"></i>
                  <i v-else class="ph-fill ph-envelope text-purple-400"></i>
                  {{ notice.notice_type === 'login' ? '登录弹窗' : (notice.notice_type === 'marquee' ? '跑马灯' : '系统通知') }}
                </span>
              </td>

              <td class="py-4">
                 <div class="font-mono text-white/60 text-xs">#{{ notice.priority }}</div>
              </td>

              <td class="py-4">
                <div class="flex flex-col items-start gap-1">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold border"
                        :class="getNoticeStatus(notice).class">
                    {{ getNoticeStatus(notice).text }}
                  </span>
                  <span class="text-[10px] text-white/20 font-mono">
                    {{ new Date(notice.start_time).toLocaleDateString() }} - {{ new Date(notice.end_time).toLocaleDateString() }}
                  </span>
                </div>
              </td>

              <td class="py-4 text-right pr-4">
                <div class="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="openEdit(notice)" class="w-7 h-7 rounded-lg bg-blue-500/10 hover:bg-blue-500 text-blue-400 hover:text-white flex items-center justify-center transition-all">
                    <i class="ph-bold ph-pencil-simple"></i>
                  </button>
                  <button @click="handleDelete(notice.id)" class="w-7 h-7 rounded-lg bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-white flex items-center justify-center transition-all">
                    <i class="ph-bold ph-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="showModal = false"></div>
        <div class="relative w-full max-w-lg bg-[#1a2342] border border-white/10 rounded-[24px] shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div class="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                    <i class="ph-duotone ph-pencil-simple text-blue-400"></i> {{ isEditMode ? '编辑公告' : '发布新公告' }}
                </h3>
                <button @click="showModal = false" class="text-white/40 hover:text-white transition-colors"><i class="ph-bold ph-x text-lg"></i></button>
            </div>

            <div class="p-6 space-y-4 overflow-y-auto max-h-[70vh] custom-scrollbar">

                <div>
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">公告标题</label>
                    <input v-model="form.title" type="text" placeholder="输入公告标题..."
                           class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 focus:bg-white/10 outline-none transition-all placeholder:text-white/20">
                </div>

                <div class="grid grid-cols-3 gap-3">
                   <div v-for="type in ['login', 'marquee', 'system']" :key="type"
                        @click="form.notice_type = type"
                        class="p-3 rounded-xl border cursor-pointer transition-all flex flex-col items-center gap-1"
                        :class="form.notice_type === type ? 'bg-blue-600/20 border-blue-500' : 'bg-white/5 border-white/10 hover:bg-white/10'">
                        <i class="ph-fill text-lg"
                           :class="{'ph-sign-in': type === 'login', 'ph-text-aa': type === 'marquee', 'ph-envelope': type === 'system', 'text-blue-400': form.notice_type === type, 'text-white/40': form.notice_type !== type}"></i>
                        <span class="text-xs font-bold" :class="form.notice_type === type ? 'text-white' : 'text-white/40'">
                            {{ type === 'login' ? '登录公告' : (type === 'marquee' ? '跑马灯' : '系统通知') }}
                        </span>
                   </div>
                </div>

                <div>
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">公告内容</label>
                    <textarea v-model="form.content" rows="4" placeholder="支持纯文本内容..."
                              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 focus:bg-white/10 outline-none transition-all placeholder:text-white/20 resize-none"></textarea>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">优先级 (越大越靠前)</label>
                        <input v-model.number="form.priority" type="number"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 outline-none font-mono">
                    </div>
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">状态</label>
                        <select v-model="form.status" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 outline-none appearance-none">
                            <option value="published" class="text-black">✅ 直接发布</option>
                            <option value="draft" class="text-black">📝 存为草稿</option>
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">生效时间</label>
                        <input v-model="form.start_time" type="datetime-local"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 outline-none font-mono [color-scheme:dark]">
                    </div>
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">失效时间</label>
                        <input v-model="form.end_time" type="datetime-local"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 outline-none font-mono [color-scheme:dark]">
                    </div>
                </div>
            </div>

            <div class="p-6 pt-2 flex gap-3">
                <button @click="showModal = false" class="flex-1 py-3 rounded-xl border border-white/10 text-white/60 text-sm font-bold hover:bg-white/5 transition-colors">取消</button>
                <button @click="handleSubmit" :disabled="submitting"
                        class="flex-1 py-3 rounded-xl bg-blue-600 border border-blue-400/30 text-white text-sm font-bold shadow-lg shadow-blue-500/20 hover:bg-blue-500 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-2">
                    <i v-if="submitting" class="ph-bold ph-spinner animate-spin"></i>
                    {{ submitting ? '处理中...' : (isEditMode ? '保存修改' : '确认发布') }}
                </button>
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
/* 弹窗动画 */
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes zoom-in-95 { from { transform: scale(0.95); } to { transform: scale(1); } }
.animate-in { animation-duration: 0.2s; animation-fill-mode: both; }
.fade-in { animation-name: fade-in; }
.zoom-in-95 { animation-name: zoom-in-95; }
</style>
