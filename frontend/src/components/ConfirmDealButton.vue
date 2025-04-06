<template>
    <div>
      <button @click="fetchDealDetails" class="confirm-deal-button" :disabled="isLoading">
        <span v-if="isLoading" class="loading-spinner"></span>
        <span v-else>Confirm Deal</span>
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
            <h2>Confirm Deal</h2>
            
            <div class="product-info">
              <div class="product-details">
                <h3>{{ dealDetails.productName }}</h3>
                <p class="product-description">{{ dealDetails.description }}</p>
                <div class="price-tag">{{ formatPrice(this.price) }}</div>
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
            
            <div class="terms-checkbox">
              <input type="checkbox" id="terms" v-model="termsAccepted">
              <label for="terms">I understand and agree to the terms of this deal</label>
            </div>
            
            <div class="modal-actions">
              <button @click="closeModal" class="cancel-button">Cancel</button>
              <button @click="confirmDeal" class="confirm-button" :disabled="!termsAccepted || isSubmitting">
                <span v-if="isSubmitting" class="loading-spinner small"></span>
                <span v-else>Confirm Deal</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
    const DEAL_API_URL = 'http://localhost:8000'; 
    const CONFIRM_DEAL_API_URL = 'http://localhost:8000/confirm_deal'; 
    import axios from 'axios';
    export default {
        name: 'ConfirmDealButton',
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
            required:true
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
            isSubmitting: false
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
        
        async confirmDeal() {
            if (!this.termsAccepted || this.isSubmitting) return;
            
            this.isSubmitting = true;
            
            try {
            // API call to confirm the deal based on confirm_deal.py
            const response = await axios.post(`${CONFIRM_DEAL_API_URL}/${this.dealId}/${this.userId}`);
            if (response.data.code === 200) {
                this.$emit('deal-confirmed', response.data.data);
                this.closeModal();
                
                // Show more detailed success message
                const productName = response.data.data.product.title;
                const price = this.formatPrice(response.data.data.product.price);
                this.$emit('show-notification', {
                    message: `Deal for ${productName} (${price}) confirmed successfully!`,
                    type: 'success'
                });
                } else {
                throw new Error(response.data.message || 'Failed to confirm deal');
                }
            } catch (error) {
                console.error('Error confirming deal:', error);
                this.$emit('show-notification', {
                message: `Failed to confirm deal: ${error.message}`,
                type: 'error'
                });
            } finally {
                this.isSubmitting = false;
            }
        },
        
        closeModal() {
            this.showModal = false;
            this.dealDetails = null;
            this.error = null;
            this.termsAccepted = false;
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
  .confirm-deal-button {
    background-color: #4caf50;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
    min-width: 150px;
  }
  
  .confirm-deal-button:disabled {
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
  
  .confirm-button {
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
  
  .confirm-button:disabled {
    background-color: #cccccc;
    cursor: not-allowed;
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
  </style>