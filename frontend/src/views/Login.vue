<template>
  <div class="login-page">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="login-card card mt-5">
            <div class="card-body p-4 p-md-5">
              <div class="text-center mb-4">
                <h2 class="brand-name">DealShare</h2>
                <p class="text-muted">Sign in to continue</p>
              </div>
              
              <!-- Alert Messages -->
              <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ errorMessage }}
                <button @click="errorMessage = ''" type="button" class="btn-close" aria-label="Close"></button>
              </div>
              
              <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                {{ successMessage }}
                <button @click="successMessage = ''" type="button" class="btn-close" aria-label="Close"></button>
              </div>
              
              <!-- Login Form -->
              <form @submit.prevent="handleLogin" class="needs-validation">
                <div class="mb-3">
                  <label for="uid" class="form-label">User ID</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-person"></i>
                    </span>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="uid" 
                      v-model="uid"
                      :class="{ 'is-invalid': validationErrors.uid }"
                      placeholder="Enter your user ID"
                      required
                    >
                    <div v-if="validationErrors.uid" class="invalid-feedback">
                      {{ validationErrors.uid }}
                    </div>
                  </div>
                </div>
                
                <div class="form-check mb-3">
                  <input type="checkbox" class="form-check-input" id="rememberMe" v-model="rememberMe">
                  <label class="form-check-label" for="rememberMe">Remember me</label>
                </div>
                
                <div class="d-grid">
                  <button 
                    type="submit" 
                    class="btn btn-primary btn-lg"
                    :disabled="isLoggingIn"
                  >
                    <span v-if="isLoggingIn" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ isLoggingIn ? 'Signing In...' : 'Sign In' }}
                  </button>
                </div>
              </form>
              
              <!-- Demo Accounts -->
              <div class="mt-4">
                <div class="separator text-center mb-3">
                  <span class="separator-text">Demo Accounts</span>
                </div>
                
                <div class="demo-accounts">
                  <div class="list-group">
                    <button 
                      v-for="account in demoAccounts" 
                      :key="account.uid" 
                      @click="fillDemoAccount(account.uid)"
                      type="button" 
                      class="list-group-item list-group-item-action"
                    >
                      <div class="d-flex w-100 justify-content-between align-items-center">
                        <div>
                          <h6 class="mb-1">{{ account.name }}</h6>
                          <p class="mb-0 small text-muted">ID: {{ account.uid }}</p>
                        </div>
                        <span class="badge bg-primary rounded-pill">Use</span>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
axios.defaults.withCredentials = true;  // Enable sending cookies

// API base URL - update this to match your Flask backend
const API_URL = 'http://localhost:8000';

export default {
  name: 'LoginPage',
  data() {
    return {
      uid: '',
      rememberMe: false,
      isLoggingIn: false,
      errorMessage: '',
      successMessage: '',
      validationErrors: {},
      demoAccounts: [
        { uid: '12345678', name: 'user1' },
        { uid: '22345678', name: 'user2' },
        { uid: '32345678', name: 'user3' },
        { uid: '42345678', name: 'user4' }
      ]
    };
  },
  created() {
    // Check if user is already logged in
    this.checkAuthStatus();
  },
  methods: {
    async checkAuthStatus() {
      try {
        const response = await axios.get(`${API_URL}/check-auth`, { withCredentials: true });
        if (response.data.code === 200 && response.data.data.authenticated) {
          // User is already logged in, redirect to home
          this.$router.push('/');
        }
      } catch (error) {
        // Not logged in, stay on login page
        console.log('Not logged in');
      }
    },
    validateForm() {
      this.validationErrors = {};
      let isValid = true;
      
      // Validate user ID
      if (!this.uid.trim()) {
        this.validationErrors.uid = 'User ID is required';
        isValid = false;
      }
      
      return isValid;
    },
    async handleLogin() {
      // Clear previous messages
      this.errorMessage = '';
      this.successMessage = '';
      
      // Validate form
      if (!this.validateForm()) {
        return;
      }
      
      // Set loading state
      this.isLoggingIn = true;
      
      try {
        // Call login API with credentials
        const response = await axios.post(`${API_URL}/login`, {
          uid: this.uid
        }, {
          withCredentials: true // Important for cookies to work
        });
        if (response.data.code === 200) {
          // Successful login
          this.successMessage = 'Login successful! Redirecting...';
          localStorage.setItem('uid', this.uid);
          
          // If remember me is checked, store the user ID (Optional)
          if (this.rememberMe) {
            localStorage.setItem('rememberedUid', this.uid);
          } else {
            localStorage.removeItem('rememberedUid');
          }
          
          // Redirect to home page after a short delay
          setTimeout(() => {
            this.$router.push('/home');
          }, 1000);
        }
      } catch (error) {
        // Handle login errors
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.message || 'Login failed. Please try again.';
        } else {
          console.log(error.response)
          this.errorMessage = 'Network error. Please check your connection.';
        }
      } finally {
        // Reset loading state
        this.isLoggingIn = false;
      }
    },
    fillDemoAccount(uid) {
      this.uid = uid;
    }
  },
  mounted() {
    // Check if there's a remembered user ID
    const rememberedUid = localStorage.getItem('rememberedUid');
    if (rememberedUid) {
      this.uid = rememberedUid;
      this.rememberMe = true;
    }
  }
};
</script>

<style scoped>
.login-page {
  background-color: #f8f9fa;
  min-height: 100vh;
  display: flex;
  align-items: center;
}

.login-card {
  border-radius: 10px;
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.brand-name {
  font-weight: 700;
  color: #007bff;
  margin-bottom: 5px;
}

.separator {
  display: flex;
  align-items: center;
  text-align: center;
  color: #6c757d;
}

.separator::before,
.separator::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #dee2e6;
}

.separator-text {
  padding: 0 0.75rem;
}

/* Custom styling for input group focus */
.input-group:focus-within {
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
  border-radius: 0.375rem;
}

.input-group:focus-within .input-group-text,
.input-group:focus-within .form-control {
  border-color: #86b7fe;
}

.input-group .form-control:focus {
  box-shadow: none;
}

.demo-accounts .list-group-item {
  cursor: pointer;
  transition: all 0.2s;
}

.demo-accounts .list-group-item:hover {
  background-color: #f8f9fa;
}
</style>