<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'

// --- 1. 数据定义 ---
const loading = ref(false)
const drawerOpen = ref(false)   // 详情抽屉
const composeOpen = ref(false)  // 写信弹窗
const submitting = ref(false)   // 发送中状态
const currentMail = ref(null)

// 统计数据
const statsCards = ref([
  { label: '邮件总数', value: '0', sub: '历史发送', icon: 'ph-envelope-simple-open', color: 'text-orange-400', bg: 'bg-orange-500/10' },
  { label: '全服邮件', value: '0', sub: '广播通知', icon: 'ph-broadcast', color: 'text-blue-400', bg: 'bg-blue-500/10' },
  { label: '已领取', value: '0', sub: '道具发放', icon: 'ph-check-circle', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
])

const mailList = ref([])

// 写信表单数据
const form = reactive({
  title: '',
  content: '',
  is_global: false,
  receiver: '',       // 玩家ID
  item_id: 1,         // 默认金币
  item_count: 0,
  valid_days: 30      // 有效期天数
})

// --- 2. 获取数据 ---
const fetchData = async () => {
  loading.value = true
  try {
    const res = await request.get('/mails/')
    const rawList = Array.isArray(res.data) ? res.data : (res.data?.results || [])

    // 更新统计
    const totalCount = res.data?.count || rawList.length
    statsCards.value[0].value = totalCount.toLocaleString()
    statsCards.value[1].value = rawList.filter(m => m.is_global).length.toLocaleString()
    statsCards.value[2].value = rawList.filter(m => m.is_claimed).length.toLocaleString()

    // 映射列表
    mailList.value = rawList.map(item => ({
      id: item.id,
      title: item.title,
      sender: item.is_global ? '全服广播' : (item.sender_name || '系统'),
      type: item.is_global ? 'system' : 'private',
      status: item.is_claimed ? 'read' : 'sent',
      content: item.content,
      time: new Date(item.created_at).toLocaleString(),
      receiver: item.receiver_name || '全体玩家',
      raw_expires: item.expires_at
    }))
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
}

// --- 3. 发送邮件逻辑 ---
const submitMail = async () => {
  // 简单的表单验证
  if (!form.title || !form.content) {
    alert('请填写标题和内容')
    return
  }
  if (!form.is_global && !form.receiver) {
    alert('非全服邮件必须填写玩家ID')
    return
  }

  submitting.value = true
  try {
    // 1. 计算过期时间 (当前时间 + 天数)
    const expiresAt = new Date()
    expiresAt.setDate(expiresAt.getDate() + parseInt(form.valid_days))

    // 2. 构造 payload
    const payload = {
      title: form.title,
      content: form.content,
      is_global: form.is_global,
      item_id: form.item_count > 0 ? form.item_id : null,
      item_count: form.item_count > 0 ? form.item_count : 0,
      expires_at: expiresAt.toISOString(), // 转为 ISO 格式发给后端
      receiver: form.is_global ? null : form.receiver // 全服邮件不需要接收者
    }

    // 3. 发送请求
    await request.post('/mails/', payload)

    // 4. 成功处理
    alert('邮件发送成功！')
    composeOpen.value = false
    resetForm()
    fetchData() // 刷新列表

  } catch (error) {
    console.error('发送失败:', error)
    // 提取后端错误信息
    const msg = error.response?.data?.message || '发送失败，请检查填写信息'
    alert(msg)
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  form.title = ''
  form.content = ''
  form.is_global = false
  form.receiver = ''
  form.item_count = 0
  form.valid_days = 30
}

// --- 4. 界面操作 ---
const openDetail = (mail) => {
  currentMail.value = mail
  drawerOpen.value = true
}

const closeDrawer = () => {
  drawerOpen.value = false
  setTimeout(() => { currentMail.value = null }, 300)
}

const getStatusStyle = (status) => {
  const map = {
    unread: 'bg-orange-500/10 border-orange-500/20 text-orange-400',
    read: 'bg-white/5 border-white/10 text-white/40',
    sent: 'bg-blue-500/10 border-blue-500/20 text-blue-400',
    draft: 'bg-white/10 border-white/20 text-white/60'
  }
  return map[status] || map.read
}

const getStatusText = (status) => {
  // 修改点：sent 改为 '未领取'
  const map = { unread: '待处理', read: '已领取', sent: '未领取', draft: '草稿' }
  return map[status]
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
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-purple-500/50 to-transparent blur-sm"></div>

      <div class="px-6 py-5 border-b border-white/5 flex justify-between items-center shrink-0">
        <div>
          <h6 class="text-base font-bold text-white tracking-wide flex items-center gap-2">
            <i class="ph-duotone ph-envelope text-purple-400"></i> 邮件管理列表
            <span class="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/40 font-mono">共 {{ mailList.length }} 条记录</span>
          </h6>
          <p class="text-[10px] text-blue-200/40 mt-0.5">查看已发送的系统邮件与全服广播</p>
        </div>
        <div class="flex gap-3">
          <button @click="fetchData" class="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-bold text-white/60 hover:bg-white/10 hover:text-white transition-all flex items-center gap-2">
            <i class="ph-bold ph-arrows-clockwise"></i> 刷新
          </button>
          <button @click="composeOpen = true" class="px-4 py-2 rounded-xl bg-blue-600 border border-blue-400/30 text-xs font-bold text-white shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:bg-blue-500 hover:scale-105 transition-all flex items-center gap-2">
            <i class="ph-bold ph-pencil-simple"></i> 发送新邮件
          </button>
        </div>
      </div>

      <div class="p-3">
        <div v-if="loading" class="flex items-center justify-center py-20 text-white/20 text-sm">
          <i class="ph-bold ph-spinner animate-spin mr-2"></i> 加载数据中...
        </div>
        <div v-else-if="mailList.length === 0" class="flex flex-col items-center justify-center py-20 text-white/20">
          <i class="ph-duotone ph-inbox text-4xl mb-2"></i>
          <span class="text-xs">暂无邮件记录</span>
        </div>
        <table v-else class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-[#131b35]/90 backdrop-blur-md z-10 rounded-xl">
            <tr class="text-blue-200/40 text-[10px] uppercase tracking-wider">
              <th class="py-3 pl-4 font-semibold rounded-l-xl">邮件标题</th>
              <th class="py-3 font-semibold">类型 / 接收者</th>
              <th class="py-3 font-semibold">状态</th>
              <th class="py-3 text-right pr-4 font-semibold rounded-r-xl">创建时间</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="mail in mailList" :key="mail.id" @click="openDetail(mail)"
                class="group hover:bg-white/3 border-white/2 last:border-0 rounded-xl cursor-pointer">
              <td class="py-4 pl-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-lg shrink-0"
                       :class="mail.type === 'system' ? 'bg-gradient-to-br from-blue-500 to-indigo-600' : 'bg-gradient-to-br from-purple-500 to-pink-600'">
                    <i class="ph-fill" :class="mail.type === 'system' ? 'ph-broadcast' : 'ph-user'"></i>
                  </div>
                  <div class="min-w-0">
                    <div class="font-bold text-white text-xs group-hover:text-purple-400 transition-colors truncate max-w-[200px]">{{ mail.title }}</div>
                    <div class="text-[10px] text-white/30 font-mono mt-0.5 truncate">{{ mail.content }}</div>
                  </div>
                </div>
              </td>
              <td class="py-4">
                 <div class="flex flex-col">
                   <span class="text-xs font-medium text-white/80">{{ mail.type === 'system' ? '全服邮件' : '私人邮件' }}</span>
                   <span class="text-[10px] text-blue-200/40">To: {{ mail.receiver }}</span>
                 </div>
              </td>
              <td class="py-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold border" :class="getStatusStyle(mail.status)">{{ getStatusText(mail.status) }}</span>
              </td>
              <td class="py-4 text-right pr-4 text-white/40 text-xs font-mono">{{ mail.time }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="composeOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="composeOpen = false"></div>

        <div class="relative w-full max-w-lg bg-[#1a2342] border border-white/10 rounded-[24px] shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div class="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                    <i class="ph-duotone ph-pencil-simple text-blue-400"></i> 发送新邮件
                </h3>
                <button @click="composeOpen = false" class="text-white/40 hover:text-white transition-colors">
                    <i class="ph-bold ph-x text-lg"></i>
                </button>
            </div>

            <div class="p-6 space-y-4 overflow-y-auto max-h-[70vh] custom-scrollbar">

                <div>
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">邮件标题</label>
                    <input v-model="form.title" type="text" placeholder="输入邮件标题..."
                           class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 focus:bg-white/10 outline-none transition-all placeholder:text-white/20">
                </div>

                <div class="flex gap-4">
                    <div class="flex-1 p-3 rounded-xl border cursor-pointer transition-all"
                         :class="form.is_global ? 'bg-blue-600/20 border-blue-500' : 'bg-white/5 border-white/10 hover:bg-white/10'"
                         @click="form.is_global = true">
                        <div class="flex items-center gap-2 mb-1">
                            <i class="ph-fill ph-broadcast text-blue-400"></i>
                            <span class="text-sm font-bold text-white">全服广播</span>
                        </div>
                        <p class="text-[10px] text-white/40">发送给所有玩家</p>
                    </div>
                    <div class="flex-1 p-3 rounded-xl border cursor-pointer transition-all"
                         :class="!form.is_global ? 'bg-purple-600/20 border-purple-500' : 'bg-white/5 border-white/10 hover:bg-white/10'"
                         @click="form.is_global = false">
                        <div class="flex items-center gap-2 mb-1">
                            <i class="ph-fill ph-user text-purple-400"></i>
                            <span class="text-sm font-bold text-white">私人邮件</span>
                        </div>
                        <p class="text-[10px] text-white/40">发送给指定玩家</p>
                    </div>
                </div>

                <div v-if="!form.is_global">
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">接收玩家 ID</label>
                    <input v-model="form.receiver" type="number" placeholder="输入玩家数字 ID (如: 1001)..."
                           class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-purple-500 focus:bg-white/10 outline-none transition-all placeholder:text-white/20 font-mono">
                </div>

                <div>
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">邮件正文</label>
                    <textarea v-model="form.content" rows="4" placeholder="输入邮件内容..."
                              class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 focus:bg-white/10 outline-none transition-all placeholder:text-white/20 resize-none"></textarea>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">附件物品</label>
                        <select v-model="form.item_id" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 outline-none appearance-none">
                            <option value="1" class="text-black">💰 金币</option>
                            <option value="2" class="text-black">💎 钻石</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">数量</label>
                        <input v-model.number="form.item_count" type="number" min="0"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 focus:bg-white/10 outline-none transition-all font-mono">
                    </div>
                </div>

                <div>
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">有效期 (天)</label>
                    <input v-model.number="form.valid_days" type="number" min="1"
                           class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-blue-500 focus:bg-white/10 outline-none transition-all font-mono">
                </div>
            </div>

            <div class="p-6 pt-2 flex gap-3">
                <button @click="composeOpen = false" class="flex-1 py-3 rounded-xl border border-white/10 text-white/60 text-sm font-bold hover:bg-white/5 transition-colors">
                    取消
                </button>
                <button @click="submitMail" :disabled="submitting"
                        class="flex-1 py-3 rounded-xl bg-blue-600 border border-blue-400/30 text-white text-sm font-bold shadow-lg shadow-blue-500/20 hover:bg-blue-500 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                    <i v-if="submitting" class="ph-bold ph-spinner animate-spin"></i>
                    {{ submitting ? '发送中...' : '确认发送' }}
                </button>
            </div>
        </div>
    </div>

    <div class="absolute inset-0 z-40 pointer-events-none overflow-hidden">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300 pointer-events-auto"
             v-if="drawerOpen" @click="closeDrawer"></div>
        <div class="absolute top-2 bottom-2 right-2 w-[500px] bg-[#1a2342]/90 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-2xl transform transition-transform duration-300 pointer-events-auto flex flex-col"
             :class="drawerOpen ? 'translate-x-0' : 'translate-x-[110%]'">
            <div v-if="currentMail" class="flex-1 flex flex-col h-full">
                <div class="p-6 border-b border-white/10 flex justify-between items-start">
                    <div>
                        <div class="flex items-center gap-2 mb-2">
                             <span class="px-2 py-0.5 rounded text-[10px] font-bold border" :class="getStatusStyle(currentMail.status)">
                                {{ getStatusText(currentMail.status) }}
                             </span>
                             <span class="text-[10px] text-white/40 font-mono">{{ currentMail.time }}</span>
                        </div>
                        <h2 class="text-xl font-bold text-white leading-tight">{{ currentMail.title }}</h2>
                    </div>
                    <button @click="closeDrawer" class="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/60 hover:text-white transition-colors">
                        <i class="ph-bold ph-x"></i>
                    </button>
                </div>
                <div class="flex-1 p-6 overflow-y-auto">
                    <div class="flex items-center gap-3 mb-6 p-4 rounded-xl bg-white/[0.03] border border-white/[0.05]">
                         <div class="w-10 h-10 rounded-full bg-gradient-to-br from-white/10 to-transparent border border-white/10 flex items-center justify-center">
                            <i class="ph-duotone ph-paper-plane-right text-lg text-blue-300"></i>
                         </div>
                         <div>
                             <div class="text-xs text-blue-200/50 uppercase tracking-wider">接收者</div>
                             <div class="text-sm font-bold text-white">{{ currentMail.receiver }}</div>
                         </div>
                    </div>
                    <div class="text-sm text-blue-100/80 leading-relaxed whitespace-pre-wrap">{{ currentMail.content }}</div>
                </div>
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
