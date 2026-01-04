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

// --- 🟢 核心修复：获取数据逻辑 ---
const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await request.get('/audit/', {
      params: {
        search: searchQuery.value,
        page: currentPage.value
      }
    })

    // 1. 获取原始数据 (兼容 axios 的 data 包装)
    const data = res.data || res
    console.log('🔍 后端返回的原始数据:', data) // 方便你在浏览器控制台调试

    // 2. 🟢 万能兼容：处理分页 (results) 或 不分页 (数组)
    let rawLogs = []
    if (Array.isArray(data)) {
        // 情况A: 后端直接返回数组
        rawLogs = data
        totalLogs.value = data.length
    } else if (data.results) {
        // 情况B: 后端返回标准分页对象 { count: 10, results: [...] }
        rawLogs = data.results
        totalLogs.value = data.count || 0
    } else {
        // 情况C: 数据异常
        rawLogs = []
        totalLogs.value = 0
    }

    // 3. 🟢 字段清洗：确保 display_admin 一定有值
    logs.value = rawLogs.map(log => ({
        ...log,
        // 优先取 admin_username，没有则取 admin_name，还没有就显示 '未知'
        display_admin: log.admin_username || log.admin_name || '未知',
        // 确保 action 不为空，防止样式计算报错
        action: log.action || '未知操作'
    }))

    // --- 前端统计逻辑 ---
    // (注意：生产环境建议由后端提供专门的统计接口，前端计算仅适合少量数据)
    stats.value.todayCount = logs.value.filter(l => {
        if (!l.created_at) return false
        const date = new Date(l.created_at)
        const today = new Date()
        return date.getDate() === today.getDate() && date.getMonth() === today.getMonth()
    }).length

    stats.value.deleteCount = logs.value.filter(l =>
      l.action && (l.action.includes('删除') || l.action.includes('封禁'))
    ).length

    const admins = new Set(logs.value.map(l => l.display_admin).filter(n => n !== '未知'))
    stats.value.distinctAdmins = admins.size

  } catch (error) {
    console.error('❌ 加载日志失败:', error)
    // 出错时至少不白屏，显示空列表
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
  const act = action.toLowerCase()
  if (act.includes('删除') || act.includes('封禁') || act.includes('delete') || act.includes('ban')) {
    return 'text-red-400 bg-red-500/10 border-red-500/20'
  }
  if (act.includes('修改') || act.includes('update') || act.includes('编辑')) {
    return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20'
  }
  if (act.includes('创建') || act.includes('create') || act.includes('生成') || act.includes('发送')) {
    return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
  }
  return 'text-blue-400 bg-blue-500/10 border-blue-500/20'
}

onMounted(fetchLogs)
</script>

<template>
  <div class="flex flex-col gap-6 h-full pb-4 relative overflow-y-auto custom-scrollbar pr-2">

    <div class="grid grid-cols-3 gap-6 shrink-0 h-[100px]">
      <div class="relative rounded-[20px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-5 flex items-center justify-between overflow-hidden group">
        <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full bg-blue-500/20 blur-[30px] group-hover:scale-150 transition-transform"></div>
        <div>
           <p class="text-blue-200/50 text-xs font-bold mb-1 uppercase tracking-wider">今日操作</p>
           <h3 class="text-2xl font-bold text-white">{{ stats.todayCount }} <span class="text-xs font-normal text-white/40">条记录</span></h3>
        </div>
        <div class="w-10 h-10 rounded-[14px] bg-blue-500/10 flex items-center justify-center border border-blue-500/20 text-blue-400">
           <i class="ph-duotone ph-clock-counter-clockwise text-xl"></i>
        </div>
      </div>

      <div class="relative rounded-[20px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-5 flex items-center justify-between overflow-hidden group">
        <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full bg-red-500/20 blur-[30px] group-hover:scale-150 transition-transform"></div>
        <div>
           <p class="text-blue-200/50 text-xs font-bold mb-1 uppercase tracking-wider">高危操作</p>
           <h3 class="text-2xl font-bold text-white">{{ stats.deleteCount }} <span class="text-xs font-normal text-white/40">次删除/封禁</span></h3>
        </div>
        <div class="w-10 h-10 rounded-[14px] bg-red-500/10 flex items-center justify-center border border-red-500/20 text-red-400">
           <i class="ph-duotone ph-warning-octagon text-xl"></i>
        </div>
      </div>

      <div class="relative rounded-[20px] border border-white/8 bg-white/2 backdrop-blur-xl shadow-lg p-5 flex items-center justify-between overflow-hidden group">
        <div class="absolute -right-6 -top-6 w-20 h-20 rounded-full bg-purple-500/20 blur-[30px] group-hover:scale-150 transition-transform"></div>
        <div>
           <p class="text-blue-200/50 text-xs font-bold mb-1 uppercase tracking-wider">活跃管理员</p>
           <h3 class="text-2xl font-bold text-white">{{ stats.distinctAdmins }} <span class="text-xs font-normal text-white/40">人</span></h3>
        </div>
        <div class="w-10 h-10 rounded-[14px] bg-purple-500/10 flex items-center justify-center border border-purple-500/20 text-purple-400">
           <i class="ph-duotone ph-user-gear text-xl"></i>
        </div>
      </div>
    </div>

    <div class="rounded-[30px] border border-white/8 bg-white/2 backdrop-blur-2xl shadow-xl overflow-hidden relative shrink-0">
      <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-orange-500/50 to-transparent blur-sm"></div>

      <div class="px-6 py-5 border-b border-white/5 flex justify-between items-center shrink-0">
        <div>
          <h6 class="text-base font-bold text-white tracking-wide flex items-center gap-2">
            <i class="ph-duotone ph-clipboard-text text-orange-400"></i> 系统审计日志
            <span class="ml-2 text-[10px] px-1.5 py-0.5 rounded bg-white/5 border border-white/10 text-white/40 font-mono">共 {{ totalLogs }} 条记录</span>
          </h6>
          <p class="text-[10px] text-blue-200/40 mt-0.5">追踪所有后台操作记录，保障系统安全</p>
        </div>

        <div class="flex gap-3">
            <div class="relative group">
              <i class="ph-bold ph-magnifying-glass absolute left-3 top-2.5 text-white/40 group-focus-within:text-orange-400 transition-colors"></i>
              <input v-model.lazy="searchQuery"
                     @keyup.enter="fetchLogs"
                     type="text"
                     placeholder="搜索操作对象/内容..."
                     class="bg-[#0f1535] border border-white/10 text-white text-xs rounded-xl focus:ring-1 focus:ring-orange-500 focus:border-orange-500 block w-64 pl-9 p-2.5 transition-all outline-none placeholder-white/30">
            </div>
            <button @click="fetchLogs" class="bg-white/5 hover:bg-white/10 text-white px-3 py-2 rounded-xl text-sm font-bold transition border border-white/10">
              <i class="ph-bold ph-arrows-clockwise"></i>
            </button>
        </div>
      </div>

      <div class="p-3">
        <div v-if="loading" class="flex items-center justify-center py-20 text-white/20 text-sm">
          <i class="ph-bold ph-spinner animate-spin mr-2"></i> 加载日志中...
        </div>

        <div v-else-if="logs.length === 0" class="flex flex-col items-center justify-center py-20 text-white/20 text-sm">
          <i class="ph-duotone ph-clipboard text-4xl mb-2 opacity-50"></i>
          <p>暂无审计记录</p>
        </div>

        <table v-else class="w-full text-left border-collapse">
          <thead class="sticky top-0 bg-[#131b35]/95 backdrop-blur-md z-10 rounded-xl">
            <tr class="text-blue-200/40 text-[10px] uppercase tracking-wider">
              <th class="py-3 pl-4 font-semibold rounded-l-xl">操作时间</th>
              <th class="py-3 font-semibold">管理员</th>
              <th class="py-3 font-semibold">动作</th>
              <th class="py-3 font-semibold">模块 / 对象</th>
              <th class="py-3 font-semibold">变更详情</th>
              <th class="py-3 text-right pr-4 font-semibold rounded-r-xl">IP地址</th>
            </tr>
          </thead>
          <tbody class="text-sm">
            <tr v-for="log in logs" :key="log.id"
                class="group hover:bg-white/3 border-white/2 last:border-0 rounded-xl">

              <td class="py-3 pl-4 text-white/40 font-mono text-xs">
                 {{ log.created_at ? new Date(log.created_at).toLocaleString() : '-' }}
              </td>

              <td class="py-3">
                <div class="flex items-center gap-2">
                   <div class="w-6 h-6 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center text-[10px] font-bold text-white border border-white/10">
                      {{ log.display_admin ? log.display_admin.charAt(0).toUpperCase() : '?' }}
                   </div>
                   <span class="font-bold text-white text-xs">{{ log.display_admin }}</span>
                </div>
              </td>

              <td class="py-3">
                 <span class="px-2 py-0.5 rounded text-[10px] font-bold border" :class="getActionStyle(log.action)">
                    {{ log.action }}
                 </span>
              </td>

              <td class="py-3">
                 <div class="flex flex-col">
                    <span class="text-[10px] text-white/40 uppercase">{{ log.app_label }} / {{ log.model_name }}</span>
                    <span class="text-xs text-white font-mono truncate max-w-[150px]" :title="log.target">
                        {{ log.target }}
                    </span>
                 </div>
              </td>

              <td class="py-3 max-w-[300px]">
                 <p class="text-xs text-blue-200/70 truncate group-hover:whitespace-normal group-hover:break-words transition-all cursor-help" :title="log.details">
                    {{ log.details || '-' }}
                 </p>
              </td>

              <td class="py-3 text-right pr-4 text-white/30 font-mono text-xs">
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