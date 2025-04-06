<template>
  <div class="home">
    <!-- Navbar (Top) -->
    <nav class="navbar navbar-light bg-light">
      <div class="container-fluid">
        <a class="navbar-brand" href="#">DealShare</a>
        <div class="d-flex">
          <input v-model="searchQuery" type="search" class="form-control me-2" placeholder="Search for deals..." aria-label="Search">
          <button @click="performSearch" class="btn btn-outline-success">Search</button>
        </div>
      </div>
    </nav>
    
    <!-- Categories Section -->
    <section class="categories">
      <h5 class="mt-3">Categories</h5>
      <div class="category-list">
        <button 
          class="category-item"
          :class="{ 'active': selectedCategory === '' }"
          @click="filterByCategory('')"
        >
          All
        </button>
        <button 
          v-for="category in categories" 
          :key="category.id"
          :class="['category-item', selectedCategory === category.id ? 'active' : '']"
          @click="filterByCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
    </section>

    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading products...</p>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="alert alert-danger my-3" role="alert">
      <i class="fas fa-exclamation-circle me-2"></i>
      {{ error }}
    </div>

    <!-- Featured Deals -->
    <section v-else class="featured-deals mt-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0">{{ selectedCategory ? `${getCategoryName(selectedCategory)} Deals` : 'Featured Deals' }}</h5>
        <div class="dropdown custom-dropdown">
          <button class="btn btn-outline-secondary" type="button" @click="toggleSortDropdown">
            Sort By: {{ getSortOptionLabel() }}
            <i class="fas fa-chevron-down ms-1"></i>
          </button>
          <div class="dropdown-menu" :class="{ 'show': sortDropdownOpen }">
            <a class="dropdown-item" href="#" @click.prevent="sortDeals('newest'); toggleSortDropdown()">Newest</a>
            <a class="dropdown-item" href="#" @click.prevent="sortDeals('price-low'); toggleSortDropdown()">Price: Low to High</a>
            <a class="dropdown-item" href="#" @click.prevent="sortDeals('price-high'); toggleSortDropdown()">Price: High to Low</a>
            <a class="dropdown-item" href="#" @click.prevent="sortDeals('title'); toggleSortDropdown()">Alphabetical</a>
          </div>
        </div>
      </div>
      
      <div v-if="filteredProducts.length === 0" class="alert alert-info">
        No deals found matching your criteria. Try a different search or category.
      </div>
      
      <div class="deal-list">
        <div class="deal-item" v-for="product in filteredProducts" :key="product.productid">
          <div class="position-relative">
            <img :src="getProductImage(product)" alt="deal-image" class="deal-image">
            <span class="deal-badge">{{ formatTimeAgo(product.created_at) }}</span>
          </div>
          <div class="deal-info">
            <h6 class="deal-title">{{ product.title }}</h6>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="badge rounded-pill text-bg-light">{{ product.category }}</span>
              <small class="text-muted">{{ product.location }}</small>
            </div>
            <p class="deal-description">{{ product.description }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <button class="btn btn-primary" @click="viewProductDetails(product.productid)">View Deal</button>
              <div class="price-display">
                <strong>${{ formatPrice(product.price) }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Post Deal Button (Floating) -->
    <button class="btn btn-primary post-deal-btn" @click="openModal">
      <i class="fas fa-plus-circle me-2"></i>Post a Deal
    </button>

    <!-- Modal for Posting a Deal -->
    <div class="modal fade" id="dealModal" tabindex="-1" aria-labelledby="dealModalLabel" aria-hidden="true" ref="dealModal">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="dealModalLabel">Post a New Deal</h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitDeal">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="dealTitle" class="form-label">Deal Title*</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="newDeal.title" 
                      id="dealTitle" 
                      :class="{ 'is-invalid': validationErrors.title }"
                      placeholder="Enter a clear, descriptive title"
                      required 
                    />
                    <div class="invalid-feedback" v-if="validationErrors.title">
                      {{ validationErrors.title }}
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label for="dealCategory" class="form-label">Category*</label>
                    <select 
                      class="form-select" 
                      v-model="newDeal.category" 
                      id="dealCategory" 
                      :class="{ 'is-invalid': validationErrors.category }"
                      required
                    >
                      <option value="">Select a category</option>
                      <option v-for="category in categories" :key="category.id" :value="category.id">
                        {{ category.name }}
                      </option>
                    </select>
                    <div class="invalid-feedback" v-if="validationErrors.category">
                      {{ validationErrors.category }}
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label for="dealLocation" class="form-label">Location*</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      v-model="newDeal.location" 
                      id="dealLocation" 
                      :class="{ 'is-invalid': validationErrors.location }"
                      placeholder="Where is this deal available?"
                      required 
                    />
                    <div class="invalid-feedback" v-if="validationErrors.location">
                      {{ validationErrors.location }}
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label for="dealPrice" class="form-label">Price*</label>
                    <div class="input-group">
                      <span class="input-group-text">$</span>
                      <input 
                        type="number" 
                        step="0.01" 
                        min="0" 
                        class="form-control" 
                        v-model="newDeal.price" 
                        id="dealPrice" 
                        :class="{ 'is-invalid': validationErrors.price }"
                        placeholder="Enter price"
                        required 
                      />
                      <div class="invalid-feedback" v-if="validationErrors.price">
                        {{ validationErrors.price }}
                      </div>
                    </div>
                  </div>
                  
                  <div class="mb-3">
                    <label for="dealExpires" class="form-label">Expires On</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      v-model="newDeal.expiresAt" 
                      id="dealExpires" 
                      min="2025-03-21"
                    />
                    <small class="form-text text-muted">Leave blank if there's no expiration</small>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="dealDescription" class="form-label">Description*</label>
                    <textarea 
                      class="form-control" 
                      v-model="newDeal.description" 
                      id="dealDescription" 
                      :class="{ 'is-invalid': validationErrors.description }"
                      rows="4" 
                      placeholder="Provide details about the deal, terms, and conditions"
                      required
                    ></textarea>
                    <div class="invalid-feedback" v-if="validationErrors.description">
                      {{ validationErrors.description }}
                    </div>
                    <small class="form-text text-muted">{{ 500 - (newDeal.description?.length || 0) }} characters remaining</small>
                  </div>
                  
                  <div class="mb-3">
                    <label for="dealImage" class="form-label">Image URL</label>
                    <input 
                      type="url" 
                      class="form-control" 
                      id="dealImage" 
                      v-model="newDeal.image_url"
                      @input="handleImageUpload"
                      placeholder="Enter image URL"
                    />
                    <div class="form-text">Paste a direct link to an image</div>
                  </div>

                  <div v-if="newDeal.imagePreview" class="mb-3 image-preview-container">
                    <img :src="newDeal.imagePreview" alt="Deal preview" class="img-preview">
                  </div>
                
                </div>
              </div>
              
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="isSubmitting"
                >
                  <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  {{ isSubmitting ? 'Posting...' : 'Post Deal' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Success Alert -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 5">
      <div 
        class="toast align-items-center text-white bg-success border-0" 
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
        ref="successToast"
      >
        <div class="d-flex">
          <div class="toast-body">
            <i class="fas fa-check-circle me-2"></i>
            Your deal has been posted successfully!
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    </div>

    <!-- Error Alert -->
    <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 5">
      <div 
        class="toast align-items-center text-white bg-danger border-0" 
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
        ref="errorToast"
      >
        <div class="d-flex">
          <div class="toast-body">
            <i class="fas fa-exclamation-circle me-2"></i>
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
import { Modal, Toast } from 'bootstrap'; // Import Bootstrap components

// Define API URL
const PRODUCT_API_URL = 'http://localhost:8000'; // Using your product.py API port
const DEAL_API_URL = 'http://localhost:8000'; // Using your product.py API port

export default {
  name: 'HomePage',
  data() {
    return {
      searchQuery: "",
      selectedCategory: "",
      sortOption: "newest",
      loading: true,
      error: null,
      products: [],
      errorMessage: "An error occurred. Please try again.",
      categories: [
        { id: "electronics", name: "Electronics" },
        { id: "fashion", name: "Fashion" },
        { id: "food", name: "Food" },
        { id: "services", name: "Services" },
        { id: "books", name: "Books" },
        { id: "furniture", name: "Furniture" }
      ],
      newDeal: {
        title: "",
        category: "",
        description: "",
        location: "",
        price: "",
        expiresAt: "",
        image_url: "",
        imagePreview: null
      },
      validationErrors: {},
      isSubmitting: false,
      modalInstance: null,
      successToast: null,
      errorToast: null,
      sortDropdownOpen: false,
    };
  },
  computed: {
    filteredProducts() {
      let result = [...this.products];
      
      // Filter by category if selected
      if (this.selectedCategory) {
        result = result.filter(product => 
          product.category.toLowerCase() === this.selectedCategory.toLowerCase()
        );
      }
      
      // Filter by search query
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(product => 
          product.title.toLowerCase().includes(query) || 
          product.description.toLowerCase().includes(query) ||
          product.location.toLowerCase().includes(query)
        );
      }
      
      // Sort products based on selected option
      switch (this.sortOption) {
        case 'newest':
          result.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
          break;
        case 'price-low':
          result.sort((a, b) => a.price - b.price);
          break;
        case 'price-high':
          result.sort((a, b) => b.price - a.price);
          break;
        case 'title':
          result.sort((a, b) => a.title.localeCompare(b.title));
          break;
      }
      
      return result;
    },
    currentUserId() {
      // Get user ID from localStorage or session
      return localStorage.getItem('uid') || '';
    }
  },
  mounted() {
    // Initialize Bootstrap components
    if (this.$refs.dealModal) {
      this.modalInstance = new Modal(this.$refs.dealModal);
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
    
    document.addEventListener('click', (e) => {
    const dropdownElement = document.querySelector('.custom-dropdown');
    if (dropdownElement && !dropdownElement.contains(e.target)) {
      this.sortDropdownOpen = false;
    }
  });
  
    // Fetch products when component mounts
    this.fetchProducts();
  },
  methods: {

    toggleSortDropdown() {
      this.sortDropdownOpen = !this.sortDropdownOpen;
    },

    getSortOptionLabel() {
      switch (this.sortOption) {
        case 'newest':
          return 'Newest';
        case 'price-low':
          return 'Price: Low to High';
        case 'price-high':
          return 'Price: High to Low';
        case 'title':
          return 'Alphabetical';
        default:
          return 'Newest';
      }
    },

    // Fetch products from API
    async fetchProducts() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`${PRODUCT_API_URL}/products`);
        
        if (response.data.code === 200) {
          this.products = response.data.data.products;
          // Extract unique categories from the products
          const uniqueCategories = [...new Set(this.products.map(product => product.category))];
          
          // Update categories array if we have categories from the API
          if (uniqueCategories.length > 0) {
            this.categories = uniqueCategories.map(category => ({
              id: category.toLowerCase(),
              name: category
            }));
          }
        } else {
          this.error = response.data.message || 'Failed to load products';
        }
      } catch (err) {
        console.error('Error fetching products:', err);
        this.error = 'Unable to load products. Please try again later.';
      } finally {
        this.loading = false;
      }
    },
    
    // Get product image or fallback to placeholder
    getProductImage(product) {
      // Check if product has an image property
      // If not, return a placeholder
      const placeholderUrl = '/default-placeholder.jpg';
  
      // Validate and return image URL
      return product.image_url && product.image_url.trim() 
        ? product.image_url 
        : placeholderUrl;
    },
    
    // Format price to 2 decimal places
    formatPrice(price) {
      return parseFloat(price).toFixed(2);
    },
    
    openModal() {
      // Check if user is logged in first
      if (!this.currentUserId) {
        // Redirect to login page or show login modal
        this.errorMessage = "Please log in to post a deal";
        if (this.errorToast) {
          this.errorToast.show();
        }
        return;
      }
      
      // Reset form data and validation errors
      this.newDeal = {
        title: "",
        category: "",
        description: "",
        location: "",
        price: "",
        expiresAt: "",
        image_url: null,
        imagePreview: null
      };
      this.validationErrors = {};
      
      // Show the modal
      if (this.modalInstance) {
        this.modalInstance.show();
      }
    },
    closeModal() {
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    },
    handleImageUpload(event) {
      const imageUrl = event.target.value;
      
      // Validate URL
      if (this.isValidUrl(imageUrl)) {
        this.newDeal.image_url = imageUrl;
        this.newDeal.imagePreview = imageUrl;
      } else {
        this.newDeal.image_url = "";
        this.newDeal.imagePreview = null;
        alert("Please enter a valid image URL");
      }
    },

    // Add URL validation method
    isValidUrl(url) {
      try {
        new URL(url);
        return true;
      } catch {
        return false;
      }
    },

    clearImage() {
      this.newDeal.image_url = "";
      this.newDeal.imagePreview = null;
      // Reset the URL input
      const urlInput = document.getElementById('dealImage');
      if (urlInput) urlInput.value = "";
    },
    async submitDeal() {
      // Reset validation errors
      this.validationErrors = {};
      
      // Check if user is logged in
      if (!this.currentUserId) {
        this.errorMessage = "Please log in to post a deal";
        if (this.errorToast) {
          this.errorToast.show();
        }
        return;
      }

      if (this.newDeal.image_url && !this.isValidUrl(this.newDeal.image_url)) {
        this.validationErrors.image_url = "Please enter a valid image URL";
        isValid = false;
      }
      
      // Validate form data
      let isValid = true;
      
      if (!this.newDeal.title.trim()) {
        this.validationErrors.title = "Title is required";
        isValid = false;
      } else if (this.newDeal.title.length < 5) {
        this.validationErrors.title = "Title must be at least 5 characters";
        isValid = false;
      }
      
      if (!this.newDeal.category) {
        this.validationErrors.category = "Please select a category";
        isValid = false;
      }
      
      if (!this.newDeal.description.trim()) {
        this.validationErrors.description = "Description is required";
        isValid = false;
      } else if (this.newDeal.description.length < 20) {
        this.validationErrors.description = "Description must be at least 20 characters";
        isValid = false;
      } else if (this.newDeal.description.length > 500) {
        this.validationErrors.description = "Description cannot exceed 500 characters";
        isValid = false;
      }
      
      if (!this.newDeal.location.trim()) {
        this.validationErrors.location = "Location is required";
        isValid = false;
      }
      
      if (!this.newDeal.price || isNaN(parseFloat(this.newDeal.price))) {
        this.validationErrors.price = "Valid price is required";
        isValid = false;
      }
      
      if (!isValid) return;
      
      // Show loading state
      this.isSubmitting = true;
      
      try {
        // Prepare data for API
        const productData = {
          title: this.newDeal.title,
          category: this.getCategoryName(this.newDeal.category), // Convert ID to name
          description: this.newDeal.description,
          location: this.newDeal.location,
          price: parseFloat(this.newDeal.price),
          userid: this.currentUserId,
          expires_at: this.newDeal.expiresAt || null,
          image_url: this.newDeal.image_url || '' 
        };
        
        // POST to API
        const response = await axios.post(`${PRODUCT_API_URL}/products`, productData);
        
        if (response.data.code === 201) {
          // Product created successfully
          
          // Get the new product from response
          const newProduct = response.data.data;
          
          // Add to products list and refresh view
          this.products.unshift(newProduct);
          
          // Hide the modal
          this.closeModal();
          
          // Show success toast
          if (this.successToast) {
            this.successToast.show();
          }
          
          // Optionally redirect to the product details
          // this.$router.push({ name: 'productDetails', params: { id: newProduct.productid.toString() } });
        } else {
          // Show error for unexpected success response
          this.errorMessage = response.data.message || 'Failed to create product';
          if (this.errorToast) {
            this.errorToast.show();
          }
        }
      } catch (err) {
        console.error('Error creating product:', err);
        this.errorMessage = err.response?.data?.message || 'Failed to create product';
        if (this.errorToast) {
          this.errorToast.show();
        }
      } finally {
        this.isSubmitting = false;
      }
    },
    performSearch() {
      // Just use the reactive filtering in the computed property
      console.log(`Searching for: ${this.searchQuery}`);
    },
    filterByCategory(categoryId) {
      if (this.selectedCategory === categoryId) {
        // If clicking the same category again, clear the filter
        this.selectedCategory = "";
      } else {
        this.selectedCategory = categoryId;
      }
    },
    sortDeals(option) {
      this.sortOption = option;
    },
    viewProductDetails(productId) {
      // Navigate to product details page
      this.$router.push({ path: `/product/${productId}` });
    },
    formatTimeAgo(dateString) {
      if (!dateString) return 'N/A';
      
      const date = new Date(dateString);
      const now = new Date();
      
      // Check if date is valid
      if (isNaN(date.getTime())) return 'N/A';
      
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);
      
      if (diffDay > 0) {
        return diffDay === 1 ? "1d ago" : `${diffDay}d ago`;
      }
      if (diffHour > 0) {
        return diffHour === 1 ? "1h ago" : `${diffHour}h ago`;
      }
      if (diffMin > 0) {
        return diffMin === 1 ? "1m ago" : `${diffMin}m ago`;
      }
      return "Just now";
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId);
      return category ? category.name : categoryId;
    }
  }
};
</script>

<style scoped>
.home {
  padding: 10px;
}

.navbar {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.categories {
  padding: 10px;
}

.category-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding-bottom: 10px;
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.category-list::-webkit-scrollbar {
  display: none;
}

.category-item {
  padding: 8px 16px;
  background-color: #f7f7f7;
  border: 1px solid #ddd;
  border-radius: 20px;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.category-item:hover {
  background-color: #e9e9e9;
}

.category-item.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
}

.featured-deals {
  padding: 10px;
}

.deal-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.deal-item {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  background-color: white;
}

.deal-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}

.deal-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.deal-info {
  padding: 15px;
}

.deal-title {
  margin-bottom: 8px;
  height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.deal-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 15px;
  height: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.deal-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(0,0,0,0.6);
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
}

.post-deal-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 10;
  border-radius: 30px;
  padding: 10px 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

.img-preview {
  max-width: 100%;
  max-height: 200px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.image-preview-container {
  display: flex;
  justify-content: center;
}

.price-display {
  background-color: #f8f9fa;
  padding: 5px 10px;
  border-radius: 5px;
  color: #212529;
}

@media (max-width: 768px) {
  .deal-list {
    grid-template-columns: 1fr;
  }
  
  .deal-item {
    display: flex;
    flex-direction: row;
  }
  
  .deal-item > div:first-child {
    width: 120px;
    min-width: 120px;
  }
  
  .deal-image {
    height: 100%;
  }
  
  .category-item {
    padding: 6px 12px;
    font-size: 0.9rem;
  }

  
  .custom-dropdown {
    position: relative;
  }

  .custom-dropdown .dropdown-menu {
    position: absolute;
    right: 0;
    top: 100%;
    z-index: 1000;
    display: none;
    min-width: 10rem;
    padding: 0.5rem 0;
    margin: 0.125rem 0 0;
    font-size: 1rem;
    color: #212529;
    text-align: left;
    list-style: none;
    background-color: #fff;
    background-clip: padding-box;
    border: 1px solid rgba(0,0,0,.15);
    border-radius: 0.25rem;
  }

  .custom-dropdown .dropdown-menu.show {
    display: block;
  }

  .custom-dropdown .dropdown-item {
    display: block;
    width: 100%;
    padding: 0.25rem 1.5rem;
    clear: both;
    font-weight: 400;
    color: #212529;
    text-align: inherit;
    white-space: nowrap;
    background-color: transparent;
    border: 0;
  }

  .custom-dropdown .dropdown-item:hover, .custom-dropdown .dropdown-item:focus {
    color: #16181b;
    text-decoration: none;
    background-color: #f8f9fa;
  }
}
</style>