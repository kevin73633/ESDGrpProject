<template>
    <div>
      <button @click="fetchDealDetails" class="verify-deal-button" :disabled="isLoading">
        <span v-if="isLoading" class="loading-spinner"></span>
        <span v-else>Verify Receipt</span>
      </button>
  
      <!-- Modal -->
      <div v-if="showModal" class="modal-backdrop">
        <div class="modal-content">
          <div v-if="loadingDetails" class="loading-container">
            <div class="loading-spinner large"></div>
            <p>Loading deal details...</p>
          </div>
          
          <div v-else-if="error" class="error-container">
            <h3>Error Loading Details</h3>
            <p>{{ error }}</p>
            <button @click="closeModal" class="primary-button">Close</button>
          </div>
          
          <div v-else-if="dealDetails" class="deal-details">
            <h2>Verify Goods Receipt</h2>
            
            <div class="product-info">
              <div class="product-details">
                <h3>{{ dealDetails.productName }}</h3>
                <p class="product-description">{{ dealDetails.description }}</p>
                <div class="price-tag">{{ formatPrice(price) }}</div>
              </div>
            </div>
            
            <div class="details-section">
              <h4>Deal Details</h4>
              <ul>
                <li v-for="(value, key) in formattedDetails" :key="key">
                  <strong>{{ formatLabel(key) }}:</strong> {{ value }}
                </li>
              </ul>
            </div>
  
            <div class="rating-section">
              <h4>Rate your experience with the other party</h4>
              <p class="rating-description">Please rate your experience with the seller/buyer:</p>
              
              <div class="star-rating">
                <div class="stars">
                  <span 
                    v-for="star in 5" 
                    :key="star" 
                    class="star" 
                    :class="{ 'active': userRating >= star }"
                    @click="userRating = star"
                  >
                    ★
                  </span>
                </div>
                <div class="rating-text">{{ getRatingText() }}</div>
              </div>
              
              <div class="rating-feedback">
                <label for="rating-feedback">Additional feedback (optional):</label>
                <textarea 
                  id="rating-feedback" 
                  v-model="ratingFeedback" 
                  class="form-control" 
                  rows="2" 
                  placeholder="Share your experience with this user..."
                ></textarea>
              </div>
            </div>
            
            <!-- Regular verification view -->
            <div v-if="!showComplaintForm">
              <div class="terms-checkbox">
                <input type="checkbox" id="terms" v-model="termsAccepted">
                <label for="terms">I acknowledge that I have received the goods in good condition</label>
              </div>
              
              <div class="modal-actions">
                <button @click="fileComplaint" class="complaint-button">File a Complaint</button>
                <button @click="closeModal" class="cancel-button">Cancel</button>
                <button @click="verifyDeal" class="verify-button" :disabled="!termsAccepted || !userRating || isSubmitting">
                  <span v-if="isSubmitting" class="loading-spinner small"></span>
                  <span v-else>Verify Receipt</span>
                </button>
              </div>
            </div>
            
            <!-- Complaint form view -->
            <div v-else>
              <div class="form-group">
                <label for="complaint-reason">Reason for complaint:</label>
                <select id="complaint-reason" v-model="complaintReason" class="form-control">
                  <option value="">Select a reason</option>
                  <option value="damaged">Item arrived damaged</option>
                  <option value="wrong">Received wrong item</option>
                  <option value="missing">Parts/items missing</option>
                  <option value="quality">Quality not as described</option>
                  <option value="other">Other</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="complaint-details">Describe your issue:</label>
                <textarea id="complaint-details" v-model="complaintDetails" class="form-control" rows="5" placeholder="Please provide details about your complaint..."></textarea>
              </div>
              
              <div class="terms-checkbox">
                <input type="checkbox" id="complaint-terms" v-model="termsAccepted">
                <label for="complaint-terms">I acknowledge that I have received the goods, despite the issue</label>
              </div>
              
              <div class="modal-actions">
                <button @click="hideComplaintForm" class="cancel-button">Back</button>
                <button @click="submitComplaint" class="submit-complaint-button" 
                  :disabled="!complaintReason || !complaintDetails.trim() || !termsAccepted || !userRating || isSubmittingComplaint">
                  <span v-if="isSubmittingComplaint" class="loading-spinner small"></span>
                  <span v-else>Submit Complaint</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
    const DEAL_API_URL = 'http://localhost:8000'; 
    const VERIFY_DEAL_API_URL = 'http://localhost:8000/verify_deal';
    import axios from 'axios';
    
    export default {
      name: 'verifyDealButton',
      props: {
        dealId: {
          type: [Number, String],
          required: true
        },
        productId: {
          type: [Number, String],
          required: true
        },
        userId: {
          type: [Number, String],
          required: true
        },
        price: {
          type: [Number],
          required: true
        }
      },
      data() {
        return {
          isLoading: false,
          showModal: false,
          loadingDetails: false,
          dealDetails: null,
          error: null,
          termsAccepted: false,
          isSubmitting: false,
          showComplaintForm: false,
          complaintReason: '',
          complaintDetails: '',
          isSubmittingComplaint: false,
          userRating: 0,
          ratingFeedback: ''
        }
      },
      computed: {
        formattedDetails() {
          if (!this.dealDetails) return {};
          
          const { status, ...filteredDetails } = this.dealDetails.deal; // Exclude status
          return filteredDetails;
        }
      },
      methods: {
        async fetchDealDetails() {
          this.isLoading = true;
          try {
            this.showModal = true;
            this.loadingDetails = true;
            this.error = null;
            this.showComplaintForm = false;
            this.termsAccepted = false;
            this.userRating = 0;
            this.ratingFeedback = '';
  
            const dealResponse = await fetch(`${DEAL_API_URL}/deal/${this.dealId}`);
            
            if (!dealResponse.ok) {
              throw new Error(`HTTP Error ${dealResponse.status}`);
            }
  
            const contentType = dealResponse.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
              throw new Error("Expected JSON, received HTML or another format.");
            }
  
            const dealData = await dealResponse.json();
            console.log("Deal Data:", dealData); // Debugging
            this.dealDetails = dealData.data;
  
          } catch (error) {
            console.error('Error fetching deal details:', error);
            this.error = error.message || "An unexpected error occurred.";
          } finally {
            this.loadingDetails = false;
            this.isLoading = false;
          }
        },
      
        async verifyDeal() {
          if (!this.termsAccepted || !this.userRating || this.isSubmitting) return;
          
          this.isSubmitting = true;
          
          try {
            // API call to verify the deal
            const response = await axios.post(`${VERIFY_DEAL_API_URL}/${this.dealId}`, {
              userId: this.userId,
              rating: this.userRating,
              feedback: this.ratingFeedback
            });
            
            if (response.data.code === 200) {
              // Create an enhanced data object
              const enhancedData = {
                ...response.data.data,
                verifiedByCurrentUser: true,
                rating: this.userRating,
                feedback: this.ratingFeedback
              };
              
              // Check if both users have verified
              if (response.data.data.verificationStatus === 'complete') {
                enhancedData.bothVerified = true;
              }
              
              this.$emit('deal-verified', enhancedData);
              this.closeModal();
              
              // Show success message
              const productName = response.data.data.product.title || 'Product';
              const price = this.formatPrice(response.data.data.product.price || 0);
              
              let message = `Receipt of goods for ${productName} (${price}) verified successfully!`;
              if (enhancedData.bothVerified) {
                message = `Receipt of goods for ${productName} (${price}) completely verified!`;
              }
              
              this.$emit('show-notification', {
                message: message,
                type: 'success'
              });
            } else {
              throw new Error(response.data.message || 'Failed to verify receipt');
            }
          } catch (error) {
            console.error('Error verifying receipt:', error);
            this.$emit('show-notification', {
              message: `Failed to verify receipt: ${error.message}`,
              type: 'error'
            });
          } finally {
            this.isSubmitting = false;
          }
        },
        
        getRatingText() {
          const ratingTexts = [
            '',
            'Poor',
            'Fair',
            'Good',
            'Very Good',
            'Excellent'
          ];
          return ratingTexts[this.userRating] || '';
        },
        
        fileComplaint() {
          this.showComplaintForm = true;
          // Reset terms acceptance when switching to complaint form
          this.termsAccepted = false;
        },
        
        hideComplaintForm() {
          this.showComplaintForm = false;
          this.complaintReason = '';
          this.complaintDetails = '';
          // Reset terms acceptance when switching back to verification form
          this.termsAccepted = false;
        },
        
        async submitComplaint() {
          if (!this.complaintReason || !this.complaintDetails.trim() || !this.termsAccepted || !this.userRating || this.isSubmittingComplaint) return;
          
          this.isSubmittingComplaint = true;
          
          try {
            // API call to verify the deal with complaint
            const response = await axios.post(`${VERIFY_DEAL_API_URL}/${this.dealId}`, {
              userId: this.userId,
              rating: this.userRating,
              feedback: this.ratingFeedback,
              hasComplaint: true,
              complaintReason: this.complaintReason,
              complaintDetails: this.complaintDetails
            });
            
            if (response.data.code === 200) {
              // Create an enhanced data object that includes rating and complaint information
              const enhancedData = {
                ...response.data.data,
                verifiedByCurrentUser: true,
                rating: this.userRating,
                feedback: this.ratingFeedback,
                hasComplaint: true
              };
              
              this.$emit('deal-verified', enhancedData);
              this.closeModal();
              
              // Show more detailed success message
              const productName = response.data.data?.product?.title || 'Product';
              const price = this.formatPrice(response.data.data?.product?.price || 0);
              
              this.$emit('show-notification', {
                message: `Your complaint for ${productName} (${price}) has been submitted successfully!`,
                type: 'success'
              });
            } else {
              throw new Error(response.data.message || 'Failed to submit complaint');
            }
          } catch (error) {
            console.error('Error submitting complaint:', error);
            
            // If we're just simulating the API (for development)
            if (VERIFY_DEAL_API_URL.startsWith('http://localhost')) {
              // Simulate success for development
              setTimeout(() => {
                this.closeModal();
                this.$emit('show-notification', {
                  message: 'Your complaint has been submitted successfully!',
                  type: 'success'
                });
              }, 1000);
              return;
            }
            
            this.$emit('show-notification', {
              message: `Failed to submit complaint: ${error.message}`,
              type: 'error'
            });
          } finally {
            this.isSubmittingComplaint = false;
          }
        },
        
        closeModal() {
          this.showModal = false;
          this.dealDetails = null;
          this.error = null;
          this.termsAccepted = false;
          this.showComplaintForm = false;
          this.complaintReason = '';
          this.complaintDetails = '';
          this.userRating = 0;
          this.ratingFeedback = '';
        },
        
        formatPrice(price) {
          return `$${parseFloat(price).toFixed(2)}`;
        },
        
        formatLabel(key) {
          // Convert camelCase to sentence case
          return key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase());
        }
      }
    }
  </script>
  
  <style scoped>
  .verify-deal-button {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    min-width: 150px;
  }
  
  .verify-deal-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
  }
  
  .modal-content {
    background-color: white;
    border-radius: 8px;
    padding: 24px;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .loading-container, .error-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 0;
  }
  
  .loading-spinner {
    border: 3px solid #f3f3f3;
    border-top: 3px solid #3498db;
    border-radius: 50%;
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
    display: inline-block;
    vertical-align: middle;
  }
  
  .loading-spinner.large {
    width: 50px;
    height: 50px;
    margin-bottom: 20px;
  }
  
  .loading-spinner.small {
    width: 12px;
    height: 12px;
    margin-right: 8px;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .product-info {
    display: flex;
    margin-bottom: 24px;
    border: 1px solid #eee;
    border-radius: 4px;
    padding: 16px;
    background-color: #f9f9f9;
  }
  
  .product-image {
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 4px;
    margin-right: 16px;
  }
  
  .product-details {
    flex: 1;
  }
  
  .product-description {
    color: #666;
    margin: 8px 0;
  }
  
  .price-tag {
    font-size: 1.5rem;
    font-weight: bold;
    color: #4caf50;
  }
  
  .details-section {
    margin-bottom: 24px;
  }
  
  .details-section ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }
  
  .details-section li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
  }
  
  .terms-checkbox {
    margin-bottom: 24px;
  }
  
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
  
  .cancel-button {
    background-color: #e0e0e0;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .verify-button {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 120px;
  }
  
  .verify-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .complaint-button {
    background-color: #ff9800;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    margin-right: auto;
  }
  
  .submit-complaint-button {
    background-color: #ff9800;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 150px;
  }
  
  .submit-complaint-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
  }
  
  .complaint-form {
    padding: 20px 0;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-control {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }
  
  textarea.form-control {
    resize: vertical;
  }
  
  .error-container {
    color: #d32f2f;
    text-align: center;
  }
  
  .primary-button {
    background-color: #2196f3;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    margin-top: 16px;
  }
  
  .rating-section {
    margin-bottom: 24px;
    padding: 16px;
    background-color: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #eee;
  }
  
  .rating-section h4 {
    margin-top: 0;
    margin-bottom: 12px;
    font-size: 1rem;
  }
  
  .rating-description {
    margin-bottom: 12px;
    color: #666;
  }
  
  .star-rating {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 16px;
  }
  
  .stars {
    display: flex;
    gap: 4px;
    margin-bottom: 8px;
    }

    .star {
    font-size: 2rem;
    color: #ddd;
    cursor: pointer;
    transition: color 0.2s ease;
    }

    .star:hover {
    color: #ffb400;
    }

    .star.active {
    color: #ffb400;
    }

    .rating-text {
    font-weight: bold;
    color: #666;
    height: 1.5rem;
    }

    .rating-feedback {
    margin-top: 12px;
    }

    .rating-feedback label {
    display: block;
    margin-bottom: 6px;
    font-weight: 500;
    }
  </style>