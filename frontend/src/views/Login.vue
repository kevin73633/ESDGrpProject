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
                  <label for="email" class="form-label">Email address</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input 
                      type="email" 
                      class="form-control" 
                      id="email" 
                      v-model="email"
                      :class="{ 'is-invalid': validationErrors.email }"
                      placeholder="Enter your email"
                      required
                    >
                    <div v-if="validationErrors.email" class="invalid-feedback">
                      {{ validationErrors.email }}
                    </div>
                  </div>
                </div>
                
                <div class="mb-3">
                  <div class="d-flex justify-content-between align-items-center">
                    <label for="password" class="form-label">Password</label>
                    <a href="#" class="small text-decoration-none" @click.prevent="showForgotPasswordModal">Forgot password?</a>
                  </div>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input 
                      :type="showPassword ? 'text' : 'password'" 
                      class="form-control" 
                      id="password" 
                      v-model="password"
                      :class="{ 'is-invalid': validationErrors.password }"
                      placeholder="Enter your password"
                      required
                    >
                    <button 
                      class="input-group-text bg-transparent border-start-0" 
                      type="button"
                      @click="showPassword = !showPassword"
                    >
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div v-if="validationErrors.password" class="invalid-feedback">
                      {{ validationErrors.password }}
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
              
              <!-- Social Login -->
              <div class="social-login mt-4">
                <div class="separator text-center mb-3">
                  <span class="separator-text">or sign in with</span>
                </div>
                
                <div class="d-flex justify-content-center gap-2">
                  <button @click="socialLogin('google')" class="btn btn-outline-secondary social-btn">
                    <i class="bi bi-google"></i>
                  </button>
                  <button @click="socialLogin('facebook')" class="btn btn-outline-secondary social-btn">
                    <i class="bi bi-facebook"></i>
                  </button>
                  <button @click="socialLogin('apple')" class="btn btn-outline-secondary social-btn">
                    <i class="bi bi-apple"></i>
                  </button>
                </div>
              </div>
              
              <!-- Sign Up Link -->
              <div class="text-center mt-4">
                <p class="mb-0">
                  Don't have an account? 
                  <router-link to="/register" class="text-decoration-none">Create an account</router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Forgot Password Modal -->
    <div class="modal fade" id="forgotPasswordModal" tabindex="-1" ref="forgotPasswordModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reset Your Password</h5>
            <button type="button" class="btn-close" @click="closeForgotPasswordModal"></button>
          </div>
          <div class="modal-body">
            <p>Enter your email address and we'll send you instructions to reset your password.</p>
            <form @submit.prevent="handleForgotPassword">
              <div class="mb-3">
                <label for="resetEmail" class="form-label">Email Address</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-envelope"></i>
                  </span>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="resetEmail" 
                    v-model="resetEmail"
                    placeholder="Enter your email"
                    required
                  >
                </div>
              </div>
              <div class="d-grid">
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="isResetting"
                >
                  <span v-if="isResetting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ isResetting ? 'Sending...' : 'Send Reset Link' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';

export default {
  name: 'LoginPage',
  data() {
    return {
      email: '',
      password: '',
      rememberMe: false,
      showPassword: false,
      isLoggingIn: false,
      errorMessage: '',
      successMessage: '',
      validationErrors: {},
      resetEmail: '',
      isResetting: false,
      forgotPasswordModal: null
    };
  },
  mounted() {
    // Initialize modals
    if (this.$refs.forgotPasswordModal) {
      this.forgotPasswordModal = new Modal(this.$refs.forgotPasswordModal);
    }
  },
  methods: {
    validateForm() {
      this.validationErrors = {};
      let isValid = true;
      
      // Validate email
      if (!this.email.trim()) {
        this.validationErrors.email = 'Email is required';
        isValid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {
        this.validationErrors.email = 'Please enter a valid email address';
        isValid = false;
      }
      
      // Validate password
      if (!this.password) {
        this.validationErrors.password = 'Password is required';
        isValid = false;
      } else if (this.password.length < 6) {
        this.validationErrors.password = 'Password must be at least 6 characters';
        isValid = false;
      }
      
      return isValid;
    },
    handleLogin() {
      // Clear previous messages
      this.errorMessage = '';
      this.successMessage = '';
      
      // Validate form
      if (!this.validateForm()) {
        return;
      }
      
      // Set loading state
      this.isLoggingIn = true;
      
      // In a real app, you would call your authentication API here
      // Simulating API call with timeout
      setTimeout(() => {
        // Check credentials (this is just for demo purposes)
        if (this.email === 'demo@example.com' && this.password === 'password123') {
          // Successful login
          this.successMessage = 'Login successful! Redirecting...';
          
          // In a real app, you would store the token and redirect to dashboard
          setTimeout(() => {
            this.$router.push('/');
          }, 1500);
        } else {
          // Failed login
          this.errorMessage = 'Invalid email or password. Please try again.';
        }
        
        // Reset loading state
        this.isLoggingIn = false;
      }, 1500);
    },
    socialLogin(provider) {
      // In a real app, you would implement OAuth flows for each provider
      this.successMessage = `Logging in with ${provider}...`;
      
      // Simulate loading and redirection
      setTimeout(() => {
        this.$router.push('/');
      }, 1500);
    },
    showForgotPasswordModal() {
      if (this.forgotPasswordModal) {
        this.resetEmail = this.email; // Pre-fill with the email from login form
        this.forgotPasswordModal.show();
      }
    },
    closeForgotPasswordModal() {
      if (this.forgotPasswordModal) {
        this.forgotPasswordModal.hide();
      }
    },
    handleForgotPassword() {
      // Validate email
      if (!this.resetEmail.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.resetEmail)) {
        alert('Please enter a valid email address');
        return;
      }
      
      // Set loading state
      this.isResetting = true;
      
      // In a real app, you would call your password reset API here
      // Simulating API call with timeout
      setTimeout(() => {
        // Show success message
        this.closeForgotPasswordModal();
        this.successMessage = 'Password reset link has been sent to your email';
        
        // Reset state
        this.isResetting = false;
        this.resetEmail = '';
      }, 1500);
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

.social-btn {
  width: 45px;
  height: 45px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  font-size: 1.2rem;
}

.social-btn:hover {
  background-color: #f1f3f5;
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

/* Remove shadow from eye button when password field is focused */
.input-group:focus-within .bg-transparent {
  box-shadow: none;
}
</style>