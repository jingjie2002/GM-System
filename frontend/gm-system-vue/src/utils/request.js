import axios from 'axios'

// 1. 创建 Axios 实例
const service = axios.create({
    // 这里的 baseURL 必须和 vite.config.js 里的代理路径一致
    baseURL: '/api',
    timeout: 5000 // 请求超时时间
})

// 2. 请求拦截器：每次发请求前，自动把 Token 塞进 Header 里
service.interceptors.request.use(
    config => {
        // 从本地存储或会话存储获取 access_token
        const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
        if (token) {
            // 后端使用的是 SimpleJWT，必须带上 Bearer 前缀
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// 3. 响应拦截器：统一处理后端返回的错误
service.interceptors.response.use(
    response => {
        // 直接返回数据部分，这样你在组件里就不用多写一份 .data 了
        return response.data
    },
    error => {
        console.error('请求出错：', error)

        // 如果后端返回 401，说明 Token 过期或无效，直接跳回登录页
        if (error.response && error.response.status === 401) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('username')
            sessionStorage.removeItem('access_token')
            sessionStorage.removeItem('refresh_token')
            sessionStorage.removeItem('username')
            window.location.href = '/login'
        }

        return Promise.reject(error)
    }
)

export default service
