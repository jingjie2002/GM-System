<script setup>
import { ref, onBeforeMount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// 页面标题映射
const pageTitle = computed(() => {
  const map = {
    'dashboard': '仪表盘',
    'players': '玩家管理',
    'player-detail': '玩家详情',
    'mails': '邮件管理',
    'notices': '公告管理',
    'cdks': '礼包码(CDK)',
    'audit': '审计日志',
    'profile': '个人中心'
  }
  return map[route.name] || route.meta.title || 'GM 管理系统'
})

// 退出登录
const handleLogout = () => {
  if(confirm('确定要退出登录吗？')) {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('username')
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('refresh_token')
    sessionStorage.removeItem('username')
    router.push('/login')
  }
}

// 获取当前登录用户名
const currentAdminName = computed(() => {
    const userInfo = localStorage.getItem('user_info')
    return userInfo ? JSON.parse(userInfo).username : 'Admin'
})

// 强制深色模式
onBeforeMount(() => {
  document.documentElement.classList.add('dark')
  localStorage.setItem('theme', 'dark')
})
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#1e1a4a] to-[#0f172a] text-white font-sans flex overflow-hidden">

    <aside class="fixed top-5 left-5 bottom-5 w-[260px] bg-white/[0.03] backdrop-blur-2xl border border-white/[0.05] rounded-[30px] p-4 z-50 flex flex-col shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] overflow-hidden transition-all duration-300">

      <nav class="flex-1 space-y-2 mt-2 overflow-y-auto custom-scrollbar">

        <div class="px-4 mb-2 text-[10px] font-bold text-blue-200/50 uppercase tracking-widest">控制台</div>

        <RouterLink to="/dashboard" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group relative overflow-hidden"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500 shadow-lg shadow-blue-500/30' : 'text-gray-400 hover:bg-white/5'">
            <div v-if="isActive" class="absolute inset-0 bg-white/20 blur-md opacity-30"></div>
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors relative z-10"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-house text-lg"></i>
            </div>
            <span class="text-sm font-bold relative z-10" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">仪表盘</span>
          </a>
        </RouterLink>

        <div class="px-4 mt-6 mb-2 text-[10px] font-bold text-blue-200/50 uppercase tracking-widest">游戏运营</div>

        <RouterLink to="/players" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'text-gray-400 hover:bg-white/5'">
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-users text-lg"></i>
            </div>
            <span class="text-sm font-medium" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">玩家管理</span>
          </a>
        </RouterLink>

        <RouterLink to="/mails" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'text-gray-400 hover:bg-white/5'">
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-envelope text-lg"></i>
            </div>
            <span class="text-sm font-medium" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">邮件管理</span>
          </a>
        </RouterLink>

        <RouterLink to="/notices" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'text-gray-400 hover:bg-white/5'">
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-megaphone text-lg"></i>
            </div>
            <span class="text-sm font-medium" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">公告管理</span>
          </a>
        </RouterLink>

        <RouterLink to="/cdks" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'text-gray-400 hover:bg-white/5'">
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-gift text-lg"></i>
            </div>
            <span class="text-sm font-medium" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">礼包码</span>
          </a>
        </RouterLink>

        <div class="px-4 mt-6 mb-2 text-[10px] font-bold text-blue-200/50 uppercase tracking-widest">系统管理</div>

        <RouterLink to="/audit" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'text-gray-400 hover:bg-white/5'">
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-clipboard-text text-lg"></i>
            </div>
            <span class="text-sm font-medium" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">审计日志</span>
          </a>
        </RouterLink>

        <RouterLink to="/profile" custom v-slot="{ href, navigate, isActive }">
          <a :href="href" @click="navigate"
             class="flex items-center px-4 py-3.5 rounded-[20px] transition-all duration-300 group"
             :class="isActive ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'text-gray-400 hover:bg-white/5'">
            <div class="w-[30px] h-[30px] rounded-[12px] flex items-center justify-center mr-3 transition-colors"
                 :class="isActive ? 'text-white' : 'bg-white/5 text-blue-400 group-hover:text-white group-hover:bg-blue-500'">
              <i class="ph-fill ph-user-gear text-lg"></i>
            </div>
            <span class="text-sm font-medium" :class="isActive ? 'text-white' : 'text-gray-400 group-hover:text-white'">个人中心</span>
          </a>
        </RouterLink>

        <a href="#" @click.prevent="handleLogout"
           class="flex items-center px-4 py-3.5 rounded-[20px] hover:bg-red-500/10 transition-all duration-300 group mt-auto text-gray-400">
            <div class="w-[30px] h-[30px] rounded-[12px] bg-white/5 text-red-400 group-hover:bg-red-500 group-hover:text-white flex items-center justify-center mr-3 transition-colors">
              <i class="ph-fill ph-sign-out text-lg"></i>
            </div>
            <span class="text-sm font-medium text-gray-400 group-hover:text-red-300">退出登录</span>
        </a>

      </nav>
    </aside>

    <main class="flex-1 ml-[290px] p-5 h-screen flex flex-col overflow-hidden relative">
      <div class="absolute top-0 left-0 w-full h-[300px] bg-gradient-to-b from-blue-500/10 to-transparent pointer-events-none"></div>

      <header class="flex justify-between items-center mb-6 pt-1 shrink-0 relative z-10">
        <div>
          <nav class="flex items-center text-xs text-blue-200/60 mb-1">
            <i class="ph-fill ph-house mr-2"></i>
            <span>/</span>
            <span class="mx-2 text-white font-medium">{{ pageTitle }}</span>
          </nav>
          <h6 class="font-bold text-white text-lg tracking-tight">{{ pageTitle }}</h6>
        </div>

        <div class="flex items-center gap-4">
          <button class="flex items-center gap-3 pl-2">
            <div class="text-right hidden md:block">
              <div class="text-sm font-bold text-white">{{ currentAdminName }}</div>
              <div class="text-[10px] text-blue-200/60">Super Admin</div>
            </div>
            <div class="w-9 h-9 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 p-[1px]">
               <div class="w-full h-full rounded-full bg-[#0f172a] flex items-center justify-center">
                 <i class="ph-fill ph-user text-white text-sm"></i>
               </div>
            </div>
          </button>
        </div>
      </header>

      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
           <component :is="Component" />
        </transition>
      </RouterView>

    </main>
  </div>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 0px;
}
/* 简单的页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
