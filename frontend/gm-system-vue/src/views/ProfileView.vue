<script setup>
import { ref, onMounted, watch } from 'vue'
import request from '@/utils/request'

// --- 数据定义 ---
const logs = ref([])
const loading = ref(true)
const totalLogs = ref(0)
const searchQuery = ref('')
const currentPage = ref(1)

// 统计数据
const stats = ref({
  todayCount: 0,
  deleteCount: 0,
  distinctAdmins: 0
})

// --- 获取数据 ---
const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await request.get('/audit/', {
      params: {
        search: searchQuery.value,
        page: currentPage.value
      }
    })

    // 1. 兼容性处理：无论后端返回 { results: [] } 还是直接 [] 都能接住
    const responseData = res.data || res
    const rawLogs = Array.isArray(responseData) ? responseData : (responseData.results || [])

    // 2. 🟢 数据清洗（核心修复点）：防止 null/undefined 导致报错
    logs.value = rawLogs.map(log => ({
      ...log,
      // 如果 action 为空，给默认值，防止 .includes 报错
      action: log.action || '未知操作',
      // 如果 admin_name 为空，显示 '系统' 或 '未知'
      admin_name: log.admin_name || '系统',
      // 确保 target 不为空
      target: log.target || '-',
      // 确保 details 不为空
      details: log.details || '-'
    }))

    totalLogs.value = responseData.count || logs.value.length

    // 3. 统计计算（增加空值保护）
    stats.value.todayCount = logs.value.filter(l => {
        if (!l.created_at) return false
        const date = new Date(l.created_at)
        const today = new Date()
        return date.getDate() === today.getDate() && date.getMonth() === today.getMonth()
    }).length

    // 🟢 修复报错：加了 ?. 保护，防止 action 为 null 时崩盘
    stats.value.deleteCount = logs.value.filter(l =>
      l.action?.includes('删除') || l.action?.includes('封禁')
    ).length

    const admins = new Set(logs.value.map(l => l.admin_name))
    stats.value.distinctAdmins = admins.size

  } catch (error) {
    console.error('❌ 加载日志失败:', error)
    // 出错时重置为空数组，防止页面白屏
    logs.value = []
  } finally {
    loading.value = false
  }
}

// 监听搜索
watch(searchQuery, () => {
  currentPage.value = 1
  fetchLogs()
})

watch(currentPage, fetchLogs)

// --- 样式辅助 ---
const getActionStyle = (action) => {
  if (!action) return 'text-gray-400 bg-gray-500/10 border-gray-500/20'
  const act = action.toString() // 强转字符串，防止意外
  if (act.includes('删除') || act.includes('封禁') || act.includes('Delete')) {
    return 'text-red-400 bg-red-500/10 border-red-500/20'
  }
  if (act.includes('修改') || act.includes('Update') || act.includes('编辑')) {
    return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
  }
  if (act.includes('创建') || act.includes('Create') || act.includes('生成') || act.includes('发送')) {
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
  }
  return 'text-blue-400 bg-blue-500/10 border-blue-500/20'
}

onMounted(fetchLogs)
</script>

<template>
  <div class="flex flex-col gap-6 h-full pb-6 relative overflow-y-auto custom-scrollbar pr-2">

    <div class="grid grid-cols-3 gap-6 shrink-0 h-[110px]">

      <div class="relative rounded-[24px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-6 flex items-center justify-between overflow-hidden group hover:bg-white/[0.04] transition-all">
        <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-blue-500/20 blur-[40px] group-hover:scale-150 transition-transform"></div>
        <div>
           <p class="text-blue-200/60 text-sm font-bold mb-2 uppercase tracking-wider">今日操作</p>
           <h3 class="text-3xl font-bold text-white">{{ stats.todayCount }} <span class="text-sm font-normal text-white/40 ml-1">条</span></h3>
        </div>
        <div class="w-12 h-12 rounded-[18px] bg-blue-500/10 flex items-center justify-center border border-blue-500/20 text-blue-400 group-hover:scale-110 transition-transform">
           <i class="ph-duotone ph-clock-counter-clockwise text-2xl"></i>
        </div>
      </div>

      <div class="relative rounded-[24px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-6 flex items-center justify-between overflow-hidden group hover:bg-white/[0.04] transition-all">
        <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-red-500/20 blur-[40px] group-hover:scale-150 transition-transform"></div>
        <div>
           <p class="text-red-200/60 text-sm font-bold mb-2 uppercase tracking-wider">敏感操作</p>
           <h3 class="text-3xl font-bold text-white">{{ stats.deleteCount }} <span class="text-sm font-normal text-white/40 ml-1">次</span></h3>
        </div>
        <div class="w-12 h-12 rounded-[18px] bg-red-500/10 flex items-center justify-center border border-red-500/20 text-red-400 group-hover:scale-110 transition-transform">
           <i class="ph-duotone ph-warning-octagon text-2xl"></i>
        </div>
      </div>

      <div class="relative rounded-[24px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-6 flex items-center justify-between overflow-hidden group hover:bg-white/[0.04] transition-all">
        <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full bg-purple-500/20 blur-[40px] group-hover:scale-150 transition-transform"></div>
        <div>
           <p class="text-purple-200/60 text-sm font-bold mb-2 uppercase tracking-wider">活跃管理员</p>
           <h3 class="text-3xl font-bold text-white">{{ stats.distinctAdmins }} <span class="text-sm font-normal text-white/40 ml-1">人</span></h3>
        </div>
        <div class="w-12 h-12 rounded-[18px] bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400 group-hover:scale-110 transition-transform">
           <i class="ph-duotone ph-user-gear text-2xl"></i>
        </div>
      </div>
    </div>

    <div class="rounded-[30px] border border-white/8 bg-white/2 backdrop-blur-2xl shadow-xl overflow-hidden relative shrink-0">

      <div class="px-8 py-6 border-b border-white/5 flex justify-between items-center shrink-0">
        <div>
          <h6 class="text-lg font-bold text-white tracking-wide flex items-center gap-3">
            <i class="ph-duotone ph-clipboard-text text-orange-400 text-xl"></i> 系统审计日志
            <span class="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/40 font-mono">共 {{ totalLogs }} 条记录</span>
          </h6>
          <p class="text-xs text-blue-200/50 mt-1">追踪所有后台操作记录，保障系统安全</p>
        </div>

        <div class="flex gap-4">
            <div class="relative group">
              <i class="ph-bold ph-magnifying-glass absolute left-3.5 top-3 text-white/40 group-focus-within:text-orange-400 transition-colors"></i>
              <input v-model.lazy="searchQuery"
                     @keyup.enter="fetchLogs"
                     type="text"
                     placeholder="搜索操作对象/内容..."
                     class="bg-[#0f1535] border border-white/10 text-white text-sm rounded-xl focus:ring-1 focus:ring-orange-500 focus:border-orange-500 block w-72 pl-10 p-2.5 transition-all outline-none placeholder-white/30 h-10">
            </div>
            <button @click="fetchLogs" class="h-10 w-10 flex items-center justify-center bg-white/5 hover:bg-white/10 text-white rounded-xl transition border border-white/10 active:scale-95">
              <i class="ph-bold ph-arrows-clockwise text-lg"></i>
            </button>
        </div>
      </div>

      <div class="p-4">
        <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-white/30 gap-3">
          <i class="ph-duotone ph-spinner animate-spin text-3xl"></i>
          <span class="text-sm">正在同步日志数据...</span>
        </div>

        <div v-else-if="logs.length === 0" class="flex flex-col items-center justify-center py-20 text-white/20 gap-4">
          <div class="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center">
            <i class="ph-duotone ph-clipboard text-4xl opacity-50"></i>
          </div>
          <p class="text-sm">暂无审计记录</p>
        </div>

        <table v-else class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-[#131b35]/95 backdrop-blur-md z-10 shadow-sm">
            <tr class="text-blue-200/50 text-xs uppercase tracking-wider">
              <th class="py-4 pl-6 font-semibold w-48">操作时间</th>
              <th class="py-4 font-semibold w-40">管理员</th>
              <th class="py-4 font-semibold w-32">动作</th>
              <th class="py-4 font-semibold w-48">模块 / 对象</th>
              <th class="py-4 font-semibold">变更详情</th>
              <th class="py-4 text-right pr-6 font-semibold w-40">IP地址</th>
            </tr>
          </thead>
          <tbody class="text-sm"> <tr v-for="log in logs" :key="log.id"
                class="group hover:bg-white/4 border-white/3 last:border-0">

              <td class="py-4 pl-6 text-white/60 font-mono text-xs">
                 {{ new Date(log.created_at).toLocaleString() }}
              </td>

              <td class="py-4">
                <div class="flex items-center gap-3">
                   <div class="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 flex items-center justify-center text-xs font-bold text-white border border-white/10 shadow-inner">
                      {{ log.admin_name ? log.admin_name.charAt(0).toUpperCase() : 'S' }}
                   </div>
                   <span class="font-medium text-white">{{ log.admin_name }}</span>
                </div>
              </td>

              <td class="py-4">
                 <span class="px-3 py-1 rounded-lg text-xs font-bold border tracking-wide" :class="getActionStyle(log.action)">
                    {{ log.action }}
                 </span>
              </td>

              <td class="py-4">
                 <div class="flex flex-col gap-1">
                    <span class="text-[10px] text-white/40 uppercase font-bold tracking-wider">{{ log.app_label }} · {{ log.model_name }}</span>
                    <span class="text-xs text-blue-100 font-mono truncate max-w-[160px]" :title="log.target">
                        {{ log.target }}
                    </span>
                 </div>
              </td>

              <td class="py-4 max-w-[400px]">
                 <p class="text-xs text-white/60 truncate group-hover:whitespace-normal group-hover:break-words transition-all cursor-help leading-relaxed" :title="log.details">
                    {{ log.details }}
                 </p>
              </td>

              <td class="py-4 text-right pr-6 text-white/30 font-mono text-xs">
                 {{ log.ip_address || 'Unknown' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<style scoped>
</style>
