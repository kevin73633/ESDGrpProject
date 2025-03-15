<template>
  <div id="app">
    <!-- Vertical Navbar -->
    <div class="sidebar">
      <ul>
        <li><router-link to="/">Home</router-link></li>
        <li><router-link to="/chat">Chats</router-link></li>
        <li><router-link to="/profile">Profile</router-link></li>
        <li><router-link to="/login">Login</router-link></li>
      </ul>
    </div>
    
    <!-- Main content area -->
    <div class="main-content">
      <router-view /> <!-- This renders the component matching the route -->
    </div>
  </div>
</template>

<script>

export default {
  name: 'App',
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
}

.sidebar ul li a:hover {
  background-color: #575757;
  padding-left: 10px;
  transition: 0.3s;
}

.sidebar ul li a.router-link-active {
  color: #4CAF50; /* Active link color */
}

.main-content {
  margin-left: 250px; /* Space to accommodate the sidebar */
  padding: 20px;
  width: 100%;
}
</style>
