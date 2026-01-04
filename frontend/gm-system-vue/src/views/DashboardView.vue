<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(true)

// --- 1. 统计卡片数据 ---
const statsCards = ref([
  { label: '玩家总数', value: '0', sub: '最新注册', icon: 'ph-users', color: 'text-blue-400', bg: 'bg-blue-500/10' },
  { label: '生效公告', value: '0', sub: '当前展示中', icon: 'ph-broadcast', color: 'text-purple-400', bg: 'bg-purple-500/10' },
  { label: 'CDK库存', value: '0', sub: '剩余可用', icon: 'ph-ticket', color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
])

// --- 2. 最新玩家列表 ---
const recentPlayers = ref([])

// --- 3. 核心：通用解包函数 ---
// 能同时处理 "统一响应格式"、"分页数据" 和 "纯列表数据"
const unwrap = (res) => {
  if (!res) return { count: 0, list: [] }

  // 1. 剥离 axios 外壳 & 统一响应外壳 (code=200)
  // 很多 axios 拦截器会直接返回 res.data，这里做双重兼容
  let body = res.data || res
  if (body && body.code === 200 && body.data) {
    body = body.data
  }

  // 2. 识别数据结构
  if (Array.isArray(body)) {
    // 情况A: 后端未开启分页，直接返回列表 [ ... ]
    return { count: body.length, list: body }
  } else if (body && body.results) {
    // 情况B: 后端开启了分页，返回 { count: 10, results: [ ... ] }
    return { count: body.count, list: body.results }
  } else {
    // 情况C: 数据异常或为空
    return { count: 0, list: [] }
  }
}

// --- 4. 获取数据 (独立请求，互不影响) ---
const fetchData = async () => {
  loading.value = true

  // 1️⃣ 获取玩家数据
  try {
    // 注意：由于后端可能未配置全局分页，page_size 参数可能被忽略，返回所有数据
    // 我们在前端做 slice(0, 5) 截取以保证显示正常
    const res = await request.get('/players/', { params: { ordering: '-created_at' } })
    const data = unwrap(res)

    statsCards.value[0].value = data.count.toLocaleString()

    // 安全映射数据
    recentPlayers.value = (data.list || []).slice(0, 5).map(p => ({
      id: p.id,
      // 保护 id 字段，防止 undefined 报错
      displayId: p.id ? p.id.toString() : 'UNKNOWN',
      nickname: p.nickname || '未命名',
      level: p.level || 1,
      gold: p.gold || 0,
      status: p.status || 'normal',
      regTime: p.created_at ? new Date(p.created_at).toLocaleDateString() : '刚刚'
    }))
  } catch (e) {
    console.error("❌ 玩家数据加载失败:", e)
  }

  // 2️⃣ 获取公告统计
  try {
    const res = await request.get('/notices/')
    const data = unwrap(res)
    statsCards.value[1].value = data.count.toLocaleString()
  } catch (e) {
    console.error("❌ 公告数据加载失败:", e)
  }

  // 3️⃣ 获取 CDK 统计
  try {
    const res = await request.get('/cdks/')
    const data = unwrap(res)
    statsCards.value[2].value = data.count.toLocaleString()
  } catch (e) {
    console.error("❌ CDK 数据加载失败:", e)
  }

  loading.value = false
}

// --- 5. 快捷跳转 ---
const navigateTo = (path) => {
  router.push(path)
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="flex flex-col gap-6 h-full pb-4">

    <div class="grid grid-cols-3 gap-6 shrink-0 h-[120px]">
      <div v-for="(item, index) in statsCards" :key="index"
           class="relative rounded-[24px] border border-white/[0.08] bg-white/[0.02] backdrop-blur-xl shadow-lg p-5 flex flex-col justify-center overflow-hidden group hover:bg-white/[0.05] transition-all duration-500">

        <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full blur-[40px] opacity-20 transition-all duration-500 group-hover:scale-150"
             :class="item.color.replace('text-', 'bg-')"></div>

        <div class="flex justify-between items-center relative z-10">
          <div>
            <p class="text-blue-200/50 text-xs font-bold mb-1 tracking-wider uppercase">{{ item.label }}</p>
            <div class="flex items-end gap-3">
              <h3 class="text-3xl font-bold text-white tracking-tight">{{ item.value }}</h3>
              <span class="text-[10px] text-white/40 mb-1.5 font-medium border border-white/10 px-1.5 rounded bg-white/5">
                {{ item.sub }}
              </span>
            </div>
          </div>

          <div class="w-12 h-12 rounded-[18px] flex items-center justify-center shadow-inner border border-white/5"
               :class="item.bg">
            <i class="ph-fill text-2xl" :class="[item.color, item.icon]"></i>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-12 gap-6 flex-1 min-h-0">

      <div class="col-span-8 flex flex-col rounded-[30px] border border-white/[0.08] bg-white/[0.02] backdrop-blur-2xl shadow-xl overflow-hidden relative transition-all duration-300">
        <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-gradient-to-r from-transparent via-blue-500/50 to-transparent blur-sm"></div>

        <div class="px-6 py-5 border-b border-white/[0.05] flex justify-between items-center shrink-0">
          <div>
            <h6 class="text-base font-bold text-white tracking-wide flex items-center gap-2">
              <i class="ph-duotone ph-user-plus text-blue-400"></i> 最新注册玩家
            </h6>
            <p class="text-[10px] text-blue-200/40 mt-0.5">实时同步 • 获取最近 5 条记录</p>
          </div>
          <button @click="navigateTo('/players')" class="text-xs text-blue-400 hover:text-blue-300 transition-colors">
            查看全部 <i class="ph-bold ph-arrow-right inline-block align-middle"></i>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto custom-scrollbar p-3">
          <table class="w-full text-left border-collapse">
            <thead class="sticky top-0 bg-[#131b35]/90 backdrop-blur-md z-10 rounded-xl">
              <tr class="text-blue-200/40 text-[10px] uppercase tracking-wider">
                <th class="py-3 pl-4 font-semibold rounded-l-xl">玩家昵称</th>
                <th class="py-3 font-semibold">等级</th>
                <th class="py-3 font-semibold">持有金币</th>
                <th class="py-3 font-semibold">状态</th>
                <th class="py-3 text-right pr-4 font-semibold rounded-r-xl">注册日期</th>
              </tr>
            </thead>
            <tbody class="text-sm">
              <tr v-if="loading && recentPlayers.length === 0" class="text-center text-white/20">
                <td colspan="5" class="py-8">
                  <i class="ph-bold ph-spinner animate-spin mr-1"></i> 加载数据中...
                </td>
              </tr>
              <tr v-else-if="recentPlayers.length === 0" class="text-center text-white/20">
                <td colspan="5" class="py-8">暂无玩家数据</td>
              </tr>
              <tr v-else v-for="player in recentPlayers" :key="player.id"
                  class="group hover:bg-white/[0.03] transition-all border-b border-white/[0.02] last:border-0 rounded-xl">
                <td class="py-4 pl-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shadow-lg">
                      {{ player.nickname.charAt(0).toUpperCase() }}
                    </div>
                    <div>
                      <div class="font-bold text-white text-xs group-hover:text-blue-400 transition-colors">{{ player.nickname }}</div>
                      <div class="text-[10px] text-white/30 font-mono mt-0.5 cursor-help max-w-[100px] truncate" :title="'ID: ' + player.id">
                        ID: {{ player.displayId }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="py-4">
                  <span class="font-mono text-blue-200/80">Lv.{{ player.level }}</span>
                </td>
                <td class="py-4">
                  <div class="flex items-center gap-1 text-amber-400">
                    <i class="ph-fill ph-coins"></i>
                    <span class="text-xs font-medium">{{ player.gold.toLocaleString() }}</span>
                  </div>
                </td>
                <td class="py-4">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold border"
                        :class="player.status === 'normal'
                          ? 'bg-green-500/10 border-green-500/20 text-green-400'
                          : 'bg-red-500/10 border-red-500/20 text-red-400'">
                    {{ player.status === 'normal' ? '正常' : '封禁中' }}
                  </span>
                </td>
                <td class="py-4 text-right pr-4 text-white/40 text-xs">
                  {{ player.regTime }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="col-span-4 flex flex-col gap-6">

        <div class="h-[180px] relative rounded-[30px] overflow-hidden group shadow-2xl border border-white/10">
          <div class="absolute inset-0 bg-gradient-to-br from-blue-600/80 to-purple-900/80 transition-all duration-700 group-hover:scale-110"></div>
          <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>

          <div class="relative z-10 p-6 h-full flex flex-col justify-between">
            <div class="flex justify-between items-start">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-md border border-white/20 flex items-center justify-center text-lg font-bold shadow-lg">
                  GM
                </div>
                <div>
                  <h3 class="text-lg font-bold leading-tight">管理员</h3>
                  <span class="text-[10px] font-medium bg-black/20 px-2 py-0.5 rounded text-white/80">超级权限</span>
                </div>
              </div>
            </div>

            <div class="bg-black/20 backdrop-blur-sm rounded-xl p-3 flex justify-between items-center border border-white/5">
              <div>
                <p class="text-blue-100/70 text-[10px] mb-0.5">系统状态</p>
                <div class="flex items-baseline gap-1">
                  <h2 class="text-lg font-bold text-green-400">运行正常</h2>
                </div>
              </div>
              <div class="h-8 w-8 rounded-lg bg-green-500/20 flex items-center justify-center">
                <i class="ph-bold ph-activity text-green-400"></i>
              </div>
            </div>
          </div>
        </div>

        <div class="flex-1 rounded-[30px] border border-white/[0.08] bg-white/[0.02] backdrop-blur-2xl shadow-xl p-6 flex flex-col transition-all duration-300">
          <h6 class="text-xs font-bold text-blue-200/40 uppercase tracking-widest mb-4">快捷操作中心</h6>

          <div class="grid grid-cols-2 gap-3 h-full">
            <button @click="navigateTo('/notices')"
                    class="flex flex-col items-center justify-center gap-2 bg-white/[0.02] border border-white/5 hover:bg-blue-600 rounded-2xl hover:border-transparent hover:shadow-lg hover:shadow-blue-500/30 transition-all duration-300 group">
              <i class="ph-duotone ph-broadcast text-2xl text-blue-400 group-hover:text-white transition-colors"></i>
              <span class="text-[11px] font-medium text-white/60 group-hover:text-white">发布公告</span>
            </button>

            <button @click="navigateTo('/mails')"
                    class="flex flex-col items-center justify-center gap-2 bg-white/[0.02] border border-white/5 hover:bg-emerald-500 rounded-2xl hover:border-transparent hover:shadow-lg hover:shadow-emerald-500/30 transition-all duration-300 group">
              <i class="ph-duotone ph-envelope-simple text-2xl text-emerald-400 group-hover:text-white transition-colors"></i>
              <span class="text-[11px] font-medium text-white/60 group-hover:text-white">发送邮件</span>
            </button>

            <button @click="navigateTo('/cdks')"
                    class="flex flex-col items-center justify-center gap-2 bg-white/[0.02] border border-white/5 hover:bg-purple-500 rounded-2xl hover:border-transparent hover:shadow-lg hover:shadow-purple-500/30 transition-all duration-300 group">
              <i class="ph-duotone ph-gift text-2xl text-purple-400 group-hover:text-white transition-colors"></i>
              <span class="text-[11px] font-medium text-white/60 group-hover:text-white">生成礼包</span>
            </button>

            <button @click="navigateTo('/audit')"
                    class="flex flex-col items-center justify-center gap-2 bg-white/[0.02] border border-white/5 hover:bg-orange-500 rounded-2xl hover:border-transparent hover:shadow-lg hover:shadow-orange-500/30 transition-all duration-300 group">
              <i class="ph-duotone ph-clipboard-text text-2xl text-orange-400 group-hover:text-white transition-colors"></i>
              <span class="text-[11px] font-medium text-white/60 group-hover:text-white">审计日志</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
