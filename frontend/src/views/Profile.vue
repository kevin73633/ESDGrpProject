<template>
  <div class="profile-page">
    <!-- Header with navigation -->
    <nav class="navbar navbar-light bg-light">
      <div class="container-fluid">
        <router-link to="/" class="navbar-brand d-flex align-items-center">
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
            <i :class="isEditing ? 'fas fa-save' : 'fas fa-edit'" class="me-2"></i>
            {{ isEditing ? 'Save Changes' : 'Edit Profile' }}
          </button>
        </div>
      </div>
    </nav>
    
    <div class="container py-5">
      <div class="row">
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
                    <i class="fas fa-camera"></i>
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
              <h5 class="my-3">{{ user.fullName }}</h5>
              <p class="text-muted mb-1">{{ user.title }}</p>
              <p class="text-muted mb-4">{{ user.location }}</p>
              
              <div class="d-flex justify-content-center mb-2">
                <div class="me-3">
                  <strong>{{ user.dealsCompleted }}</strong>
                  <div class="small text-muted">Deals</div>
                </div>
                <div class="border-start ps-3">
                  <strong>{{ user.memberSince }}</strong>
                  <div class="small text-muted">Member Since</div>
                </div>
              </div>
              
              <!-- User Ratings -->
              <div class="rating-summary text-center mt-3">
                <div class="d-flex align-items-center justify-content-center mb-2">
                  <span class="h3 mb-0 me-2">{{ averageRating.toFixed(1) }}</span>
                  <div>
                    <div class="stars-container">
                      <i 
                        v-for="star in 5" 
                        :key="star" 
                        :class="[
                          star <= Math.round(averageRating) ? 'fas fa-star text-warning' : 'far fa-star text-muted'
                        ]"
                      ></i>
                    </div>
                    <div class="small text-muted">{{ userRatings.length }} ratings</div>
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
                <i class="fas fa-info-circle me-1"></i> Editing enabled
              </span>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="form-label small text-muted">Email</label>
                <div v-if="!isEditing" class="mb-0">{{ user.email }}</div>
                <input 
                  v-else 
                  type="email" 
                  class="form-control" 
                  v-model="editedUser.email"
                  :class="{ 'is-invalid': validationErrors.email }" 
                >
                <div v-if="validationErrors.email" class="invalid-feedback">
                  {{ validationErrors.email }}
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label small text-muted">Phone</label>
                <div v-if="!isEditing" class="mb-0">{{ user.phone }}</div>
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
              
              <div class="mb-0">
                <label class="form-label small text-muted">Preferred Contact Method</label>
                <div v-if="!isEditing" class="mb-0">{{ user.preferredContactMethod }}</div>
                <select 
                  v-else 
                  class="form-select" 
                  v-model="editedUser.preferredContactMethod"
                >
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="inapp">In-App Messaging</option>
                </select>
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
                  <div v-if="!isEditing">{{ user.fullName }}</div>
                  <input 
                    v-else 
                    type="text" 
                    class="form-control" 
                    v-model="editedUser.fullName"
                    :class="{ 'is-invalid': validationErrors.fullName }" 
                  >
                  <div v-if="validationErrors.fullName" class="invalid-feedback">
                    {{ validationErrors.fullName }}
                  </div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">Username</label>
                </div>
                <div class="col-sm-9">
                  <div v-if="!isEditing">@{{ user.username }}</div>
                  <div class="input-group" v-else>
                    <span class="input-group-text">@</span>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="editedUser.username"
                      :class="{ 'is-invalid': validationErrors.username }" 
                    >
                    <div v-if="validationErrors.username" class="invalid-feedback">
                      {{ validationErrors.username }}
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">Title/Bio</label>
                </div>
                <div class="col-sm-9">
                  <div v-if="!isEditing">{{ user.title }}</div>
                  <input 
                    v-else 
                    type="text" 
                    class="form-control" 
                    v-model="editedUser.title"
                    placeholder="e.g. Deal Hunter, Food Enthusiast, etc."
                  >
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-sm-3">
                  <label class="form-label small text-muted">Location</label>
                </div>
                <div class="col-sm-9">
                  <div v-if="!isEditing">{{ user.location }}</div>
                  <input 
                    v-else 
                    type="text" 
                    class="form-control" 
                    v-model="editedUser.location"
                  >
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
                <i class="fas fa-plus me-1"></i> Add New
              </button>
            </div>
            <div class="card-body">
              <div v-if="user.paymentMethods.length === 0" class="text-center py-4">
                <i class="fas fa-credit-card text-muted mb-3" style="font-size: 2rem;"></i>
                <p class="mb-0">No payment methods added yet.</p>
                <button 
                  v-if="isEditing" 
                  class="btn btn-primary mt-3"
                  @click="addNewPaymentMethod"
                >
                  <i class="fas fa-plus me-1"></i> Add Payment Method
                </button>
              </div>
              
              <div v-else>
                <div 
                  v-for="(method, index) in editedUser.paymentMethods" 
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
                        <i class="fas fa-trash"></i>
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
          
          <!-- Ratings and Reviews -->
          <div class="card">
            <div class="card-header">
              <h6 class="mb-0">Ratings & Reviews</h6>
            </div>
            <div class="card-body">
              <div v-if="userRatings.length === 0" class="text-center py-4">
                <i class="fas fa-star text-muted mb-3" style="font-size: 2rem;"></i>
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
                              star <= rating.stars ? 'fas fa-star text-warning' : 'far fa-star text-muted'
                            ]"
                          ></i>
                        </div>
                        <p class="mb-0">{{ rating.comment }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="userRatings.length > 3" class="text-center mt-3">
                    <button class="btn btn-outline-primary btn-sm">
                      View All Reviews
                    </button>
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
            <i class="fas fa-check-circle me-2"></i>
            Profile updated successfully!
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal, Toast } from 'bootstrap';

export default {
  name: 'ProfilePage',
  data() {
    return {
      isEditing: false,
      user: {
        fullName: 'John Doe',
        username: 'johndoe',
        email: 'john.doe@example.com',
        phone: '+1 (123) 456-7890',
        preferredContactMethod: 'email',
        title: 'Deal Enthusiast',
        location: 'New York, NY',
        avatar: '/api/placeholder/150/150',
        memberSince: 'Jan 2023',
        dealsCompleted: 25,
        paymentMethods: [
          {
            type: 'card',
            name: 'Personal Visa',
            lastFour: '4242',
            expiryDate: '09/27',
            default: true
          },
          {
            type: 'paypal',
            identifier: 'john.doe@example.com',
            default: false
          }
        ]
      },
      editedUser: {}, // Will be populated with user data when editing starts
      validationErrors: {},
      userRatings: [
        {
          stars: 5,
          comment: "Great experience! John was responsive and the deal was exactly as described.",
          date: "2025-03-15T14:30:00Z",
          rater: {
            name: "Alice Smith",
            avatar: "/api/placeholder/40/40"
          }
        },
        {
          stars: 4,
          comment: "Good communication and easy to work with. Would recommend.",
          date: "2025-03-10T11:15:00Z",
          rater: {
            name: "Bob Johnson",
            avatar: "/api/placeholder/40/40"
          }
        },
        {
          stars: 5,
          comment: "Very professional! The transaction was smooth and John was very helpful.",
          date: "2025-03-01T09:45:00Z",
          rater: {
            name: "Emma Wilson",
            avatar: "/api/placeholder/40/40"
          }
        }
      ],
      newPayment: {
        type: 'card',
        name: '',
        lastFour: '',
        expiryDate: '',
        identifier: '',
        default: false
      },
      paymentModal: null,
      toast: null
    };
  },
  computed: {
    averageRating() {
      if (this.userRatings.length === 0) return 0;
      const sum = this.userRatings.reduce((total, rating) => total + rating.stars, 0);
      return sum / this.userRatings.length;
    }
  },
  methods: {
    toggleEditMode() {
      if (this.isEditing) {
        // Save changes
        if (this.validateForm()) {
          this.saveChanges();
        }
      } else {
        // Enter edit mode
        this.editedUser = JSON.parse(JSON.stringify(this.user)); // Deep copy
        this.isEditing = true;
      }
    },
    validateForm() {
      this.validationErrors = {};
      let isValid = true;
      
      // Validate full name
      if (!this.editedUser.fullName.trim()) {
        this.validationErrors.fullName = "Full name is required";
        isValid = false;
      }
      
      // Validate username
      if (!this.editedUser.username.trim()) {
        this.validationErrors.username = "Username is required";
        isValid = false;
      } else if (this.editedUser.username.includes(' ')) {
        this.validationErrors.username = "Username cannot contain spaces";
        isValid = false;
      }
      
      // Validate email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.editedUser.email.trim()) {
        this.validationErrors.email = "Email is required";
        isValid = false;
      } else if (!emailRegex.test(this.editedUser.email)) {
        this.validationErrors.email = "Please enter a valid email address";
        isValid = false;
      }
      
      // Validate phone (optional but must be valid if provided)
      if (this.editedUser.phone.trim() && !/^\+?[0-9\s\-()]{7,20}$/.test(this.editedUser.phone)) {
        this.validationErrors.phone = "Please enter a valid phone number";
        isValid = false;
      }
      
      return isValid;
    },
    saveChanges() {
      // In a real app, this would send data to an API
      this.user = JSON.parse(JSON.stringify(this.editedUser));
      this.isEditing = false;
      
      // Show success toast
      if (this.toast) {
        this.toast.show();
      }
    },
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
        this.editedUser.paymentMethods.forEach(method => {
          method.default = false;
        });
      }
      
      // Add new payment method
      this.editedUser.paymentMethods.push({...this.newPayment});
      
      // Close modal
      this.closePaymentModal();
    },
    removePaymentMethod(index) {
      // Check if it's the default method
      const isDefault = this.editedUser.paymentMethods[index].default;
      
      // Remove the payment method
      this.editedUser.paymentMethods.splice(index, 1);
      
      // If it was the default and there are other methods, set the first one as default
      if (isDefault && this.editedUser.paymentMethods.length > 0) {
        this.editedUser.paymentMethods[0].default = true;
      }
    },
    setDefaultPayment(index) {
      // If this method is being set as default
      if (this.editedUser.paymentMethods[index].default) {
        // Clear the default flag on all other methods
        this.editedUser.paymentMethods.forEach((method, i) => {
          if (i !== index) {
            method.default = false;
          }
        });
      } else {
        // If this was the only default and it's being unset, we need at least one default
        const hasOtherDefault = this.editedUser.paymentMethods.some((method, i) => i !== index && method.default);
        if (!hasOtherDefault) {
          // Keep this as default if there's no other default
          this.editedUser.paymentMethods[index].default = true;
          alert("You must have at least one default payment method");
        }
      }
    },
    getPaymentIcon(type) {
      switch (type) {
        case 'card':
          return 'fas fa-credit-card';
        case 'paypal':
          return 'fab fa-paypal';
        case 'bankAccount':
          return 'fas fa-university';
        default:
          return 'fas fa-money-bill-alt';
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
    }
  },
  mounted() {
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

.payment-method {
  transition: all 0.2s ease;
}

.payment-method:hover {
  background-color: #f8f9fa;
}

.payment-icon {
  width: 40px;
  text-align: center;
  color: #6c757d;
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