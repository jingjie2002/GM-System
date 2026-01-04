<script setup>
import { ref, reactive, onMounted } from 'vue'
import request from '@/utils/request'

// --- 1. 数据定义 ---
const loading = ref(false)
const showGenerateModal = ref(false)
const submitting = ref(false)
const cdkList = ref([])

// 统计卡片 (复用仪表盘风格)
const statsCards = ref([
  { label: '库存总量', value: '0', sub: '所有CDK', icon: 'ph-ticket', color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { label: '已兑换', value: '0', sub: '累计使用', icon: 'ph-check-circle', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  { label: '通用码', value: '0', sub: '多人可用', icon: 'ph-users-three', color: 'text-blue-400', bg: 'bg-blue-500/10' },
])

// 生成表单
const form = reactive({
  count: 10,
  item_id: 1,
  item_count: 1000,
  max_uses: 1,
  days: 30
})

// --- 2. 核心逻辑 ---
const fetchData = async () => {
  loading.value = true
  try {
    const res = await request.get('/cdks/')
    // 兼容 DRF 分页
    const rawList = res.data?.results || res.data || []
    cdkList.value = rawList

    // 更新统计
    const total = res.data?.count || rawList.length
    const used = rawList.reduce((acc, cur) => acc + cur.used_count, 0)
    const multi = rawList.filter(c => c.max_uses > 1).length

    statsCards.value[0].value = total.toLocaleString()
    statsCards.value[1].value = used.toLocaleString()
    statsCards.value[2].value = multi.toLocaleString()

  } catch (error) {
    console.error('加载失败', error)
  } finally {
    loading.value = false
  }
}

// 提交生成
const handleGenerate = async () => {
  submitting.value = true
  try {
    await request.post('/cdks/generate/', form)
    alert('✅ 批量生成成功！')
    showGenerateModal.value = false
    fetchData()
  } catch (error) {
    const msg = error.response?.data?.error || '生成失败'
    alert(`❌ ${msg}`)
  } finally {
    submitting.value = false
  }
}

// 删除
const handleDelete = async (id) => {
  if (!confirm('确定要删除这个兑换码吗？')) return
  try {
    await request.delete(`/cdks/${id}/`)
    fetchData() // 刷新列表
  } catch (error) {
    alert('删除失败')
  }
}

// 复制到剪贴板
const copyCode = async (code) => {
  try {
    await navigator.clipboard.writeText(code)
    alert('已复制: ' + code)
  } catch (err) {
    console.error('复制失败', err)
  }
}

// 状态样式辅助函数
const getStatusClass = (cdk) => {
  const now = new Date()
  const expire = new Date(cdk.expires_at)

  if (cdk.remaining_uses <= 0) return 'bg-white/5 text-white/30 border-white/10' // 耗尽
  if (now > expire) return 'bg-red-500/10 text-red-400 border-red-500/20'       // 过期
  return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'             // 正常
}

const getStatusText = (cdk) => {
  const now = new Date()
  if (cdk.remaining_uses <= 0) return '已耗尽'
  if (now > new Date(cdk.expires_at)) return '已过期'
  return '生效中'
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="flex flex-col gap-6 h-full pb-4 relative overflow-y-auto custom-scrollbar pr-2">

    <!-- 统计卡片 -->
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

    <!-- 主内容卡片 -->
    <div class="rounded-[30px] border border-white/8 bg-white/2 backdrop-blur-2xl shadow-xl overflow-hidden relative shrink-0">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-purple-500/50 to-transparent blur-sm"></div>

      <!-- 头部 -->
      <div class="px-6 py-5 border-b border-white/5 flex justify-between items-center shrink-0">
        <div>
          <h6 class="text-base font-bold text-white tracking-wide flex items-center gap-2">
            <i class="ph-duotone ph-ticket text-purple-400"></i> 礼包码管理
            <span class="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/40 font-mono">共 {{ cdkList.length }} 条记录</span>
          </h6>
          <p class="text-[10px] text-blue-200/40 mt-0.5">批量生成与管理 CDK 兑换码</p>
        </div>
        <div class="flex gap-3">
          <button @click="fetchData" class="px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-bold text-white/60 hover:bg-white/10 hover:text-white transition-all flex items-center gap-2">
            <i class="ph-bold ph-arrows-clockwise"></i> 刷新
          </button>
          <button @click="showGenerateModal = true" class="px-4 py-2 rounded-xl bg-purple-600 border border-purple-400/30 text-xs font-bold text-white shadow-[0_0_20px_rgba(147,51,234,0.3)] hover:bg-purple-500 hover:scale-105 transition-all flex items-center gap-2">
            <i class="ph-bold ph-magic-wand"></i> 批量生成
          </button>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="p-3">
        <!-- 加载状态 -->
        <div v-if="loading" class="flex items-center justify-center py-20 text-white/20 text-sm">
          <i class="ph-bold ph-spinner animate-spin mr-2"></i> 加载数据中...
        </div>

        <!-- 空状态 -->
        <div v-else-if="cdkList.length === 0" class="flex flex-col items-center justify-center py-20 text-white/20">
          <i class="ph-duotone ph-ticket text-4xl mb-2"></i>
          <span class="text-xs">暂无兑换码</span>
        </div>

        <!-- 表格 -->
        <table v-else class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-[#131b35]/90 backdrop-blur-md z-10 rounded-xl">
            <tr class="text-blue-200/40 text-[10px] uppercase tracking-wider">
              <th class="py-3 pl-4 font-semibold rounded-l-xl">兑换码</th>
              <th class="py-3 font-semibold">奖励内容</th>
              <th class="py-3 font-semibold">使用进度</th>
              <th class="py-3 font-semibold">状态</th>
              <th class="py-3 text-right pr-4 font-semibold rounded-r-xl">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="cdk in cdkList" :key="cdk.id"
                class="group hover:bg-white/3 border-white/2 last:border-0 rounded-xl">

              <td class="py-4 pl-4">
                <div @click="copyCode(cdk.code)"
                     class="font-mono font-bold text-white text-xs cursor-pointer hover:text-purple-400 transition-colors flex items-center gap-2 w-fit group/code">
                  {{ cdk.code }}
                  <i class="ph-bold ph-copy text-[10px] opacity-0 group-hover/code:opacity-100 transition-opacity"></i>
                </div>
                <div class="text-[10px] text-white/30 mt-0.5">过期: {{ new Date(cdk.expires_at).toLocaleDateString() }}</div>
              </td>

              <td class="py-4">
                <div class="flex items-center gap-2">
                   <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs border border-white/10"
                        :class="cdk.item_id === 1 ? 'bg-yellow-500/20 text-yellow-400' : 'bg-cyan-500/20 text-cyan-400'">
                      <i class="ph-fill" :class="cdk.item_id === 1 ? 'ph-coins' : 'ph-diamond'"></i>
                   </div>
                   <span class="text-xs font-bold text-white/80">
                     {{ cdk.item_id === 1 ? '金币' : '钻石' }} x{{ cdk.item_count.toLocaleString() }}
                   </span>
                </div>
              </td>

              <td class="py-4">
                 <div class="flex items-center gap-2">
                    <div class="w-20 h-1.5 bg-white/10 rounded-full overflow-hidden">
                       <div class="h-full bg-blue-500 rounded-full"
                            :style="{ width: Math.min((cdk.used_count / cdk.max_uses) * 100, 100) + '%' }"></div>
                    </div>
                    <span class="text-[10px] font-mono text-white/50">{{ cdk.used_count }}/{{ cdk.max_uses }}</span>
                 </div>
              </td>

              <td class="py-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold border" :class="getStatusClass(cdk)">
                  {{ getStatusText(cdk) }}
                </span>
              </td>

              <td class="py-4 text-right pr-4">
                <button @click="handleDelete(cdk.id)" class="w-7 h-7 rounded-lg bg-red-500/10 hover:bg-red-500 text-red-400 hover:text-white flex items-center justify-center transition-all opacity-60 hover:opacity-100">
                  <i class="ph-bold ph-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>

    <!-- 生成弹窗 -->
    <div v-if="showGenerateModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" @click="showGenerateModal = false"></div>

        <div class="relative w-full max-w-md bg-[#1a2342] border border-white/10 rounded-[24px] shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">

            <div class="px-6 py-4 border-b border-white/10 flex justify-between items-center bg-white/[0.02]">
                <h3 class="text-lg font-bold text-white flex items-center gap-2">
                    <i class="ph-duotone ph-magic-wand text-purple-400"></i> 批量生成 CDK
                </h3>
                <button @click="showGenerateModal = false" class="text-white/40 hover:text-white transition-colors"><i class="ph-bold ph-x text-lg"></i></button>
            </div>

            <div class="p-6 space-y-5">

                <div>
                    <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-2 block flex justify-between">
                        <span>生成数量</span>
                        <span class="text-white font-mono">{{ form.count }} 个</span>
                    </label>
                    <input v-model.number="form.count" type="range" min="1" max="100"
                           class="w-full h-2 bg-white/10 rounded-lg appearance-none cursor-pointer accent-purple-500">
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">奖励类型</label>
                        <div class="relative">
                            <select v-model="form.item_id" class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-purple-500 outline-none appearance-none">
                                <option value="1" class="text-black">💰 金币</option>
                                <option value="2" class="text-black">💎 钻石</option>
                            </select>
                            <i class="ph-bold ph-caret-down absolute right-3 top-3 text-white/30 pointer-events-none"></i>
                        </div>
                    </div>
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">奖励数量</label>
                        <input v-model.number="form.item_count" type="number"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-purple-500 outline-none font-mono">
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">可用次数</label>
                        <input v-model.number="form.max_uses" type="number" min="1"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-purple-500 outline-none font-mono"
                               title="1为一次性，大于1为通用码">
                    </div>
                    <div>
                        <label class="text-xs text-blue-200/60 uppercase tracking-wider mb-1 block">有效期(天)</label>
                        <input v-model.number="form.days" type="number" min="1"
                               class="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:border-purple-500 outline-none font-mono">
                    </div>
                </div>

                <div class="bg-purple-500/10 border border-purple-500/20 rounded-xl p-3 flex gap-3 items-start">
                   <i class="ph-fill ph-info text-purple-400 mt-0.5 shrink-0"></i>
                   <p class="text-[10px] text-purple-100/80 leading-relaxed">
                      提示: 设置 <strong>可用次数 > 1</strong> 可创建多人通用的礼包码（如节日口令）。
                   </p>
                </div>

            </div>

            <div class="p-6 pt-2 flex gap-3 bg-black/20 border-t border-white/5">
                <button @click="showGenerateModal = false" class="flex-1 py-3 rounded-xl border border-white/10 text-white/60 text-sm font-bold hover:bg-white/5 transition-colors">取消</button>
                <button @click="handleGenerate" :disabled="submitting"
                        class="flex-1 py-3 rounded-xl bg-purple-600 border border-purple-400/30 text-white text-sm font-bold shadow-lg shadow-purple-500/20 hover:bg-purple-500 hover:scale-[1.02] active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-2">
                    <i v-if="submitting" class="ph-bold ph-spinner animate-spin"></i>
                    {{ submitting ? '生成中...' : '确认生成' }}
                </button>
            </div>
        </div>
    </div>

  </div>
</template>

<style scoped>
/* 自定义滚动条，保持赛博风格 */

/* 简单的弹窗动画 */
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes zoom-in-95 { from { transform: scale(0.95); } to { transform: scale(1); } }
.animate-in { animation-duration: 0.2s; animation-fill-mode: both; }
.fade-in { animation-name: fade-in; }
.zoom-in-95 { animation-name: zoom-in-95; }
</style>
