import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/',
      component: MainLayout,
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue')
        },
        // 🟢 新增：财务账单页面
        // 🟢 如果你想把“数据报表”也指向这里，可以加这个：
        {
          path: 'tables',
          name: 'tables',
          // 暂时重定向到 billing，或者你以后有了 TablesView 再改
          redirect: '/billing'
        },
        {
          path: 'players',
          name: 'players',
          component: () => import('../views/PlayerListView.vue')
        },
        {
          path: 'mails',
          name: 'mails',
          component: () => import('../views/MailManagement.vue')
        },
        {
          path: 'notices',
          name: 'notices',
          component: () => import('../views/NoticeManagement.vue')
        },
        {
          path: 'cdks',
          name: 'cdks',
          component: () => import('../views/CdkManagement.vue')
        },
        {
          path: 'audit',
          name: 'audit',
          component: () => import('../views/AuditLogView.vue')
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('../views/ProfileView.vue')
        },

      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  if (to.name !== 'login' && !token) {
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
