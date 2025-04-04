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
              <form @submit.prevent="handleUserIdSubmit" class="needs-validation" v-if="!otpSent">
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
                    :disabled="isProcessing"
                  >
                    <span v-if="isProcessing" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ isProcessing ? 'Sending OTP...' : 'Continue' }}
                  </button>
                </div>
              </form>
              
              <!-- OTP Verification Form -->
              <form @submit.prevent="verifyOtp" class="needs-validation" v-if="otpSent">
                <div class="text-center mb-3">
                  <p>A verification code has been sent to <strong>{{ maskedPhone }}</strong></p>
                </div>
                
                <div class="mb-4">
                  <label for="otp" class="form-label">Enter Verification Code</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-shield-lock"></i>
                    </span>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="otp" 
                      v-model="otp"
                      :class="{ 'is-invalid': validationErrors.otp }"
                      placeholder="Enter 6-digit code"
                      maxlength="6"
                      required
                    >
                    <div v-if="validationErrors.otp" class="invalid-feedback">
                      {{ validationErrors.otp }}
                    </div>
                  </div>
                  <div class="d-flex justify-content-between mt-2">
                    <small class="text-muted">Didn't receive code?</small>
                    <button 
                      type="button" 
                      class="btn btn-link btn-sm p-0" 
                      @click="resendOtp"
                      :disabled="resendCooldown > 0"
                    >
                      {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend Code' }}
                    </button>
                  </div>
                </div>
                
                <div class="d-grid gap-2">
                  <button 
                    type="submit" 
                    class="btn btn-primary btn-lg"
                    :disabled="isVerifying"
                  >
                    <span v-if="isVerifying" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    {{ isVerifying ? 'Verifying...' : 'Verify & Sign In' }}
                  </button>
                  
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary"
                    @click="cancelOtpVerification"
                  >
                    Back
                  </button>
                </div>
              </form>
              
              <!-- Demo Accounts -->
              <div class="mt-4" v-if="!otpSent">
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
const API_URL = 'http://localhost:5001';
// OTP API from OutSystems
const OTP_API_URL = 'http://localhost:5001/generate-otp';

export default {
  name: 'LoginPage',
  data() {
    return {
      uid: '',
      otp: '',
      generatedOtp: '', // Store the generated OTP
      userPhone: '', // Store the retrieved phone number
      maskedPhone: '', // For display purposes
      rememberMe: false,
      isProcessing: false,
      isVerifying: false,
      otpSent: false,
      errorMessage: '',
      successMessage: '',
      validationErrors: {},
      resendCooldown: 0,
      cooldownInterval: null,
      demoAccounts: [
        { uid: '12345678', name: 'user1' },
        { uid: '22345678', name: 'user2' },
        { uid: '32345678', name: 'user3' }
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
    validateUserId() {
      this.validationErrors = {};
      let isValid = true;
      
      // Validate user ID
      if (!this.uid.trim()) {
        this.validationErrors.uid = 'User ID is required';
        isValid = false;
      }
      
      return isValid;
    },
    validateOtp() {
      this.validationErrors = {};
      let isValid = true;
      
      // Validate OTP
      if (!this.otp.trim()) {
        this.validationErrors.otp = 'Verification code is required';
        isValid = false;
      } else if (this.otp.length !== 6 || !/^\d+$/.test(this.otp)) {
        this.validationErrors.otp = 'Please enter a valid 6-digit code';
        isValid = false;
      }
      
      return isValid;
    },
    async handleUserIdSubmit() {
      // Clear previous messages
      this.errorMessage = '';
      this.successMessage = '';
      
      // Validate form
      if (!this.validateUserId()) {
        return;
      }
      
      // Set loading state
      this.isProcessing = true;
      
      try {
        // Call API to verify user ID and get phone number
        const response = await axios.post(`${API_URL}/verify-user`, {
          uid: this.uid
        });
        
        if (response.data.code === 200) {
          // Store the user's phone number
          this.userPhone = response.data.data.phone;
          
          // Create masked version of phone number for display
          this.maskedPhone = this.maskPhoneNumber(this.userPhone);
          
          // Generate and send OTP
          await this.generateAndSendOtp();
          
          // Move to OTP verification step
          this.otpSent = true;
          this.successMessage = 'Verification code sent successfully!';
        } else {
          this.errorMessage = response.data.message || 'Failed to verify user ID';
        }
      } catch (error) {
        // Handle errors
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.message || 'User verification failed. Please try again.';
        } else {
          this.errorMessage = 'Network error. Please check your connection.';
        }
      } finally {
        // Reset loading state
        this.isProcessing = false;
      }
    },
    async generateAndSendOtp() {
      try {
        console.log("Generating OTP...");
        // Call your backend proxy instead
        const otpResponse = await axios.get(OTP_API_URL);
        console.log("OTP response:", otpResponse);
        
        if (otpResponse.data && otpResponse.data.OTP) {
          // Store the generated OTP
          this.generatedOtp = otpResponse.data.OTP;
          
          console.log("Sending OTP...");
          // Call backend to send OTP via AWS SNS
          await axios.post(`${API_URL}/send-otp`, {
            phone: this.userPhone,
            otp: this.generatedOtp
          });
          
          // Start the resend cooldown
          this.startResendCooldown();
          
          return true;
        } else {
          console.error("Invalid OTP response:", otpResponse);
          throw new Error("Invalid OTP response from server");
        }
      } catch (error) {
        console.error("Error generating/sending OTP:", error);
        this.errorMessage = "Failed to send verification code. Please try again.";
        return false;
      }
    },
    async verifyOtp() {
      // Clear previous messages
      this.errorMessage = '';
      this.successMessage = '';
      
      // Validate OTP
      if (!this.validateOtp()) {
        return;
      }
      
      // Set loading state
      this.isVerifying = true;
      
      try {
        console.log(`Verifying OTP: ${this.otp} for user ${this.uid}`);
        
        // Call API to verify OTP
        const response = await axios.post(`${API_URL}/verify-otp`, {
          uid: this.uid,
          otp: this.otp
        });
        
        console.log("Verification response:", response);
        
        if (response.data.code === 200) {
          // OTP verified successfully
          this.successMessage = 'Verification successful! Logging in...';
          
          // If remember me is checked, store the user ID
          if (this.rememberMe) {
            localStorage.setItem('rememberedUid', this.uid);
          } else {
            localStorage.removeItem('rememberedUid');
          }
          
          // Redirect to home page after a short delay
          setTimeout(() => {
            this.$router.push('/home');
          }, 1000);
        } else {
          this.errorMessage = response.data.message || 'Verification failed. Please try again.';
        }
      } catch (error) {
        // Handle errors
        console.error("Error verifying OTP:", error);
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.message || 'Verification failed. Please try again.';
        } else {
          this.errorMessage = 'Network error. Please check your connection.';
        }
      } finally {
        // Reset loading state
        this.isVerifying = false;
      }
    },
    async resendOtp() {
      // Clear previous messages
      this.errorMessage = '';
      this.successMessage = '';
      
      // Set loading state
      this.isProcessing = true;
      
      // Generate and send new OTP
      const success = await this.generateAndSendOtp();
      
      if (success) {
        this.successMessage = 'Verification code resent successfully!';
      }
      
      // Reset loading state
      this.isProcessing = false;
    },
    startResendCooldown() {
      // Set initial cooldown time (60 seconds)
      this.resendCooldown = 60;
      
      // Clear any existing interval
      if (this.cooldownInterval) {
        clearInterval(this.cooldownInterval);
      }
      
      // Start countdown
      this.cooldownInterval = setInterval(() => {
        if (this.resendCooldown > 0) {
          this.resendCooldown--;
        } else {
          // Stop the interval when countdown reaches 0
          clearInterval(this.cooldownInterval);
        }
      }, 1000);
    },
    cancelOtpVerification() {
      // Clear OTP related data
      this.otp = '';
      this.otpSent = false;
      this.generatedOtp = '';
      
      // Clear any error/success messages
      this.errorMessage = '';
      this.successMessage = '';
      
      // Clear the cooldown interval
      if (this.cooldownInterval) {
        clearInterval(this.cooldownInterval);
        this.resendCooldown = 0;
      }
    },
    maskPhoneNumber(phone) {
      if (!phone || phone.length < 8) return '***-***-****';
      
      // Keep last 4 digits visible, mask the rest
      return '***-***-' + phone.slice(-4);
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
  },
  beforeUnmount() {
    // Clear interval when component is destroyed
    if (this.cooldownInterval) {
      clearInterval(this.cooldownInterval);
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