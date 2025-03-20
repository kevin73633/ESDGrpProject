<template>
  <div class="deal-details">
    <!-- Navigation Header -->
    <div class="navigation-bar bg-light">
      <div class="container">
        <div class="d-flex align-items-center py-3">
          <button class="btn btn-link text-dark me-3 p-0" @click="goBack" style="font-size: 1.5rem;">
            <i class="bi bi-arrow-left"></i>
          </button>
          <h5 class="mb-0">Deal Details</h5>
        </div>
      </div>
    </div>

    <div class="container mt-3 mb-5 pb-5">
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3">Loading deal details...</p>
      </div>
      
      <div v-else-if="error" class="alert alert-danger">
        <i class="fas fa-exclamation-circle me-2"></i>
        {{ error }}
      </div>
      
      <div v-else class="deal-content">
        <!-- Deal Image Gallery -->
        <div class="image-gallery mb-4">
          <img :src="deal.image || '/api/placeholder/800/400'" alt="Deal Image" class="main-image rounded">
          <div v-if="deal.additionalImages && deal.additionalImages.length" class="thumbnails mt-2">
            <div 
              v-for="(img, index) in deal.additionalImages" 
              :key="index" 
              class="thumbnail"
              @click="setMainImage(img)"
            >
              <img :src="img" :alt="`${deal.title} - Image ${index + 2}`">
            </div>
          </div>
        </div>
        
        <!-- Deal Title & Basic Info -->
        <div class="card mb-4">
          <div class="card-body">
            <h3 class="card-title">{{ deal.title }}</h3>
            <div class="d-flex justify-content-between align-items-center mb-3">
              <span class="badge rounded-pill bg-primary">{{ getCategoryName(deal.category) }}</span>
              <span class="posted-time text-muted">Posted {{ formatTimeAgo(deal.createdAt) }}</span>
            </div>
            
            <div class="location mb-3">
              <i class="fas fa-map-marker-alt me-2"></i> {{ deal.location || 'Location not specified' }}
            </div>
            
            <div class="price mb-3">
              <i class="fas fa-tag me-2"></i> ${{ deal.price || '0.00' }}
            </div>
            
            <div v-if="deal.expiresAt" class="expiration mb-3">
              <i class="far fa-clock me-2"></i> 
              <span :class="isExpiringSoon ? 'text-danger' : ''">
                {{ isExpired ? 'Expired' : `Expires ${formatExpiration(deal.expiresAt)}` }}
              </span>
            </div>
            
            <div class="deal-stats d-flex">
              <div class="me-4">
                <i class="far fa-eye me-1"></i> {{ deal.views || 0 }} views
              </div>
              <div class="me-4">
                <i class="far fa-heart me-1"></i> {{ deal.likes || 0 }} likes
              </div>
              <div>
                <i class="far fa-comment me-1"></i> {{ deal.comments?.length || 0 }} comments
              </div>
            </div>
          </div>
        </div>
        
        <!-- Deal Description -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Description</h5>
          </div>
          <div class="card-body">
            <p class="description-text">
              {{ deal.description }}
            </p>
            <hr v-if="deal.terms && deal.terms.length">
            <div v-if="deal.terms && deal.terms.length" class="terms-conditions">
              <h6>Terms & Conditions:</h6>
              <ul>
                <li v-for="(term, index) in deal.terms" :key="index">{{ term }}</li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Deal Owner Info -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Posted By</h5>
          </div>
          <div class="card-body">
            <div class="d-flex align-items-center">
              <div class="user-avatar me-3">
                <img :src="deal.user?.avatar || '/api/placeholder/50/50'" alt="User avatar" class="rounded-circle" width="50" height="50">
              </div>
              <div>
                <h6 class="mb-1">{{ deal.user?.name || 'Anonymous User' }}</h6>
                <p class="text-muted mb-0 small">Member since {{ formatDate(deal.user?.joinDate) || 'Unknown' }}</p>
              </div>
              <div class="ms-auto">
                <router-link :to="{ name: 'Chat', params: { dealId: deal.id } }" class="btn btn-primary">
                  <i class="fas fa-comments me-2"></i>Chat with Seller
                </router-link>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Related Deals -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Similar Deals</h5>
          </div>
          <div class="card-body">
            <div v-if="similarDeals.length === 0" class="text-center py-3">
              <p class="text-muted">No similar deals found</p>
            </div>
            <div v-else class="row">
              <div v-for="(similarDeal, index) in similarDeals" :key="index" class="col-md-4 mb-3">
                <div class="card h-100">
                  <img :src="similarDeal.image || '/api/placeholder/300/150'" class="card-img-top" alt="Deal image">
                  <div class="card-body">
                    <h6 class="card-title">{{ similarDeal.title }}</h6>
                    <p class="card-text small">{{ truncateText(similarDeal.description, 60) }}</p>
                    <router-link :to="{ name: 'dealDetails', params: { id: similarDeal.id } }" class="btn btn-sm btn-outline-primary">
                      View Deal
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Comments Section -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Comments ({{ deal.comments?.length || 0 }})</h5>
          </div>
          <div class="card-body">
            <div v-if="!deal.comments || deal.comments.length === 0" class="text-center py-3">
              <p class="text-muted">No comments yet. Be the first to comment!</p>
            </div>
            <div v-else>
              <div v-for="(comment, index) in deal.comments" :key="index" class="comment-item mb-3">
                <div class="d-flex">
                  <div class="me-3">
                    <img :src="comment.user.avatar || '/api/placeholder/40/40'" alt="User avatar" class="rounded-circle" width="40" height="40">
                  </div>
                  <div class="flex-grow-1">
                    <div class="d-flex justify-content-between align-items-center">
                      <h6 class="mb-0">{{ comment.user.name }}</h6>
                      <small class="text-muted">{{ formatTimeAgo(comment.createdAt) }}</small>
                    </div>
                    <p class="comment-text mb-0">{{ comment.text }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Comment Form -->
            <div class="comment-form mt-4">
              <h6>Add a Comment</h6>
              <form @submit.prevent="addComment">
                <div class="mb-3">
                  <textarea 
                    v-model="newComment" 
                    class="form-control" 
                    rows="3" 
                    placeholder="Write your comment here..."
                    required
                  ></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Post Comment</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DealDetails',
  props: ['id'],
  data() {
    return {
      deal: null,
      loading: true,
      error: null,
      isLiked: false,
      newComment: '',
      mainImage: null,
      categories: [
        { id: "electronics", name: "Electronics" },
        { id: "fashion", name: "Fashion" },
        { id: "food", name: "Food" },
        { id: "services", name: "Services" },
        { id: "books", name: "Books" },
        { id: "furniture", name: "Furniture" }
      ],
      similarDeals: []
    };
  },
  computed: {
    isExpired() {
      if (!this.deal?.expiresAt) return false;
      return new Date(this.deal.expiresAt) < new Date();
    },
    isExpiringSoon() {
      if (!this.deal?.expiresAt) return false;
      const expirationDate = new Date(this.deal.expiresAt);
      const now = new Date();
      const diffInDays = Math.floor((expirationDate - now) / (1000 * 60 * 60 * 24));
      return diffInDays <= 3 && diffInDays >= 0;
    }
  },
  methods: {
    goBack() {
      // Try to use browser back if possible
      if (window.history.length > 1) {
        this.$router.go(-1);
      } else {
        // Fallback to home route if there's no history
        this.$router.push({ name: 'home' });
      }
    },
    shareDeal() {
      // In a real app, implement share functionality
      // Could use navigator.share() for mobile devices
      alert(`Sharing deal: ${this.deal.title}`);
    },
    toggleLike() {
      this.isLiked = !this.isLiked;
      if (this.isLiked) {
        this.deal.likes = (this.deal.likes || 0) + 1;
      } else {
        this.deal.likes = Math.max(0, (this.deal.likes || 0) - 1);
      }
      
      // Update the deal in localStorage
      this.updateDealInStorage();
      
      // In a real app, make an API call to update likes
      console.log(`Deal ${this.isLiked ? 'liked' : 'unliked'}: ${this.deal.id}`);
    },
    addComment() {
      if (!this.newComment.trim()) return;
      
      // Initialize comments array if it doesn't exist
      if (!this.deal.comments) {
        this.deal.comments = [];
      }
      
      const comment = {
        id: Date.now(),
        text: this.newComment,
        createdAt: new Date().toISOString(),
        user: {
          name: 'You', // In a real app, get the logged-in user
          avatar: '/api/placeholder/40/40'
        }
      };
      
      this.deal.comments.push(comment);
      this.newComment = '';
      
      // Update the deal in localStorage
      this.updateDealInStorage();
      
      // In a real app, make an API call to save the comment
      console.log('Comment added:', comment);
    },
    setMainImage(imageUrl) {
      this.mainImage = imageUrl;
      this.deal.image = imageUrl;
    },
    formatTimeAgo(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffSec = Math.floor(diffMs / 1000);
      const diffMin = Math.floor(diffSec / 60);
      const diffHour = Math.floor(diffMin / 60);
      const diffDay = Math.floor(diffHour / 24);
      
      if (diffDay > 30) {
        return this.formatDate(dateString);
      }
      if (diffDay > 0) {
        return diffDay === 1 ? '1 day ago' : `${diffDay} days ago`;
      }
      if (diffHour > 0) {
        return diffHour === 1 ? '1 hour ago' : `${diffHour} hours ago`;
      }
      if (diffMin > 0) {
        return diffMin === 1 ? '1 minute ago' : `${diffMin} minutes ago`;
      }
      return 'Just now';
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },
    formatExpiration(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      const now = new Date();
      const diffInDays = Math.floor((date - now) / (1000 * 60 * 60 * 24));
      
      if (diffInDays < 0) {
        return 'Expired';
      }
      if (diffInDays === 0) {
        return 'Today';
      }
      if (diffInDays === 1) {
        return 'Tomorrow';
      }
      if (diffInDays < 7) {
        return `in ${diffInDays} days`;
      }
      return this.formatDate(dateString);
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId);
      return category ? category.name : categoryId;
    },
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substr(0, maxLength) + '...';
    },
    fetchDealDetails() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get deals from localStorage (shared with Home component)
        const dealsJSON = localStorage.getItem('deals');
        const deals = dealsJSON ? JSON.parse(dealsJSON) : [];
        
        // Find the requested deal
        const dealId = parseInt(this.id);
        const deal = deals.find(d => d.id === dealId);
        
        if (deal) {
          this.deal = deal;
          
          // Increment view count
          this.deal.views = (this.deal.views || 0) + 1;
          this.updateDealInStorage();
          
          // Find similar deals (same category, excluding this one)
          this.similarDeals = deals
            .filter(d => d.category === deal.category && d.id !== dealId)
            .slice(0, 3);
        } else {
          this.error = "Deal not found";
        }
      } catch (err) {
        console.error('Error fetching deal details:', err);
        this.error = "Error loading deal details";
      } finally {
        this.loading = false;
      }
    },
    updateDealInStorage() {
      // Get all deals from localStorage
      const dealsJSON = localStorage.getItem('deals');
      let deals = dealsJSON ? JSON.parse(dealsJSON) : [];
      
      // Update the current deal in the array
      const index = deals.findIndex(d => d.id === parseInt(this.id));
      if (index !== -1) {
        deals[index] = this.deal;
        // Save back to localStorage
        localStorage.setItem('deals', JSON.stringify(deals));
      }
    }
  },
  created() {
    this.fetchDealDetails();
  }
};
</script>

<style scoped>
.deal-details {
  padding-bottom: 60px;
}

.navigation-bar {
  position: sticky;
  top: 0;
  z-index: 1000;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.main-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border: 1px solid #eee;
}

.thumbnails {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.thumbnail {
  width: 80px;
  height: 80px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail:hover {
  border-color: #007bff;
}

.card {
  border-radius: 8px;
  border: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.card-header {
  background-color: rgba(0,0,0,0.02);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.description-text {
  white-space: pre-line;
  line-height: 1.6;
}

.comment-item {
  padding: 15px;
  border-radius: 8px;
  background-color: #f8f9fa;
}

.comment-text {
  margin-top: 5px;
  white-space: pre-line;
}

.user-avatar img {
  border: 1px solid #eee;
}

@media (max-width: 768px) {
  .similar-deals {
    grid-template-columns: 1fr;
  }
}
</style>