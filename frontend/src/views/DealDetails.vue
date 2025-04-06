<template>
  <div class="product-details-page">
    <!-- Back button and navigation -->
    <nav class="navbar navbar-light bg-light">
      <div class="container-fluid">
        <router-link to="/" class="navbar-brand d-flex align-items-center">
          <button class="btn btn-link text-dark me-3 p-0" style="font-size: 1.5rem;">
            <i class="bi bi-arrow-left"></i>
          </button>
          <span>Back to Deals</span>
        </router-link>
        <div class="d-flex align-items-center" v-if="product && isOwner">
          <div class="dropdown">
            <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="actionDropdown" data-bs-toggle="dropdown" aria-expanded="false">
              Actions
            </button>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="actionDropdown">
              <li><a class="dropdown-item" href="#" @click.prevent="editProduct">            <i class="bi bi-pencil me-2"></i>Edit</a></li>
              <li><a class="dropdown-item text-danger" href="#" @click.prevent="confirmDelete"><i class="bi bi-trash me-2"></i>Delete</a></li>
            </ul>
          </div>
        </div>
      </div>
    </nav>

    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading product details...</p>
    </div>

    <!-- Error Message -->
          <div v-else-if="error" class="alert alert-danger m-4" role="alert">
      <i class="bi bi-exclamation-circle me-2"></i>
      {{ error }}
    </div>

    <!-- Product Details -->
    <div v-else-if="product" class="container py-4">
          <div class="product-details">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h2 class="product-title mb-0">{{ product.title }}</h2>
              <span class="badge bg-primary rounded-pill price-badge">${{ formatPrice(product.price) }}</span>
            </div>

            <div class="mb-3 d-flex align-items-center">
              <span class="badge rounded-pill bg-light text-dark me-2">{{ product.category }}</span>
              <span class="text-muted small">Posted {{ formatDate(product.created_at) }}</span>
            </div>

            <hr>

            <div class="location-section mb-3">
              <h5>Location</h5>
              <p><i class="bi bi-geo-alt-fill me-2 text-danger"></i>{{ product.location }}</p>
            </div>

            <div class="description-section mb-4">
              <h5>Description</h5>
              <p>{{ product.description }}</p>
            </div>

            <div v-if="product.expires_at" class="expires-section mb-4">
              <h5>Deal Expires</h5>
              <p><i class="bi bi-calendar me-2"></i>{{ formatDate(product.expires_at) }}</p>
            </div>

            <!-- Contact Seller -->
            <div class="card mb-4">
              <div class="card-header">
                <h5 class="mb-0">Contact Information</h5>
              </div>
              <div class="card-body">
                <div v-if="loading" class="text-center">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <small>Loading user details...</small>
                </div>
                <div v-else-if="seller">
                  <div class="d-flex align-items-center mb-3">
                    <img :src="sellerAvatar" alt="Seller" class="rounded-circle me-3" style="width: 50px; height: 50px;">
                    <div>
                      <h6 class="mb-0">{{ seller.name }}</h6>
                      <div class="rating-stars">
                        <i v-for="star in 5" :key="star" 
                           :class="[star <= Math.round(seller.rating) ? 'bi bi-star-fill text-warning' : 'bi bi-star text-muted']"></i>
                        <span class="ms-1">{{ seller.rating }} stars</span>
                      </div>
                    </div>
                  </div>
                  <div class="mb-3">
                    <button class="btn btn-primary w-100 mb-2" @click="startChat">
                      <i class="bi bi-chat-dots me-2"></i>Chat with Seller
                    </button>
                    <button class="btn btn-outline-primary w-100" @click="goToProfile">
                      <i class="bi bi-person-circle">Profile</i>
                    </button>
                  </div>
                </div>
                <div v-else>
                  <p class="text-muted text-center">Seller information unavailable</p>
                </div>
              </div>
            </div>

            <!-- Share Buttons -->
            <div class="share-buttons">
              <h5>Share this Deal</h5>
              <div class="d-flex gap-2">
                <button class="btn btn-outline-primary">
                  <i class="bi bi-facebook"></i>
                </button>
                <button class="btn btn-outline-info">
                  <i class="bi bi-twitter"></i>
                </button>
                <button class="btn btn-outline-success">
                  <i class="bi bi-whatsapp"></i>
                </button>
                <button class="btn btn-outline-secondary" @click="copyLink">
                  <i class="bi bi-link-45deg"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Similar Products Section -->
      <div class="similar-products mt-5">
        <h3 class="mb-4">Similar Deals</h3>
        <div v-if="similarProducts.length === 0" class="alert alert-light">
          No similar products available at the moment.
        </div>
        <div v-else class="row row-cols-1 row-cols-md-3 g-4">
          <div class="col" v-for="similarProduct in similarProducts" :key="similarProduct.productid">
            <div class="card h-100 product-card" @click="navigateToProduct(similarProduct.productid)">
              <img :src="getProductImage(similarProduct)" class="card-img-top similar-product-image" :alt="similarProduct.title">
              <div class="card-body">
                <h5 class="card-title">{{ similarProduct.title }}</h5>
                <p class="card-text text-muted mb-2">{{ similarProduct.location }}</p>
                <div class="d-flex justify-content-between align-items-center">
                  <span class="badge bg-light text-dark">{{ similarProduct.category }}</span>
                  <strong>${{ formatPrice(similarProduct.price) }}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this product? This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteProduct">
              <i class="bi bi-trash me-2"></i>Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Toast -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div 
        class="toast align-items-center text-white bg-success border-0" 
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
        ref="successToast"
      >
        <div class="d-flex">
          <div class="toast-body">
            <i class="bi bi-check-circle me-2"></i>
            {{ successMessage }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    </div>

    <!-- Error Toast -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 11">
      <div 
        class="toast align-items-center text-white bg-danger border-0" 
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
        ref="errorToast"
      >
        <div class="d-flex">
          <div class="toast-body">
            <i class="bi bi-exclamation-circle me-2"></i>
            {{ errorMessage }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal, Toast } from 'bootstrap';
import OtherProfile from './OtherProfile.vue';

// Define API URLs
const PRODUCT_API_URL = 'http://localhost:8000';
const USER_API_URL = 'http://localhost:8000';
const DEAL_API_URL = 'http://localhost:8000';
const CHAT_API_URL = 'http://localhost:8000';

export default {
  name: 'ProductDetails',
  data() {
    return {
      loading: true,
      error: null,
      product: null,
      seller: null,
      similarProducts: [],
      sellerAvatar: '/api/placeholder/50/50',
      errorMessage: 'An error occurred. Please try again.',
      successMessage: 'Operation completed successfully!',
      deleteModal: null,
      successToast: null,
      errorToast: null
    };
  },
  computed: {
    productId() {
      return this.$route.params.id;
    },
    currentUserId() {
      return localStorage.getItem('uid') || z;
    },
    isOwner() {
      return this.product && this.currentUserId && this.product.userid === this.currentUserId;
    }
  },
  async mounted() {
    // Initialize Bootstrap components
    if (this.$refs.deleteModal) {
      this.deleteModal = new Modal(this.$refs.deleteModal);
    }
    
    if (this.$refs.successToast) {
      this.successToast = new Toast(this.$refs.successToast, {
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
    
    // Fetch product and related data
    await this.fetchProductDetails();
  },
  methods: {
    // Fetch product details from API
    async fetchProductDetails() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get product details
        const response = await axios.get(`${PRODUCT_API_URL}/products/${this.productId}`);
        
        if (response.data.code === 200) {
          this.product = response.data.data.product;
          
          // Fetch seller information
          if (this.product.userid) {
            await this.fetchSellerInfo(this.product.userid);
          }
          
          // Fetch similar products (same category)
          await this.fetchSimilarProducts(this.product.category);
        } else {
          this.error = response.data.message || 'Failed to load product details';
        }
      } catch (err) {
        console.error('Error fetching product details:', err);
        this.error = 'Unable to load product details. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    // Fetch seller information
    async fetchSellerInfo(userId) {
      try {
        const response = await axios.get(`${USER_API_URL}/user/${userId}`, { withCredentials: true });
        if (response.data.code === 200) {
          this.seller = response.data.data.user;
        }
      } catch (err) {
        console.error('Error fetching seller info:', err);
        // Don't set error state, just log it, as this is not critical
      }
    },
    
    // Fetch similar products
    async fetchSimilarProducts(category) {
      try {
        const response = await axios.get(`${PRODUCT_API_URL}/products/category/${category}`);
        if (response.data.code === 200) {
          // Filter out current product and limit to 3 items
          this.similarProducts = response.data.data.products
            .filter(p => p.productid !== parseInt(this.productId))
            .slice(0, 3);
        }
      } catch (err) {
        console.error('Error fetching similar products:', err);
        // Don't set error state, just log it
      }
    },
    
    // Get product image or fallback to placeholder
    getProductImage(product) {
      return product.image || `/api/placeholder/800/600`;
    },
    
    // Format price to 2 decimal places
    formatPrice(price) {
      return parseFloat(price).toFixed(2);
    },
    
    // Format date to readable string
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      
      // Check if date is valid
      if (isNaN(date.getTime())) return 'N/A';
      
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    // Get expiry status
    getExpiryStatus(expiryDate) {
      if (!expiryDate) return '';
      
      const expiry = new Date(expiryDate);
      const now = new Date();
      
      if (isNaN(expiry.getTime())) return '';
      
      if (expiry < now) {
        return 'Expired';
      }
      
      // Calculate days until expiry
      const diffTime = Math.abs(expiry - now);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays <= 1) {
        return 'Expires today';
      } else {
        return `Expires in ${diffDays} days`;
      }
    },
    
    // Navigate to another product
    navigateToProduct(productId) {
      if (productId === parseInt(this.productId)) return;
      
      this.$router.push({ path: `/product/${productId}` });
      
      // Reload page data for new product
      this.fetchProductDetails();
    },
    
    // Start chat with seller
    startChat() {
      if (!this.currentUserId) {
        // If user is not logged in, show error
        this.errorMessage = 'Please log in to chat with the seller';
        if (this.errorToast) {
          this.errorToast.show();
        }
        return;
      }
      
      if (this.seller && this.seller.uid && this.product) {
        // Navigate to the chat page with necessary parameters
        // The chat component will handle the creation of the deal and messages when the user sends a message
        this.$router.push({
          path: '/chat',
          query: {
            productId: this.product.productid,
            sellerId: this.seller.uid,
            buyerId: this.currentUserId,
            productTitle: this.product.title
          }
        });
      } else {
        this.errorMessage = 'Unable to start chat. Seller information is not available.';
        if (this.errorToast) {
          this.errorToast.show();
        }
      }
    },
    
    // View seller profile
    goToProfile() {
      if (this.seller.uid){
        this.$router.push({
          name: 'OtherProfile',
          params: { id: this.seller.uid}
        });
      }else{
        this.$router.push({name:'Profile'});
      }
    },
    
    // Copy product link to clipboard
    copyLink() {
      const url = window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        this.successMessage = 'Link copied to clipboard!';
        if (this.successToast) {
          this.successToast.show();
        }
      }).catch(err => {
        console.error('Failed to copy link:', err);
        this.errorMessage = 'Failed to copy link';
        if (this.errorToast) {
          this.errorToast.show();
        }
      });
    },
    
    // Edit product action
    editProduct() {
      // In a real app, navigate to edit page or open edit modal
      this.$router.push({ path: `/product/${this.productId}/edit` });
    },
    
    // Show delete confirmation modal
    confirmDelete() {
      if (this.deleteModal) {
        this.deleteModal.show();
      }
    },
    
    // Delete product action
    async deleteProduct() {
      try {
        const response = await axios.delete(`${PRODUCT_API_URL}/products/${this.productId}`);
        
        if (response.data.code === 200) {
          // Hide modal
          if (this.deleteModal) {
            this.deleteModal.hide();
          }
          
          // Show success message
          this.successMessage = 'Product deleted successfully';
          if (this.successToast) {
            this.successToast.show();
          }
          
          // Navigate back to home page after short delay
          setTimeout(() => {
            this.$router.push({ path: '/' });
          }, 1500);
        } else {
          this.errorMessage = response.data.message || 'Failed to delete product';
          if (this.errorToast) {
            this.errorToast.show();
          }
        }
      } catch (err) {
        console.error('Error deleting product:', err);
        this.errorMessage = err.response?.data?.message || 'Failed to delete product';
        if (this.errorToast) {
          this.errorToast.show();
        }
      }
    }
  }
};
</script>

<style scoped>
.product-details-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.navbar {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  margin-bottom: 20px;
}

.container {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  padding: 30px;
  margin: 0 auto;
}

.product-image-container {
  position: relative;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.product-image {
  width: 100%;
  height: auto;
  max-height: 500px;
  object-fit: cover;
}

.expiry-badge {
  position: absolute;
  top: 15px;
  right: 15px;
  background-color: rgba(0,0,0,0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 0.8rem;
}

.price-badge {
  font-size: 1.2rem;
  padding: 8px 15px;
}

.product-title {
  font-size: 2rem;
  font-weight: 600;
}

.description-section, .location-section, .expires-section {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
}

.description-section h5, .location-section h5, .expires-section h5 {
  font-size: 1.1rem;
  margin-bottom: 10px;
}

.share-buttons {
  margin-top: 20px;
}

.share-buttons h5 {
  margin-bottom: 10px;
}

.rating-stars {
  color: #ffc107;
  font-size: 0.9rem;
}

.similar-products {
  margin-top: 40px;
  padding: 0 15px;
}

.similar-product-image {
  height: 180px;
  object-fit: cover;
}

.product-card {
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

@media (max-width: 768px) {
  .container {
    padding: 15px;
  }
  
  .product-title {
    font-size: 1.5rem;
  }
  
  .price-badge {
    font-size: 1rem;
    padding: 5px 10px;
  }
}
</style>