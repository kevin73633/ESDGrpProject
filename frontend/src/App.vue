<template>
  <div id="app">
    <!-- Vertical Navbar -->
    <div class="sidebar">
      <ul>
        <li><router-link to="/home">Home</router-link></li>
        <li><router-link to="/chat">Chats</router-link></li>
        <li><router-link to="/profile">Profile</router-link></li>
        <li v-if="!isAuthenticated"><router-link to="/login">Login</router-link></li>
        <li v-else>
          <a href="#" @click.prevent="signOut" class="sign-out-link">
            <i class="fas fa-sign-out-alt"></i> Sign Out
          </a>
        </li>
      </ul>
    </div>
    
    <!-- Main content area -->
    <div class="main-content">
      <router-view /> <!-- This renders the component matching the route -->
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      isAuthenticated: false
    };
  },
  methods: {
    async checkAuthStatus() {
      try {
        const response = await axios.get('http://localhost:8000/check-auth', { 
          withCredentials: true 
        });
        
        this.isAuthenticated = response.data.code === 200 && response.data.data.authenticated;
      } catch (error) {
        console.error("Error checking auth status:", error);
        this.isAuthenticated = false;
      }
    },
    
    async signOut() {
      try {
        // Call the backend logout endpoint
        await axios.post('http://localhost:8000/logout', {}, { 
          withCredentials: true 
        });
        
        // Update authentication status
        this.isAuthenticated = false;
        
        // Redirect to login page
        this.$router.push('/login');
      } catch (error) {
        console.error("Error signing out:", error);
        
        // Even if there's an error, still log out on the client side
        this.isAuthenticated = false;
        this.$router.push('/login');
      }
    }
  },
  created() {
    // Check authentication status when component is created
    this.checkAuthStatus();
    
    // Listen for route changes to update authentication status
    this.$router.beforeEach((to, from, next) => {
      this.checkAuthStatus();
      next();
    });
  }
};
</script>

<style scoped>
#app {
  display: flex;
  height: 100vh; /* Full height */
}

.sidebar {
  width: 250px;
  background-color: #333;
  color: white;
  padding: 20px;
  position: fixed;
  height: 100%;
}

.sidebar ul {
  list-style-type: none;
  padding: 0;
}

.sidebar ul li {
  margin: 20px 0;
}

.sidebar ul li a {
  color: white;
  text-decoration: none;
  font-size: 18px;
  display: block;
}

.sidebar ul li a:hover {
  background-color: #575757;
  padding-left: 10px;
  transition: 0.3s;
}

.sidebar ul li a.router-link-active {
  color: #4CAF50; /* Active link color */
}

.sign-out-link {
  cursor: pointer;
}

.sign-out-link:hover {
  color: #ff6b6b; /* Red hover color for sign out */
}

.main-content {
  margin-left: 250px; /* Space to accommodate the sidebar */
  padding: 20px;
  width: 100%;
}
</style>