<template>
  <div class="profile-page">
    <!-- Header with navigation -->
    <nav class="navbar navbar-light bg-light">
      <div class="container-fluid">
        <router-link to="/home" class="navbar-brand d-flex align-items-center">
          <button class="btn btn-link text-dark me-3 p-0" style="font-size: 1.5rem;">
             <i class="bi bi-arrow-left"></i>
            </button>
          <span>Back to Home</span>
        </router-link>
        <div class="d-flex">
          <button 
            @click="toggleEditMode" 
            class="btn" 
            :class="isEditing ? 'btn-success' : 'btn-outline-primary'"
          >
            <i :class="isEditing ? 'bi bi-floppy' : 'bi bi-pencil-square'" class="me-2"></i>
            {{ isEditing ? 'Save Changes' : 'Edit Profile' }}
          </button>
        </div>
      </div>
    </nav>
    
    <div class="container py-5">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2">Loading profile data...</p>
      </div>
      
      <div v-else-if="error" class="alert alert-danger" role="alert">
        <i class="bi bi-exclamation-triangle me-2"></i>
        {{ error }}
      </div>
      
      <div v-else class="row">
        <!-- Left Column: Profile Details -->
        <div class="col-lg-4">
          <div class="card mb-4">
            <div class="card-body text-center">
              <div class="position-relative d-inline-block mb-3">
                <img 
                  :src="user.avatar || '/api/placeholder/150/150'" 
                  alt="Profile Photo" 
                  class="rounded-circle img-fluid" 
                  style="width: 150px;"
                >
                <div v-if="isEditing" class="position-absolute bottom-0 end-0">
                  <label for="profilePhoto" class="btn btn-sm btn-primary rounded-circle">
                    <i class="bi bi-camera"></i>
                  </label>
                  <input 
                    type="file" 
                    id="profilePhoto" 
                    class="d-none" 
                    accept="image/*"
                    @change="handleProfilePhotoChange"
                  >
                </div>
              </div>
              <h5 class="my-3">{{ user.name }}</h5>

              <!-- User Ratings -->
              <div class="rating-summary text-center mt-3">
                <div class="d-flex align-items-center justify-content-center mb-2">
                  <span class="h3 mb-0 me-2">{{ user.rating || 0 }}</span>
                  <div>
                    <div class="stars-container">
                      <i 
                        v-for="star in 5" 
                        :key="star" 
                        :class="[
                          star <= Math.round(user.rating || 0) ? 'bi bi-star-fill text-warning' : 'bi bi-star text-muted'
                        ]"
                      ></i>
                    </div>
                    <div class="small text-muted">{{ userRatings.length || 0 }} ratings</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Contact Info Card -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Contact Information</h6>
              <span v-if="isEditing" class="text-primary small">
                <i class="bi bi-info-circle me-1"></i> Editing enabled
              </span>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="form-label small text-muted">Account Number</label>
                <div class="mb-0">{{ user.accnum }}</div>
              </div>
              
              <div class="mb-3">
                <label class="form-label small text-muted">Phone</label>
                <div v-if="!isEditing" class="mb-0">{{ user.phone || 'Not specified' }}</div>
                <input 
                  v-else 
                  type="tel" 
                  class="form-control" 
                  v-model="editedUser.phone"
                  :class="{ 'is-invalid': validationErrors.phone }" 
                >
                <div v-if="validationErrors.phone" class="invalid-feedback">
                  {{ validationErrors.phone }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Right Column: Account Details and Payments -->
        <div class="col-lg-8">
          <!-- Account Details -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Account Details</h6>
            </div>
            <div class="card-body">
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">Full Name</label>
                </div>
                <div class="col-sm-9">
                  <div v-if="!isEditing">{{ user.name }}</div>
                  <input 
                    v-else 
                    type="text" 
                    class="form-control" 
                    v-model="editedUser.name"
                    :class="{ 'is-invalid': validationErrors.name }" 
                  >
                  <div v-if="validationErrors.name" class="invalid-feedback">
                    {{ validationErrors.name }}
                  </div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">User ID</label>
                </div>
                <div class="col-sm-9">
                  <div>{{ user.uid }}</div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">Rating</label>
                </div>
                <div class="col-sm-9">
                  <div class="d-flex align-items-center">
                    <span>{{ user.rating }}</span>
                    <div class="stars-container ms-2">
                      <i 
                        v-for="star in 5" 
                        :key="star" 
                        :class="[
                          star <= Math.round(user.rating || 0) ? 'bi bi-star-fill text-warning' : 'bi bi-star text-muted'
                        ]"
                      ></i>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">Account Number</label>
                </div>
                <div class="col-sm-9">
                  <div>{{ user.accnum }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Payment Methods -->
          <div class="card mb-4">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h6 class="mb-0">Payment Methods</h6>
              <button 
                v-if="isEditing" 
                class="btn btn-sm btn-outline-primary"
                @click="addNewPaymentMethod"
              >
                <i class="bi bi-plus me-1"></i> Add New
              </button>
            </div>
            <div class="card-body">
              <div v-if="paymentMethods.length === 0" class="text-center py-4">
                <i class="bi bi-credit-card text-muted mb-3" style="font-size: 2rem;"></i>
                <p class="mb-0">No payment methods added yet.</p>
                <button 
                  v-if="isEditing" 
                  class="btn btn-primary mt-3"
                  @click="addNewPaymentMethod"
                >
                  <i class="bi bi-plus me-1"></i> Add Payment Method
                </button>
              </div>
              
              <div v-else>
                <div 
                  v-for="(method, index) in paymentMethods" 
                  :key="index"
                  class="payment-method mb-3 p-3 border rounded"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="d-flex align-items-center">
                      <div class="payment-icon me-3">
                        <i :class="getPaymentIcon(method.type)" class="fa-2x"></i>
                      </div>
                      <div>
                        <h6 class="mb-0">{{ getPaymentTypeLabel(method.type) }}</h6>
                        <p v-if="!isEditing" class="mb-0 text-muted small">
                          {{ method.type === 'card' ? `•••• •••• •••• ${method.lastFour}` : method.identifier }}
                        </p>
                        <div v-else>
                          <div v-if="method.type === 'card'" class="mt-2">
                            <input 
                              type="text" 
                              class="form-control mb-2" 
                              v-model="method.name"
                              placeholder="Card Name (e.g. Personal Visa)"
                            >
                            <div class="row">
                              <div class="col-md-6 mb-2">
                                <input 
                                  type="text" 
                                  class="form-control" 
                                  v-model="method.lastFour"
                                  placeholder="Last 4 digits"
                                  maxlength="4"
                                >
                              </div>
                              <div class="col-md-6 mb-2">
                                <input 
                                  type="text" 
                                  class="form-control" 
                                  v-model="method.expiryDate"
                                  placeholder="Expiry (MM/YY)"
                                >
                              </div>
                            </div>
                          </div>
                          <div v-else class="mt-2">
                            <input 
                              type="text" 
                              class="form-control" 
                              v-model="method.identifier"
                              :placeholder="method.type === 'paypal' ? 'PayPal Email' : 'Account ID'"
                            >
                          </div>
                        </div>
                      </div>
                    </div>
                    <div v-if="isEditing">
                      <button 
                        class="btn btn-sm btn-outline-danger"
                        @click="removePaymentMethod(index)"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>
                  <div v-if="!isEditing && method.default" class="mt-2">
                    <span class="badge bg-success">Default</span>
                  </div>
                  <div v-if="isEditing" class="form-check mt-2">
                    <input 
                      type="checkbox" 
                      class="form-check-input" 
                      :id="`defaultPayment-${index}`" 
                      v-model="method.default"
                      @change="setDefaultPayment(index)"
                    >
                    <label class="form-check-label" :for="`defaultPayment-${index}`">
                      Set as default payment method
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Activity History -->
          <div class="card mb-4">
            <div class="card-header">
              <h6 class="mb-0">Activity History</h6>
            </div>
            <div class="card-body">
              <p class="text-muted text-center py-4">
                <i class="bi bi-clock-history me-2"></i>
                Activity history will be displayed here
              </p>
            </div>
          </div>
          
          <!-- Ratings and Reviews -->
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Ratings & Reviews</h6>
            </div>
            <div class="card-body">
              <div v-if="userRatings.length === 0" class="text-center py-4">
                <i class="bi bi-star-fill text-muted mb-3" style="font-size: 2rem;"></i>
                <p class="mb-0">No ratings yet.</p>
              </div>
              
              <div v-else>
                <div class="rating-breakdown mb-4">
                  <h6 class="mb-3">Rating Breakdown</h6>
                  <div class="row">
                    <div 
                      v-for="star in 5" 
                      :key="star" 
                      class="col-12 mb-2"
                    >
                      <div class="d-flex align-items-center">
                        <div style="width: 60px;">{{ 6 - star }} stars</div>
                        <div class="progress flex-grow-1 mx-2" style="height: 8px;">
                          <div 
                            class="progress-bar bg-warning" 
                            :style="`width: ${getRatingPercentage(6 - star)}%`"
                          ></div>
                        </div>
                        <div style="width: 40px; text-align: right;">
                          {{ getRatingCount(6 - star) }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="ratings-list">
                  <h6 class="mb-3">Recent Reviews</h6>
                  <div 
                    v-for="(rating, index) in userRatings" 
                    :key="index"
                    class="review-item mb-3 pb-3"
                    :class="{'border-bottom': index < userRatings.length - 1}"
                  >
                    <div class="d-flex">
                      <img 
                        :src="rating.rater.avatar || '/api/placeholder/40/40'" 
                        class="rounded-circle me-3" 
                        alt="Reviewer" 
                        style="width: 40px; height: 40px;"
                      >
                      <div class="flex-grow-1">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                          <h6 class="mb-0">{{ rating.rater.name }}</h6>
                          <span class="text-muted small">{{ formatDate(rating.date) }}</span>
                        </div>
                        <div class="stars-container mb-2">
                          <i 
                            v-for="star in 5" 
                            :key="star" 
                            :class="[
                              star <= rating.stars ? 'bi bi-star-fill text-warning' : 'bi bi-star text-muted'
                            ]"
                          ></i>
                        </div>
                        <p class="mb-0">{{ rating.comment }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add Payment Method Modal -->
    <div class="modal fade" id="addPaymentModal" tabindex="-1" ref="paymentModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Payment Method</h5>
            <button type="button" class="btn-close" @click="closePaymentModal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Payment Type</label>
              <select v-model="newPayment.type" class="form-select">
                <option value="card">Credit/Debit Card</option>
                <option value="paypal">PayPal</option>
                <option value="bankAccount">Bank Account</option>
              </select>
            </div>
            
            <div v-if="newPayment.type === 'card'">
              <div class="mb-3">
                <label class="form-label">Card Name</label>
                <input type="text" class="form-control" v-model="newPayment.name" placeholder="e.g. Personal Visa">
              </div>
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Last 4 Digits</label>
                  <input type="text" class="form-control" v-model="newPayment.lastFour" maxlength="4" placeholder="1234">
                </div>
                <div class="col-md-6">
                  <label class="form-label">Expiry Date</label>
                  <input type="text" class="form-control" v-model="newPayment.expiryDate" placeholder="MM/YY">
                </div>
              </div>
            </div>
            
            <div v-else-if="newPayment.type === 'paypal'">
              <div class="mb-3">
                <label class="form-label">PayPal Email</label>
                <input type="email" class="form-control" v-model="newPayment.identifier" placeholder="you@example.com">
              </div>
            </div>
            
            <div v-else-if="newPayment.type === 'bankAccount'">
              <div class="mb-3">
                <label class="form-label">Bank Account Number</label>
                <input type="text" class="form-control" v-model="newPayment.identifier" placeholder="Last 4 digits of account">
              </div>
            </div>
            
            <div class="form-check mt-3">
              <input type="checkbox" class="form-check-input" id="makeDefault" v-model="newPayment.default">
              <label class="form-check-label" for="makeDefault">Make this my default payment method</label>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closePaymentModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveNewPaymentMethod">Save</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Success Toast -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div class="toast align-items-center text-white bg-success border-0" role="alert" aria-live="assertive" aria-atomic="true" ref="toast">
        <div class="d-flex">
          <div class="toast-body">
            <i class="bi bi-check-circle-fill me-2"></i>
            {{ toastMessage }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>

    <!-- Error Toast -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div class="toast align-items-center text-white bg-danger border-0" role="alert" aria-live="assertive" aria-atomic="true" ref="errorToast">
        <div class="d-flex">
          <div class="toast-body">
            <i class="bi bi-exclamation-circle-fill me-2"></i>
            {{ errorMessage }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal, Toast } from 'bootstrap';
import axios from 'axios';

// API URL base - should match your backend
const API_URL = 'http://localhost:5001';
const RATING_SERVICE_GET_URL = "https://personal-nzmfqiqp.outsystemscloud.com/RatingAPI_REST/rest/v1/userRating/RatedID/?RatedID=";

export default {
  name: 'ProfilePage',
  data() {
    return {
      loading: true,
      error: null,
      isEditing: false,
      user: {
        uid: '',
        name: '',
        rating: 0,
        accnum: '',
        phone: ''
      },
      editedUser: {}, // Will be populated with user data when editing starts
      validationErrors: {},
      userRatings: [],
      paymentMethods: [],
      newPayment: {
        type: 'card',
        name: '',
        lastFour: '',
        expiryDate: '',
        identifier: '',
        default: false
      },
      paymentModal: null,
      toastMessage: 'Profile updated successfully!',
      errorMessage: 'An error occurred. Please try again.',
      toast: null,
      errorToast: null
    };
  },
  computed: {
    currentUserId() {
      // Get the user ID from route params or from session/localStorage
      return this.$route.params.uid || localStorage.getItem('uid');
    },
    
    // Get top 3 recent reviews for display
    topReviews() {
      // First sort by date (newest first)
      const sortedRatings = [...this.userRatings].sort((a, b) => 
        new Date(b.date) - new Date(a.date)
      );
      
      // Return only the first 3
      return sortedRatings.slice(0, 3);
    }
  },
  methods: {
    // Fetch user profile data from API
    // Update the fetchUserProfile method to handle the new rating data format
    async fetchUserProfile() {
      this.loading = true;
      this.error = null;
      
      try {
        // First check if user is authenticated
        const authResponse = await axios.get(`${API_URL}/check-auth`, { withCredentials: true });
        
        if (authResponse.data.code === 200 && authResponse.data.data.authenticated) {
          // Use the currentUserId computed property to get the user ID
          const userId = this.currentUserId;
          
          if (!userId) {
            this.error = "No user ID provided";
            this.loading = false;
            return;
          }
          
          // If authenticated, fetch user profile
          const response = await axios.get(`${API_URL}/user/${userId}`, { withCredentials: true });
          
          if (response.data.code === 200) {
            this.user = response.data.data.user;
            
            // Make sure rating is a number
            this.user.rating = Number(this.user.rating) || 0;
            
            // Also fetch phone number if not included in the main profile
            try {
              const phoneResponse = await axios.get(`${API_URL}/user/getPhoneFromUser/${userId}`, { withCredentials: true });
              if (phoneResponse.data.code === 200) {
                this.user.phone = phoneResponse.data.data.phone;
              }
            } catch (phoneErr) {
              console.error('Error fetching phone:', phoneErr);
            }
            
            // Fetch ratings from the ratings API
            try {
              // Connect to your ratings API
              const ratingsResponse = await axios.get(`${RATING_SERVICE_GET_URL}${userId}`, { withCredentials: false });
              if (ratingsResponse.data && ratingsResponse.data.Rating && Array.isArray(ratingsResponse.data.Rating)) {
                // Process the ratings
                const ratings = ratingsResponse.data.Rating;
                
                // Calculate average rating
                if (ratings.length > 0) {
                  const totalScore = ratings.reduce((sum, rating) => sum + rating.RatingScore, 0);
                  this.user.rating = (totalScore / ratings.length).toFixed(1);
                } else {
                  this.user.rating = 0;
                }
                
                // Format for the component's expected structure - without comments
                this.userRatings = ratings.map(rating => ({
                  stars: rating.RatingScore || 0,
                  date: rating.CreatedAt || new Date().toISOString(),
                  rater: {
                    name: `User ${rating.RaterID}`, 
                    avatar: null,
                    id: rating.RaterID
                  }
                }));
                
                // Sort ratings by date (newest first)
                this.userRatings.sort((a, b) => new Date(b.date) - new Date(a.date));
              } else {
                console.log('No ratings found or invalid response format');
                this.userRatings = [];
                this.user.rating = 0;
              }
            } catch (ratingsErr) {
              console.error('Error fetching user ratings:', ratingsErr);
              this.userRatings = [];
              this.user.rating = 0;
              // Don't set error, we'll just show "No ratings yet"
            }
          } else {
            this.error = response.data.message || 'Failed to load user profile';
          }
        } else {
          // User not authenticated
          this.error = 'You are not logged in. Please log in to view your profile.';
        }
      } catch (err) {
        console.error('Error fetching user profile:', err);
        this.error = 'Unable to load profile. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    // Toggle edit mode
    toggleEditMode() {
      if (this.isEditing) {
        // Save changes
        if (this.validateForm()) {
          this.saveChanges();
        }
      } else {
        // Enter edit mode
        this.editedUser = {...this.user}; // Copy user data
        this.isEditing = true;
      }
    },
    
    // Validate form before saving
    validateForm() {
      this.validationErrors = {};
      let isValid = true;
      
      // Validate name
      if (!this.editedUser.name || !this.editedUser.name.trim()) {
        this.validationErrors.name = "Name is required";
        isValid = false;
      }
      
      // Validate phone (optional but must be valid if provided)
      if (this.editedUser.phone && !/^\+?[0-9\s\-()]{7,20}$/.test(this.editedUser.phone)) {
        this.validationErrors.phone = "Please enter a valid phone number";
        isValid = false;
      }
      
      return isValid;
    },
    
    // Save changes to API
    async saveChanges() {
      try {
        // For now, we'll just update the phone number since that's what the API supports
        if (this.user.phone !== this.editedUser.phone) {
          // Here you would make an API call to update the phone number
          // Since there's no update endpoint in the provided API, this is a placeholder
          
          // Simulate API call
          this.user.phone = this.editedUser.phone;
          this.isEditing = false;
          
          // Show success toast
          this.toastMessage = 'Profile updated successfully!';
          if (this.toast) {
            this.toast.show();
          }
        } else {
          // No changes were made
          this.isEditing = false;
        }
      } catch (err) {
        console.error('Error saving profile changes:', err);
        this.errorMessage = 'Failed to save changes. Please try again.';
        if (this.errorToast) {
          this.errorToast.show();
        }
      }
    },
    
    // Handle profile photo change
    handleProfilePhotoChange(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Check file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        alert("File is too large. Maximum size is 5MB.");
        return;
      }
      
      // Preview the image
      const reader = new FileReader();
      reader.onload = e => {
        this.editedUser.avatar = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    
    // Rating utility methods
    getRatingCount(stars) {
      return this.userRatings.filter(rating => rating.stars === stars).length;
    },
    
    getRatingPercentage(stars) {
      if (this.userRatings.length === 0) return 0;
      const count = this.getRatingCount(stars);
      return (count / this.userRatings.length) * 100;
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    },
    
    // Payment methods management
    addNewPaymentMethod() {
      // Reset new payment form
      this.newPayment = {
        type: 'card',
        name: '',
        lastFour: '',
        expiryDate: '',
        identifier: '',
        default: false
      };
      
      // Show modal
      if (this.paymentModal) {
        this.paymentModal.show();
      }
    },
    
    closePaymentModal() {
      if (this.paymentModal) {
        this.paymentModal.hide();
      }
    },
    
    saveNewPaymentMethod() {
      // Validate the payment method
      let isValid = true;
      
      if (this.newPayment.type === 'card') {
        if (!this.newPayment.lastFour || this.newPayment.lastFour.length !== 4) {
          alert("Please enter the last 4 digits of your card");
          isValid = false;
        }
      } else if (!this.newPayment.identifier) {
        alert("Please enter your payment information");
        isValid = false;
      }
      
      if (!isValid) return;
      
      // If this is set as default, clear other defaults
      if (this.newPayment.default) {
        this.paymentMethods.forEach(method => {
          method.default = false;
        });
      }
      
      // Add new payment method
      this.paymentMethods.push({...this.newPayment});
      
      // In a real application, you would save this to your backend
      // For example:
      // await axios.post(`${API_URL}/user/${this.user.uid}/payment-methods`, 
      //   { paymentMethod: this.newPayment }, 
      //   { withCredentials: true }
      // );
      
      // Show success toast
      this.toastMessage = 'Payment method added successfully!';
      if (this.toast) {
        this.toast.show();
      }
      
      // Close modal
      this.closePaymentModal();
    },
    
    removePaymentMethod(index) {
      // Check if it's the default method
      const isDefault = this.paymentMethods[index].default;
      
      // Remove the payment method
      this.paymentMethods.splice(index, 1);
      
      // If it was the default and there are other methods, set the first one as default
      if (isDefault && this.paymentMethods.length > 0) {
        this.paymentMethods[0].default = true;
      }
      
      // In a real application, you would update this on your backend
      
      // Show success toast
      this.toastMessage = 'Payment method removed successfully!';
      if (this.toast) {
        this.toast.show();
      }
    },
    
    setDefaultPayment(index) {
      // If this method is being set as default
      if (this.paymentMethods[index].default) {
        // Clear the default flag on all other methods
        this.paymentMethods.forEach((method, i) => {
          if (i !== index) {
            method.default = false;
          }
        });
      } else {
        // If this was the only default and it's being unset, we need at least one default
        const hasOtherDefault = this.paymentMethods.some((method, i) => i !== index && method.default);
        if (!hasOtherDefault && this.paymentMethods.length > 0) {
          // Keep this as default if there's no other default
          this.paymentMethods[index].default = true;
          alert("You must have at least one default payment method");
        }
      }
      
      // In a real application, you would update this on your backend
    },
    
    getPaymentIcon(type) {
      switch (type) {
        case 'card':
          return 'bi bi-credit-card';
        case 'paypal':
          return 'bi bi-paypal';
        case 'bankAccount':
          return 'bi bi-bank';
        default:
          return 'bi bi-cash-stack';
      }
    },
    
    getPaymentTypeLabel(type) {
      switch (type) {
        case 'card':
          return 'Credit/Debit Card';
        case 'paypal':
          return 'PayPal';
        case 'bankAccount':
          return 'Bank Account';
        default:
          return 'Other';
      }
    },
    
    // Log out user
    async logout() {
      try {
        const response = await axios.post(`${API_URL}/logout`, {}, { withCredentials: true });
        
        if (response.data.code === 200) {
          // Clear local storage or any other client-side storage
          localStorage.removeItem('uid');
          
          // Redirect to login page
          this.$router.push('/login');
        }
      } catch (err) {
        console.error('Error during logout:', err);
        this.errorMessage = 'Failed to log out. Please try again.';
        if (this.errorToast) {
          this.errorToast.show();
        }
      }
    }
  },
  mounted() {
    // Fetch user profile when component mounts
    this.fetchUserProfile();
    
    // Initialize Bootstrap components
    if (this.$refs.paymentModal) {
      this.paymentModal = new Modal(this.$refs.paymentModal);
    }
    
    if (this.$refs.toast) {
      this.toast = new Toast(this.$refs.toast, {
        autohide: true,
        delay: 3000
      });
    }
    
    if (this.$refs.errorToast) {
      this.errorToast = new Toast(this.$refs.errorToast, {
        autohide: true,
        delay: 4000
      });
    }
    
    // Demo data for payment methods - in a real app, this would come from your API
    // Remove this when you have a real API endpoint for payment methods
    this.paymentMethods = [
      {
        type: 'card',
        name: 'Personal Visa',
        lastFour: '4242',
        expiryDate: '09/27',
        default: true
      }
    ];
  }
};
</script>

<style scoped>
.profile-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.card {
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.card-header {
  background-color: rgba(0,0,0,0.02);
  border-bottom: 1px solid rgba(0,0,0,0.05);
  padding: 15px 20px;
}

.card-body {
  padding: 20px;
}

.stars-container {
  font-size: 1rem;
  color: #ffc107;
  letter-spacing: 2px;
}

.user-avatar img {
  border: 3px solid #fff;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* Progress bar custom styling */
.progress {
  background-color: #e9ecef;
  border-radius: 5px;
  overflow: hidden;
}

.progress-bar {
  border-radius: 5px;
}

/* Responsiveness */
@media (max-width: 768px) {
  .container {
    padding-left: 15px;
    padding-right: 15px;
  }
  
  .card-body {
    padding: 15px;
  }
}
</style>