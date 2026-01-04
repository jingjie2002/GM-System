<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)

// 定义表单数据
const loginForm = reactive({
  username: '',
  password: '',
  rememberMe: false
})

// 登录逻辑
const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    alert('请输入账号和密码')
    return
  }

  loading.value = true
  try {
    const res = await request.post('/token/', {
      username: loginForm.username,
      password: loginForm.password
    })
    const data = res.data || res

    if (data.access) {
      if (loginForm.rememberMe) {
        // 保持登录：存入 localStorage
        localStorage.setItem('access_token', data.access)
        localStorage.setItem('refresh_token', data.refresh)
        localStorage.setItem('username', loginForm.username)
        // 清理 session 以免混淆
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('refresh_token')
        sessionStorage.removeItem('username')
      } else {
        // 不保持登录：存入 sessionStorage
        sessionStorage.setItem('access_token', data.access)
        sessionStorage.setItem('refresh_token', data.refresh)
        sessionStorage.setItem('username', loginForm.username)
        // 清理 local 以免混淆
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('username')
      }
      
      router.push('/dashboard')
    } else {
      alert('登录失败: 未获取到有效的 Token')
    }
  } catch (err) {
    console.error(err)
    const msg = err.response?.data?.detail || '登录失败，请检查账号密码'
    alert(msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#0b0e1f] flex items-center justify-center p-4 font-sans text-white overflow-hidden relative">

    <div class="absolute top-8 left-8 z-20">
      <a href="#" class="text-sm font-bold tracking-[2px] uppercase text-white hover:opacity-80 transition flex items-center gap-2">
        <i class="ph-fill ph-game-controller text-blue-500 text-lg"></i>
        GM ADMIN SYSTEM
      </a>
    </div>

    <div class="flex w-full max-w-[1200px] h-[85vh] gap-6">

      <div class="hidden xl:flex flex-1 relative rounded-[24px] overflow-hidden items-center justify-center">
        <div class="absolute inset-0 z-0">
          <img src="../img/submit.png" class="w-full h-full object-cover" alt="Background" onerror="this.style.display='none'; this.parentNode.style.background='linear-gradient(135deg, #060b28 0%, #1a1f37 100%)'" />
          <div class="absolute inset-0 bg-[#060b28]/80 mix-blend-multiply"></div>
          <div class="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-blue-600/20 to-purple-600/20 mix-blend-overlay"></div>
        </div>

        <div class="relative z-10 text-center px-10">
          <div class="w-20 h-20 border-2 border-white/20 rounded-full flex items-center justify-center mx-auto mb-8 bg-white/5 backdrop-blur-sm shadow-[0_0_20px_rgba(0,118,255,0.3)]">
             <i class="ph-duotone ph-shield-check text-3xl text-white"></i>
          </div>
          <p class="text-white/80 text-xs font-bold tracking-[4px] uppercase mb-4">Professional & Secure</p>
          <h1 class="text-4xl font-bold leading-tight tracking-wide text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70">
            GAME MANAGEMENT<br>SYSTEM
          </h1>
          <p class="mt-6 text-white/40 text-sm max-w-md mx-auto leading-relaxed">
            专为游戏运营打造的高效管理平台。<br>资产审计 · 邮件分发 · 玩家管理
          </p>
        </div>
      </div>

      <div class="flex-1 flex flex-col items-center justify-center relative">

        <div class="text-center mb-10">
          <h2 class="text-3xl font-bold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
            欢迎回来!
          </h2>
          <p class="text-gray-400 text-sm font-medium">请登录您的管理员账号</p>
        </div>

        <div class="w-full max-w-[400px] bg-[#161b3b]/60 backdrop-blur-2xl border border-white/5 rounded-[24px] p-10 shadow-2xl relative overflow-hidden group">
          <div class="absolute top-0 left-1/2 -translate-x-1/2 w-1/2 h-1 bg-blue-500/50 blur-[20px] group-hover:bg-blue-400/80 transition-all duration-500"></div>

          <form @submit.prevent="handleLogin" class="space-y-6">

            <div class="space-y-2">
              <label class="text-xs font-bold ml-1 text-white">账号</label>
              <div class="relative">
                <input
                  v-model="loginForm.username"
                  type="text"
                  placeholder="请输入管理员账号"
                  class="w-full bg-[#0f1535] border border-white/10 rounded-[16px] px-5 py-3.5 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  required
                />
              </div>
            </div>

            <div class="space-y-2">
              <label class="text-xs font-bold ml-1 text-white">密码</label>
              <div class="relative">
                <input
                  v-model="loginForm.password"
                  type="password"
                  placeholder="请输入密码"
                  class="w-full bg-[#0f1535] border border-white/10 rounded-[16px] px-5 py-3.5 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  required
                />
              </div>
            </div>

            <div class="flex items-center pl-1">
              <label class="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" v-model="loginForm.rememberMe" class="sr-only peer">
                <div class="w-9 h-5 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                <span class="ml-3 text-sm font-medium text-gray-400">保持登录状态</span>
              </label>
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-[#0075ff] hover:bg-[#0061d5] disabled:bg-blue-800 disabled:cursor-not-allowed text-white font-bold py-3.5 rounded-[16px] text-sm tracking-wide transition-all shadow-[0_4px_14px_0_rgba(0,118,255,0.39)] hover:shadow-[0_6px_20px_rgba(0,118,255,0.23)] hover:-translate-y-[1px]"
            >
              {{ loading ? '正在验证...' : '立即登录' }}
            </button>

          </form>
        </div>

        <div class="mt-8 text-center">
          <p class="text-gray-500 text-[10px] uppercase tracking-wider">
            © 2026 Game Management System. All Rights Reserved.
          </p>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

.font-sans {
  font-family: 'Plus Jakarta Sans', sans-serif;
}
</style>
