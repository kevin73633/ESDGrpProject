// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import axios from 'axios';
import Home from '../views/Home.vue';
import DealDetails from '../views/DealDetails.vue';
import Chat from '../views/Chat.vue';
import Profile from '../views/Profile.vue';
import OtherProfile from '../views/OtherProfile.vue';
import Login from '../views/Login.vue';

const routes = [
  {
    path: '/',
    redirect: '/login' // Redirect root path to login
  },
  {
    path: '/home',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/product/:id',
    name: 'dealDetails',
    component: DealDetails,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/otherprofile/:id',
    name: 'OtherProfile',
    component: OtherProfile,
    meta: { requiresAuth: true }
  },
  // Catch-all redirect to login
  {
    path: '/:catchAll(.*)',
    redirect: '/login'
  }
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation guard
router.beforeEach(async (to, from, next) => {
  // Allow direct access to login page
  if (to.path === '/login') {
    next();
    return;
  }
  
  // Check authentication for all other routes
  try {
    const response = await axios.get('http://localhost:5001/check-auth', { 
      withCredentials: true 
    });
    
    if (response.data.code === 200 && response.data.data.authenticated) {
      // User is authenticated
      next();
    } else {
      // Not authenticated, redirect to login
      next('/login');
    }
  } catch (error) {
    // Error or not authenticated, redirect to login
    next('/login');
  }
});

export default router;