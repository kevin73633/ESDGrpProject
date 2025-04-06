<template>
    <div class="profile-page">
      <!-- Header with navigation -->
      <nav class="navbar navbar-light bg-light">
        <div class="container-fluid">
          <router-link to="/chat" class="navbar-brand d-flex align-items-center">
            <button class="btn btn-link text-dark me-3 p-0" style="font-size: 1.5rem;">
              <i class="bi bi-arrow-left"></i>
            </button>
            <span>Back to Chat</span>
          </router-link>
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
              </div>
              <div class="card-body">
                <div class="mb-3">
                  <label class="form-label small text-muted">Account Number</label>
                  <div class="mb-0">{{ user.accnum }}</div>
                </div>
                
                <div class="mb-3">
                  <label class="form-label small text-muted">Phone</label>
                  <div class="mb-0">{{ user.phone || 'Not specified' }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Right Column: Account Details and Ratings -->
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
                    <div>{{ user.name }}</div>
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
  
                <!-- Additional contact button -->
                <div class="row mt-4">
                  <div class="col-12">
                    <router-link :to="{ path: '/chat' }" class="btn btn-primary w-100">
                      <i class="bi bi-chat-text me-2"></i> Contact This User
                    </router-link>
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
      
      <!-- Notification Toast -->
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
  import { Toast } from 'bootstrap';
  import axios from 'axios';
  
  // API URL base - should match your backend
  const API_URL = 'http://localhost:8000';
  const RATING_SERVICE_GET_URL = "https://personal-nzmfqiqp.outsystemscloud.com/RatingAPI_REST/rest/v1/userRating/RatedID/?RatedID=";
  
  export default {
    name: 'OtherProfile',
    data() {
      return {
        loading: true,
        error: null,
        user: {
          uid: '',
          name: '',
          rating: 0,
          accnum: '',
          phone: ''
        },
        userRatings: [],
        errorMessage: 'An error occurred. Please try again.',
        errorToast: null
      };
    },
    computed: {
      // Get user ID from route params
      profileUserId() {
        return this.$route.params.id;
      }
    },
    methods: {
      // Fetch user profile data from API
      async fetchUserProfile() {
        this.loading = true;
        this.error = null;
        
        try {
            // First check if user is authenticated
            const authResponse = await axios.get(`${API_URL}/check-auth`, { withCredentials: true });
            
            if (authResponse.data.code === 200 && authResponse.data.data.authenticated) {
            const userId = this.profileUserId;
            
            if (!userId) {
                this.error = "No user ID provided";
                this.loading = false;
                return;
            }
            
            // If authenticated, fetch user profile
            const response = await axios.get(`${API_URL}/user/${userId}`, { withCredentials: true });
            
            if (response.data.code === 200) {
                this.user = response.data.data.user;
                
                // Use the rating from the user data directly
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
                // Connect to your ratings Flask API - use a different URL for ratings
                const ratingsResponse = await axios.get(`${RATING_SERVICE_GET_URL}${userId}`, { withCredentials: false });
                
                if (ratingsResponse.data && Array.isArray(ratingsResponse.data)) {
                    // Map the API response to match our component's expected format
                    this.userRatings = ratingsResponse.data.map(rating => ({
                    stars: rating.Stars || 0,
                    comment: rating.Comment || "",
                    date: rating.CreatedOn || new Date().toISOString(),
                    rater: {
                        name: rating.RaterName || "Anonymous",
                        avatar: rating.RaterAvatar || null
                    }
                    }));
                } else {
                    console.log('No ratings found or invalid response format');
                    this.userRatings = [];
                }
                } catch (ratingsErr) {
                console.error('Error fetching user ratings:', ratingsErr);
                this.userRatings = [];
                // Don't set error, we'll just show "No ratings yet"
                }
            } else {
                this.error = response.data.message || 'Failed to load user profile';
            }
            } else {
            // User not authenticated
            this.error = 'You are not logged in. Please log in to view profiles.';
            }
        } catch (err) {
            console.error('Error fetching user profile:', err);
            this.error = 'Unable to load profile. Please try again later.';
        } finally {
            this.loading = false;
        }
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
      }
    },
    mounted() {
      // Fetch user profile when component mounts
      this.fetchUserProfile();
      
      // Initialize bootstrap toast
      if (this.$refs.errorToast) {
        this.errorToast = new Toast(this.$refs.errorToast, {
          autohide: true,
          delay: 4000
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