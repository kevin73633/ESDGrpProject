// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import DealDetails from '../views/DealDetails.vue';
import Chat from '../views/Chat.vue';
import Profile from '../views/Profile.vue';
import Login from '../views/Login.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/deal/:id',
    name: 'DealDetails',
    component: DealDetails,
    props: true, // This allows you to pass the :id parameter as a prop to the component
  },
  {
    path: '/chat/:dealId',
    name: 'Chat',
    component: Chat,
    props: true,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
