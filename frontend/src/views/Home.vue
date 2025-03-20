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
          v-for="category in categories" 
          :key="category.id"
          :class="['category-item', selectedCategory === category.id ? 'active' : '']"
          @click="filterByCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
    </section>

    <!-- Featured Deals -->
    <section class="featured-deals mt-4">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h5 class="mb-0">{{ selectedCategory ? `${getCategoryName(selectedCategory)} Deals` : 'Featured Deals' }}</h5>
        <div class="dropdown">
          <button class="btn btn-outline-secondary dropdown-toggle" type="button" id="sortDropdown" data-bs-toggle="dropdown" aria-expanded="false">
            Sort By
          </button>
          <ul class="dropdown-menu" aria-labelledby="sortDropdown">
            <li><a class="dropdown-item" href="#" @click.prevent="sortDeals('newest')">Newest</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="sortDeals('popular')">Most Popular</a></li>
            <li><a class="dropdown-item" href="#" @click.prevent="sortDeals('title')">Alphabetical</a></li>
          </ul>
        </div>
      </div>
      
      <div v-if="filteredDeals.length === 0" class="alert alert-info">
        No deals found matching your criteria. Try a different search or category.
      </div>
      
      <div class="deal-list">
        <div class="deal-item" v-for="deal in filteredDeals" :key="deal.id">
          <div class="position-relative">
            <img :src="deal.image || '/api/placeholder/300/150'" alt="deal-image" class="deal-image">
            <span class="deal-badge">{{ formatTimeAgo(deal.createdAt) }}</span>
          </div>
          <div class="deal-info">
            <h6 class="deal-title">{{ deal.title }}</h6>
            <div class="d-flex justify-content-between align-items-center mb-2">
              <span class="badge rounded-pill text-bg-light">{{ getCategoryName(deal.category) }}</span>
              <small class="text-muted">{{ deal.location }}</small>
            </div>
            <p class="deal-description">{{ deal.description }}</p>
            <div class="d-flex justify-content-between align-items-center">
              <button class="btn btn-primary" @click="viewDealDetails(deal.id)">View Deal</button>
              <div>
                <i class="far fa-heart me-1"></i>
                <span>{{ deal.likes || 0 }}</span>
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
                    <label for="dealImage" class="form-label">Upload Image</label>
                    <div class="input-group">
                      <input 
                        type="file" 
                        class="form-control" 
                        id="dealImage" 
                        @change="handleImageUpload"
                        accept="image/*"
                      />
                      <button 
                        v-if="newDeal.imagePreview" 
                        class="btn btn-outline-secondary" 
                        type="button"
                        @click="clearImage"
                      >
                        Clear
                      </button>
                    </div>
                    <div class="form-text">Max file size: 5MB. Recommended size: 800x600px</div>
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
  </div>
</template>

<script>
import { Modal, Toast } from 'bootstrap'; // Import Bootstrap components

export default {
  name: 'HomePage',
  data() {
    return {
      searchQuery: "",
      selectedCategory: "",
      sortOption: "newest",
      categories: [
        { id: "electronics", name: "Electronics" },
        { id: "fashion", name: "Fashion" },
        { id: "food", name: "Food" },
        { id: "services", name: "Services" },
        { id: "books", name: "Books" },
        { id: "furniture", name: "Furniture" }
      ],
      deals: [
        { 
          id: 1, 
          title: "1-for-1 Bubble Tea", 
          category: "food", 
          description: "Looking for someone to share a bubble tea deal. Valid at all outlets until end of month.", 
          image: "/api/placeholder/300/150", 
          location: "Downtown",
          price: "5.00",
          likes: 24,
          createdAt: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
          expiresAt: new Date(Date.now() + 604800000).toISOString(), // 7 days from now
          terms: [
            "Valid only at participating outlets",
            "Cannot be combined with other promotions",
            "Valid until end of month"
          ],
          user: {
            name: "Jane Doe",
            avatar: "/api/placeholder/50/50",
            joinDate: "2023-01-15"
          }
        },
        { 
          id: 2, 
          title: "Donut Box for $15", 
          category: "food", 
          description: "Need someone to share a box of donuts. 12 pieces of assorted flavors.", 
          image: "/api/placeholder/300/150", 
          location: "North Campus",
          price: "15.00",
          likes: 18,
          createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          user: {
            name: "John Smith",
            avatar: "/api/placeholder/50/50",
            joinDate: "2022-11-20"
          }
        },
        { 
          id: 3, 
          title: "50% Off Bluetooth Earbuds", 
          category: "electronics", 
          description: "I have a coupon for 50% off wireless earbuds at TechStore. Looking to share with someone.", 
          image: "/api/placeholder/300/150", 
          location: "East Mall",
          price: "25.00",
          likes: 32,
          createdAt: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
          user: {
            name: "Mike Johnson",
            avatar: "/api/placeholder/50/50",
            joinDate: "2023-02-05"
          }
        },
        { 
          id: 4, 
          title: "Buy 2 Get 1 Free Books", 
          category: "books", 
          description: "Bookstore promotion, buy 2 books and get 1 free. Let's pool together to maximize the deal.", 
          image: "/api/placeholder/300/150", 
          location: "Central Library",
          price: "30.00",
          likes: 15,
          createdAt: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
          user: {
            name: "Sarah Williams",
            avatar: "/api/placeholder/50/50",
            joinDate: "2023-01-10"
          }
        }
      ],
      newDeal: {
        title: "",
        category: "",
        description: "",
        location: "",
        price: "",
        expiresAt: "",
        image: null,
        imagePreview: null
      },
      validationErrors: {},
      isSubmitting: false,
      modalInstance: null,
      toastInstance: null
    };
  },
  computed: {
    filteredDeals() {
      let result = [...this.deals];
      
      // Filter by category if selected
      if (this.selectedCategory) {
        result = result.filter(deal => deal.category === this.selectedCategory);
      }
      
      // Filter by search query
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(deal => 
          deal.title.toLowerCase().includes(query) || 
          deal.description.toLowerCase().includes(query)
        );
      }
      
      // Sort deals based on selected option
      switch (this.sortOption) {
        case 'newest':
          result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
          break;
        case 'popular':
          result.sort((a, b) => (b.likes || 0) - (a.likes || 0));
          break;
        case 'title':
          result.sort((a, b) => a.title.localeCompare(b.title));
          break;
      }
      
      return result;
    }
  },
  methods: {
    openModal() {
      // Reset form data and validation errors
      this.newDeal = {
        title: "",
        category: "",
        description: "",
        location: "",
        price: "",
        expiresAt: "",
        image: null,
        imagePreview: null
      };
      this.validationErrors = {};
      
      // Show the modal
      if (this.$refs.dealModal) {
        const modalElement = this.$refs.dealModal;
        const modalInstance = new Modal(modalElement);
        modalInstance.show();
        this.modalInstance = modalInstance;
      }
    },
    closeModal() {
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        alert("File is too large. Maximum size is 5MB.");
        event.target.value = ""; // Clear the input
        return;
      }
      
      // Save file reference
      this.newDeal.image = file;
      
      // Create a preview
      const reader = new FileReader();
      reader.onload = e => {
        this.newDeal.imagePreview = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    clearImage() {
      this.newDeal.image = null;
      this.newDeal.imagePreview = null;
      // Reset the file input
      const fileInput = document.getElementById('dealImage');
      if (fileInput) fileInput.value = "";
    },
    submitDeal() {
      // Reset validation errors
      this.validationErrors = {};
      
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
      
      // Simulate API call with a timeout
      setTimeout(() => {
        const newDealId = this.deals.length + 1;
        
        // Create a new deal object
        const dealToAdd = {
          id: newDealId,
          title: this.newDeal.title,
          category: this.newDeal.category,
          description: this.newDeal.description,
          location: this.newDeal.location,
          price: this.newDeal.price,
          image: this.newDeal.imagePreview || "/api/placeholder/300/150",
          createdAt: new Date().toISOString(),
          likes: 0,
          expiresAt: this.newDeal.expiresAt || null,
          user: {
            name: "Current User", // In a real app, get the logged-in user
            avatar: "/api/placeholder/50/50",
            joinDate: new Date().toISOString().split('T')[0]
          }
        };
        
        // Add the new deal to the list
        this.deals.unshift(dealToAdd);
        
        // Hide the modal
        this.closeModal();
        
        // Reset submission state
        this.isSubmitting = false;
        
        // Show success toast
        this.showSuccessToast();
        
        // Redirect to the newly created deal
        this.$router.push({ name: 'dealDetails', params: { id: newDealId.toString() } });
      }, 1500); // Simulate 1.5s processing time
    },
    showSuccessToast() {
      if (this.$refs.successToast) {
        const toastElement = this.$refs.successToast;
        const toast = new Toast(toastElement);
        toast.show();
      }
    },
    performSearch() {
      // You could implement additional search logic here if needed
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
    viewDealDetails(dealId) {
      this.$router.push({ name: 'dealDetails', params: { id: dealId.toString() } });
    },
    formatTimeAgo(dateString) {
      const date = new Date(dateString);
      const now = new Date();
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
  },
  created() {
    // Save deals to localStorage for sharing with DealDetails component
    localStorage.setItem('deals', JSON.stringify(this.deals));
  },
  watch: {
    deals: {
      handler(newDeals) {
        // Update localStorage when deals change
        localStorage.setItem('deals', JSON.stringify(newDeals));
      },
      deep: true
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
}
</style>