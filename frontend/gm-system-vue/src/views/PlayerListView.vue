<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import request from '@/utils/request'

// --- 响应式数据 ---
const players = ref([])
const loading = ref(true)
const totalPlayers = ref(0)

// 筛选与排序
const searchQuery = ref('')
const currentPage = ref(1)
const ordering = ref('-created_at') // 默认按注册时间倒序

// --- 弹窗控制 ---
const showGoldModal = ref(false)   // 充值弹窗
const showEditModal = ref(false)   // 编辑/新建弹窗
const isEditMode = ref(false)      // false=新建, true=编辑

const currentActionPlayer = ref(null)
const goldAmount = ref(1000)

// 编辑表单数据
const formData = ref({
  nickname: '',
  level: 1,
  diamond: 0
})

// --- 1. 核心：获取数据 (查) ---
const fetchPlayers = async () => {
  loading.value = true
  try {
    const res = await request.get('/players/', {
      params: {
        search: searchQuery.value,
        page: currentPage.value,
        ordering: ordering.value
      }
    })

    // 兼容 DRF 的分页响应结构
    const backendData = res.data || res
    if (backendData.results) {
      players.value = backendData.results
      totalPlayers.value = backendData.count
    } else {
      // 兼容未分页的情况
      players.value = backendData
      totalPlayers.value = backendData.length
    }
  } catch (e) {
    console.error("加载失败:", e)
  } finally {
    loading.value = false
  }
}

// 监听筛选条件变化
watch([searchQuery, ordering], () => {
  currentPage.value = 1 // 条件变了重置回第一页
  fetchPlayers()
})

watch(currentPage, () => {
  fetchPlayers()
})

// --- 2. 排序逻辑 ---
const handleSort = (field) => {
  // 如果当前已经是这个字段，则切换正序/倒序
  if (ordering.value === field) {
    ordering.value = `-${field}`
  } else if (ordering.value === `-${field}`) {
    ordering.value = field
  } else {
    // 否则默认倒序（数值大在前）
    ordering.value = `-${field}`
  }
}

// --- 3. 封禁/解封 (状态控制) ---
const toggleBanStatus = async (player) => {
  const isBanned = player.status === 'banned'
  const actionText = isBanned ? '解封' : '封禁'
  const url = isBanned ? `/players/${player.id}/unban/` : `/players/${player.id}/ban/`

  if (!confirm(`确定要${actionText}玩家【${player.nickname}】吗？`)) return

  try {
    const res = await request.post(url)
    // 局部更新状态，避免整页刷新
    player.status = res.data?.data?.status || (isBanned ? 'normal' : 'banned')
    alert(`操作成功：${res.data?.message || '状态已更新'}`)
  } catch (e) {
    alert('操作失败: ' + (e.response?.data?.message || e.message))
  }
}

// --- 4. 充值金币 (资产操作) ---
const openGoldModal = (player) => {
  currentActionPlayer.value = player
  goldAmount.value = 1000
  showGoldModal.value = true
}

const confirmAddGold = async () => {
  if (!currentActionPlayer.value) return
  try {
    await request.post(`/players/${currentActionPlayer.value.id}/add_gold/`, {
      amount: parseInt(goldAmount.value)
    })
    // 刷新列表以显示最新金币
    fetchPlayers()
    showGoldModal.value = false
    alert('充值成功')
  } catch (e) {
    alert('充值失败: ' + (e.response?.data?.message || e.message))
  }
}

// --- 5. 新建/编辑玩家 (增/改) ---
const openCreateModal = () => {
  isEditMode.value = false
  formData.value = { nickname: '', level: 1, diamond: 0 }
  showEditModal.value = true
}

const openEditModal = (player) => {
  isEditMode.value = true
  currentActionPlayer.value = player
  // 填充表单
  formData.value = {
    nickname: player.nickname,
    level: player.level,
    diamond: player.diamond
  }
  showEditModal.value = true
}

const submitEdit = async () => {
  try {
    if (isEditMode.value) {
      // 编辑模式 PUT
      await request.put(`/players/${currentActionPlayer.value.id}/`, formData.value)
      alert('修改成功')
    } else {
      // 新建模式 POST
      await request.post('/players/', formData.value)
      alert('创建成功')
    }
    showEditModal.value = false
    fetchPlayers()
  } catch (e) {
    alert('提交失败: ' + (e.response?.data?.message || JSON.stringify(e.response?.data)))
  }
}

// --- 6. 删除玩家 (删) ---
const deletePlayer = async (player) => {
  if(!confirm(`⚠️ 高危操作\n确定要永久删除玩家【${player.nickname}】吗？\n此操作不可恢复！`)) return

  try {
    await request.delete(`/players/${player.id}/`)
    fetchPlayers()
    alert('删除成功')
  } catch (e) {
    alert('删除失败')
  }
}

// 计算总页数 (假设每页20条，后端默认配置)
const totalPages = computed(() => Math.ceil(totalPlayers.value / 20))

onMounted(() => { fetchPlayers() })
</script>

<template>
  <div class="flex flex-col gap-6 h-full pb-4 relative overflow-y-auto custom-scrollbar pr-2">

    <div class="flex justify-between items-center bg-[#1a1f37]/60 backdrop-blur-3xl p-5 rounded-[24px] border border-white/[0.08] shadow-xl shrink-0">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-[18px] bg-blue-500/20 flex items-center justify-center text-blue-400">
          <i class="ph-fill ph-users-three text-2xl"></i>
        </div>
        <div>
          <h2 class="text-lg font-bold text-white tracking-tight">玩家管理</h2>
          <div class="flex items-center gap-2 mt-0.5">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.6)]"></span>
            <p class="text-xs text-white/50 font-medium">共找到 {{ totalPlayers }} 名玩家</p>
          </div>
        </div>
      </div>

      <div class="flex gap-3">
        <div class="relative group">
          <i class="ph-bold ph-magnifying-glass absolute left-3 top-2.5 text-white/40 group-focus-within:text-blue-400 transition-colors"></i>
          <input v-model.lazy="searchQuery"
                 @keyup.enter="fetchPlayers"
                 type="text"
                 placeholder="搜索昵称..."
                 class="bg-[#0f1535] border border-white/10 text-white text-sm rounded-xl focus:ring-1 focus:ring-blue-500 focus:border-blue-500 block w-64 pl-9 p-2 transition-all outline-none placeholder-white/30">
        </div>

        <button @click="openCreateModal" class="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-xl text-sm font-bold transition flex items-center gap-2 shadow-lg shadow-blue-600/30">
          <i class="ph-bold ph-plus"></i> 新建玩家
        </button>

        <button @click="fetchPlayers" class="bg-white/5 hover:bg-white/10 text-white px-3 py-2 rounded-xl text-sm font-bold transition border border-white/10">
          <i class="ph-bold ph-arrows-clockwise"></i>
        </button>
      </div>
    </div>

    <div class="bg-[#1a1f37]/60 backdrop-blur-3xl rounded-[24px] border border-white/[0.08] shadow-xl overflow-hidden relative shrink-0">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-blue-500/30 to-transparent blur-sm"></div>

      <div class="p-0">
        <table class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-[#1a1f37]/95 backdrop-blur-md z-10 shadow-sm border-b border-white/[0.05]">
            <tr class="text-white/40 text-[10px] font-semibold uppercase tracking-wider">
              <th class="py-4 pl-6">玩家信息</th>
              <th class="py-4 cursor-pointer hover:text-blue-400 transition-colors select-none" @click="handleSort('level')">
                等级 <i v-if="ordering.includes('level')" class="ph-bold" :class="ordering === '-level' ? 'ph-arrow-down' : 'ph-arrow-up'"></i>
              </th>
              <th class="py-4 cursor-pointer hover:text-blue-400 transition-colors select-none" @click="handleSort('gold')">
                资产详情 <i v-if="ordering.includes('gold') || ordering.includes('diamond')" class="ph-bold ph-arrows-down-up"></i>
              </th>
              <th class="py-4 cursor-pointer hover:text-blue-400 transition-colors select-none" @click="handleSort('created_at')">
                注册时间 <i v-if="ordering.includes('created_at')" class="ph-bold" :class="ordering === '-created_at' ? 'ph-arrow-down' : 'ph-arrow-up'"></i>
              </th>
              <th class="py-4">状态</th>
              <th class="py-4 text-right pr-6">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-white/[0.02]">
            <tr v-if="loading" class="animate-pulse">
                <td colspan="6" class="py-8 text-center text-white/20">正在同步数据...</td>
            </tr>
            <tr v-else v-for="player in players" :key="player.id" class="group hover:bg-white/[0.03] transition-colors">

              <td class="py-4 pl-6">
                <div class="flex items-center gap-3">
                  <div class="w-9 h-9 rounded-[10px] bg-white/5 flex items-center justify-center text-white font-bold text-xs border border-white/10 shadow-inner">
                    {{ player.nickname.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <div class="font-bold text-white text-xs group-hover:text-blue-400 transition-colors">{{ player.nickname }}</div>
                    <div class="text-[10px] text-white/30 font-mono mt-0.5 select-all">ID: {{ player.id }}</div>
                  </div>
                </div>
              </td>

              <td class="py-4">
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-white/5 text-white/70 border border-white/10">
                  Lv.{{ player.level }}
                </span>
              </td>

              <td class="py-4">
                <div class="flex items-center gap-4">
                  <div class="flex items-center gap-1.5 group/gold cursor-pointer" @click="openGoldModal(player)" title="快速充值">
                    <i class="ph-fill ph-coins text-yellow-400 text-sm"></i>
                    <span class="text-white/80 font-mono text-xs">{{ player.gold.toLocaleString() }}</span>
                    <i class="ph-bold ph-plus text-blue-400 opacity-0 group-hover/gold:opacity-100 transition-opacity text-[10px]"></i>
                  </div>
                  <div class="flex items-center gap-1.5 opacity-50">
                    <i class="ph-fill ph-diamond text-cyan-400 text-sm"></i>
                    <span class="text-white/80 font-mono text-xs">{{ player.diamond.toLocaleString() }}</span>
                  </div>
                </div>
              </td>

              <td class="py-4 text-white/40 text-[11px] font-mono">
                {{ new Date(player.created_at).toLocaleString() }}
              </td>

              <td class="py-4">
                <div class="flex items-center gap-2">
                  <div class="w-1.5 h-1.5 rounded-full"
                       :class="player.status === 'normal' ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]' : 'bg-red-500'"></div>
                  <span class="text-xs font-medium" :class="player.status === 'normal' ? 'text-emerald-300' : 'text-red-300'">
                    {{ player.status === 'normal' ? '正常' : '封禁中' }}
                  </span>
                </div>
              </td>

              <td class="py-4 text-right pr-6">
                <div class="flex justify-end gap-1 opacity-60 group-hover:opacity-100 transition-opacity">
                   <button @click="openEditModal(player)" class="w-7 h-7 rounded hover:bg-white/10 hover:text-blue-400 text-white/40 transition flex items-center justify-center" title="编辑资料">
                    <i class="ph-bold ph-pencil-simple"></i>
                  </button>

                  <button @click="openGoldModal(player)" class="w-7 h-7 rounded hover:bg-yellow-500/10 hover:text-yellow-400 text-white/40 transition flex items-center justify-center" title="充值">
                    <i class="ph-bold ph-coins"></i>
                  </button>

                  <button @click="toggleBanStatus(player)"
                          class="w-7 h-7 rounded transition flex items-center justify-center"
                          :class="player.status === 'normal' ? 'text-white/40 hover:text-red-400 hover:bg-red-500/10' : 'text-emerald-400 hover:bg-emerald-500/10'"
                          :title="player.status === 'normal' ? '封禁' : '解封'">
                    <i class="ph-bold" :class="player.status === 'normal' ? 'ph-lock-key' : 'ph-lock-key-open'"></i>
                  </button>

                  <button @click="deletePlayer(player)" class="w-7 h-7 rounded hover:bg-red-500/20 hover:text-red-500 text-white/20 transition flex items-center justify-center" title="删除账号">
                    <i class="ph-bold ph-trash"></i>
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="players.length === 0 && !loading">
              <td colspan="6" class="py-20 text-center">
                <div class="flex flex-col items-center gap-3">
                  <div class="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center text-white/20 border border-white/5">
                    <i class="ph-duotone ph-user-list text-2xl"></i>
                  </div>
                  <span class="text-white/30 text-xs font-medium">暂无符合条件的玩家</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showGoldModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in zoom-in duration-200">
      <div class="bg-[#1a1f37] w-full max-w-sm rounded-[24px] border border-white/10 shadow-2xl p-6 relative overflow-hidden">
        <div class="absolute top-0 right-0 w-32 h-32 bg-yellow-500/10 blur-[50px] pointer-events-none"></div>

        <div class="flex justify-between items-center mb-4 relative z-10">
          <h3 class="text-lg font-bold text-white flex items-center gap-2"><i class="ph-fill ph-coins text-yellow-500"></i> 发放福利</h3>
          <button @click="showGoldModal = false" class="text-white/40 hover:text-white transition"><i class="ph-bold ph-x"></i></button>
        </div>
        <p class="text-white/60 text-xs mb-6">正在为 <span class="text-white font-bold mx-1 bg-white/10 px-1 rounded">{{ currentActionPlayer?.nickname }}</span> 增加金币。</p>

        <div class="mb-6">
          <div class="relative">
            <input v-model="goldAmount" type="number" class="w-full bg-[#0f1535] border border-white/10 rounded-xl py-3 pl-4 pr-4 text-white focus:ring-1 focus:ring-yellow-500 focus:border-yellow-500 outline-none font-mono text-xl text-center font-bold">
          </div>
          <div class="grid grid-cols-3 gap-2 mt-3">
            <button @click="goldAmount = 1000" class="py-2 rounded-lg bg-white/5 text-xs text-white/60 hover:text-white hover:bg-white/10 transition border border-white/5">+1,000</button>
            <button @click="goldAmount = 10000" class="py-2 rounded-lg bg-white/5 text-xs text-white/60 hover:text-white hover:bg-white/10 transition border border-white/5">+10,000</button>
            <button @click="goldAmount = 100000" class="py-2 rounded-lg bg-white/5 text-xs text-white/60 hover:text-white hover:bg-white/10 transition border border-white/5">+100,000</button>
          </div>
        </div>

        <div class="flex gap-3">
          <button @click="showGoldModal = false" class="flex-1 py-2.5 rounded-xl text-white/60 hover:bg-white/5 transition text-sm font-bold">取消</button>
          <button @click="confirmAddGold" class="flex-1 py-2.5 rounded-xl bg-yellow-500 text-[#1a1f37] font-bold hover:bg-yellow-400 shadow-lg shadow-yellow-500/20 transition text-sm">确认发放</button>
        </div>
      </div>
    </div>

    <div v-if="showEditModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in zoom-in duration-200">
      <div class="bg-[#1a1f37] w-full max-w-sm rounded-[24px] border border-white/10 shadow-2xl p-6 relative">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-bold text-white">{{ isEditMode ? '编辑玩家' : '新建玩家' }}</h3>
          <button @click="showEditModal = false" class="text-white/40 hover:text-white transition"><i class="ph-bold ph-x"></i></button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="text-[10px] uppercase text-white/40 font-bold tracking-wider mb-1 block">昵称</label>
            <input v-model="formData.nickname" type="text" class="w-full bg-[#0f1535] border border-white/10 rounded-xl p-3 text-white focus:ring-1 focus:ring-blue-500 outline-none">
          </div>

          <div class="grid grid-cols-2 gap-4">
             <div>
                <label class="text-[10px] uppercase text-white/40 font-bold tracking-wider mb-1 block">等级</label>
                <input v-model="formData.level" type="number" class="w-full bg-[#0f1535] border border-white/10 rounded-xl p-3 text-white focus:ring-1 focus:ring-blue-500 outline-none">
             </div>
             <div>
                <label class="text-[10px] uppercase text-white/40 font-bold tracking-wider mb-1 block">钻石</label>
                <input v-model="formData.diamond" type="number" class="w-full bg-[#0f1535] border border-white/10 rounded-xl p-3 text-white focus:ring-1 focus:ring-blue-500 outline-none">
             </div>
          </div>
        </div>

        <div class="flex gap-3 mt-8">
          <button @click="showEditModal = false" class="flex-1 py-2.5 rounded-xl text-white/60 hover:bg-white/5 transition text-sm font-bold">取消</button>
          <button @click="submitEdit" class="flex-1 py-2.5 rounded-xl bg-blue-600 text-white font-bold hover:bg-blue-500 shadow-lg shadow-blue-600/30 transition text-sm">
            {{ isEditMode ? '保存修改' : '立即创建' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* 禁用选中文字，防止点击排序时选中表头 */
.select-none { user-select: none; }
</style>
